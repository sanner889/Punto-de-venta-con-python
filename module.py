import tkinter
from tkinter import ttk
from datetime import datetime
import os
import json
import sqlite3
import pandas as pd
import locale
import hashlib


locale.setlocale(locale.LC_TIME, "es_ES")

# ─────────────────────────────────────────────────────────────────────────────
# RUTAS CENTRALES
# ─────────────────────────────────────────────────────────────────────────────


_DIR = os.path.dirname(os.path.abspath(__file__))

RUTA_JSON        = os.path.join(_DIR, "Registro_Ventas.json")
RUTA_DB          = os.path.join(_DIR, "Registro_Ventas.db")
RUTA_PRODUCTOS   = os.path.join(_DIR, "productos.json")
RUTA_ADMIN       = os.path.join(_DIR,"admin.json")


# ─────────────────────────────────────────────────────────────────────────────
# BASE DE DATOS — INICIALIZACIÓN
# ─────────────────────────────────────────────────────────────────────────────
# Se crea la base de datos SQLite con dos tablas normalizadas la primera vez
# que se importa el módulo.  Si las tablas ya existen, CREATE TABLE IF NOT
# EXISTS no hace nada → operación idempotente y segura.

def _init_db():
    con = sqlite3.connect(RUTA_DB)
    con.execute("PRAGMA journal_mode=WAL")

    con.executescript("""
        CREATE TABLE IF NOT EXISTS ventas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Total TEXT NOT NULL,
            pagado INTEGER NOT NULL,
            devueltas INTEGER NOT NULL,
            fecha TEXT NOT NULL
        );
    
        CREATE TABLE IF NOT EXISTS venta_productos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTENGER NOT NULL REFERENCES venta(id) ON DELETE CASCADE,
            producto TEXT NOT NULL,
            cantidad TEXT NOT NULL
        );
    """)
    con.commit()
    con.close()

_init_db()   # se ejecuta al importar el módulo


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE FORMATO
# ─────────────────────────────────────────────────────────────────────────────

def puntos_de_mil(numero):
    try:
        numero = int(numero)
        return f"$ {numero:,}".replace(",", ".")
    except Exception:
        return "$ 0"


def calcular_total(precio_unitario, cantidad_de_productos, label_total):
    if not precio_unitario:
        return
    numero_de_productos = cantidad_de_productos.get()
    if numero_de_productos.isdigit():
        numero_de_productos = int(numero_de_productos)
        total = str(precio_unitario * numero_de_productos)
        label_total["text"] = puntos_de_mil(total)

def solo_numeros(texto):
    return texto.isdigit() or texto == ""


# ─────────────────────────────────────────────────────────────────────────────
# ACTUALIZAR TOTAL
# ─────────────────────────────────────────────────────────────────────────────

def actualizar_total_general(filas, label_text):
    total = 0
    for fila in filas:
        texto = fila["total"]["text"]
        numero = texto.replace("$ ", "").replace(".", "")
        if numero:
            try:
                total += int(numero)
            except Exception:
                pass
    label_text["text"] = puntos_de_mil(str(total))


# ─────────────────────────────────────────────────────────────────────────────
# ELIMINAR FILA / TODOS LOS DATOS
# ─────────────────────────────────────────────────────────────────────────────

def eliminar_fila(fila, filas, label_text, devueltas_total_de_todo, ingresado, precio_total_de_todo):
    for widget in fila.values():
        if isinstance(widget, ttk.Combobox):
            widget.set("")
            continue
        elif isinstance(widget, tkinter.Label):
            widget["text"] = "$ 0"
    ingresado.delete(0, tkinter.END)
    devueltas_total_de_todo["text"] = "$ 0"
    actualizar_total_general(filas, label_text)
    obtener_devueltas(precio_total_de_todo, ingresado, devueltas_total_de_todo)


def eliminar_datos_todo(filas, label_text, devueltas_total_de_todo, ingresado, precio_total_de_todo):
    for fila in filas:
        eliminar_fila(fila, filas, label_text, devueltas_total_de_todo, ingresado, precio_total_de_todo)


def obtener_devueltas(precio_total_de_todo, ingresado, devueltas_total_de_todo):
    try:
        precio_total = precio_total_de_todo["text"].replace("$ ", "").replace(".", "")
        precio_total = int(precio_total)
    except Exception:
        return

    if ingresado.get().isdigit():
        pago = int(ingresado.get())
    else:
        return

    try:
        devueltas = pago - precio_total
    except Exception:
        return

    if devueltas < 0:
        devueltas_total_de_todo["text"] = "Pago insuficiente"
    else:
        devueltas_total_de_todo["text"] = puntos_de_mil(devueltas)


# ─────────────────────────────────────────────────────────────────────────────
# GUARDAR VENTA  
# ─────────────────────────────────────────────────────────────────────────────


def guardar_venta(label_total, filas, mensaje_exito, devueltas_total_de_todo, ingresado, precio_total_de_todo):
    mensaje_exito["text"] = ""
    mensaje_exito["foreground"] = "#DC2626"


    productos = cargar_productos()
    nombres = [p["producto"].lower() for p in productos]

    # ── Cargar historial JSON ─────────────────────────────────────────────────
    try:
        with open(RUTA_JSON, "r", encoding="utf-8") as f:
            ventas_json = json.load(f)
    except Exception:
        ventas_json = []

    # ── Fecha ─────────────────────────────────────────────────────────────────
    now = datetime.now()
    tiempo = now.strftime("%a %d %B %Y, %I:%M:%S %p")

    # ── Validar pago del cliente ──────────────────────────────────────────────
    if ingresado.get().isdigit():
        pago = int(ingresado.get())
    elif ingresado.get() == "":
        mensaje_exito["text"] = "⚠️ Ingrese la cantidad con la que pagó el cliente"
        return
    else:
        mensaje_exito["text"] = "⚠️ Pago del cliente inválido"
        return

    # ── Validar devueltas ─────────────────────────────────────────────────────
    devueltas = devueltas_total_de_todo["text"].replace("$ ", "").replace(".", "")
    if not devueltas.isdigit():
        mensaje_exito["text"] = "⚠️ Pago insuficiente"
        return

    # ── Construir lista de productos de la venta ──────────────────────────────
    productos_lista = []
    for fila in filas:
        producto = fila["producto"].get()
        cantidad = fila["cantidad"].get()

        if producto.lower() not in nombres and producto.strip() != "":
            mensaje_exito["text"] = f'⚠️ El producto: "{producto}" no fue encontrado o no existe'
            return

        if producto and cantidad.isdigit():
            productos_lista.append({
                "producto": producto,
                "cantidad": int(cantidad)
            })

    if not productos_lista:
        mensaje_exito["text"] = "⚠️ Agrega al menos un producto con cantidad válida"
        return

    # ── Verificar y descontar stock ───────────────────────────────────────────
    for i in productos_lista:
        for p in productos:
            if i["producto"] == p["producto"]:
                if (p["stock"] - i["cantidad"]) < 0:
                    mensaje_exito["text"] = f"Stock insuficiente de {i['producto']}"
                    return
                else:
                    p["stock"] -= i["cantidad"]
    actualizar_productos(productos)

    # ─────────────────────────────────────────────────────────────────────────
    # PASO 1 — Guardar en SQLite (fuente de verdad)
    # Si este paso falla, no se toca nada más → integridad garantizada.
    # ─────────────────────────────────────────────────────────────────────────
    try:
        con = sqlite3.connect(RUTA_DB)
        con.execute("PRAGMA journal_mode=WAL")
        cur = con.cursor()

        cur.execute(
            "INSERT INTO ventas (Total,pagado,devueltas,fecha) VALUES(?,?,?,?)",
            (label_total["text"],pago,int(devueltas),tiempo)
        )
        venta_id_db = cur.lastrowid
        cur.executemany(
            "INSERT INTO venta_productos (venta_id,producto,cantidad) VALUES (?,?,?)",
            [(venta_id_db, p["producto"], p["cantidad"]) for p in productos_lista]
        )

        con.commit()
    except Exception as e:
        con.rollback()
        mensaje_exito["text"] = f"❌ Error crítico al guardar venta: {e}"
        return
    finally:
        con.close()

    # ─────────────────────────────────────────────────────────────────────────
    # PASO 2 — Actualizar JSON (compatibilidad con el resto del sistema)
    # ─────────────────────────────────────────────────────────────────────────
    venta_json = {
        "id": len(ventas_json) + 1,
        "producto": productos_lista,
        "Total": label_total["text"],
        "pagado": pago,
        "devueltas": devueltas,
        "fecha": tiempo
    }
    ventas_json.append(venta_json)

    eliminar_datos_todo(filas, label_total, devueltas_total_de_todo, ingresado, precio_total_de_todo)
    mensaje_exito["text"] = "✅ Venta guardada exitosamente!"
    mensaje_exito["foreground"] = "#1EDB63"

    try:
        with open(RUTA_JSON, "w", encoding="utf-8") as f:
            json.dump(ventas_json, f, indent=4, ensure_ascii=False)
    except Exception as e:
        # El JSON falló, pero SQLite ya tiene la venta → no es crítico
        mensaje_exito["text"] += f"  ⚠️ (aviso: JSON no actualizado: {e})"



# ─────────────────────────────────────────────────────────────────────────────
# EXPORTAR EXCEL
# ─────────────────────────────────────────────────────────────────────────────

def exportar_excel(msg_error):
    try:
        with open(RUTA_JSON, "r", encoding="utf-8") as f:
            ventas_json = json.load(f)
    except Exception:
        ventas_json = []

    lista_excel = []
    
    try:
        if ventas_json:
            for items in ventas_json:
                for producto in items["producto"]:
                    lista_excel.append({
                        "ID":items["id"],
                        "PRODUCTO":producto["producto"],
                        "CANTIDAD":producto["cantidad"],
                        "TOTAL":items["Total"],
                        "PAGADO":items["pagado"],
                        "DEVUELTAS":items["devueltas"],
                        "FECHA":items["fecha"]
                    })

            df = pd.DataFrame(lista_excel)
            df.to_excel("Registro_de_ventas.xlsx",index=False)
            msg_error["text"] = "Exportado correctamente!"
            msg_error["font"] = ("Arial",15)
            return
        else:
            msg_error["text"] = "Error al exportar, no hay ventas registradas"
            msg_error["font"] = ("Arial",15)
    except Exception:
        return


# ─────────────────────────────────────────────────────────────────────────────
# CARGAR / ACTUALIZAR PRODUCTOS
# ─────────────────────────────────────────────────────────────────────────────

def cargar_productos():
    try:
        with open(RUTA_PRODUCTOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def actualizar_productos(productos):
    try:
        with open(RUTA_PRODUCTOS, "w", encoding="utf-8") as f:
            json.dump(productos, f, indent=4, ensure_ascii=False)
    except Exception:
        return


# ─────────────────────────────────────────────────────────────────────────────
# CARGAR VENTAS (para historial.py)
# ─────────────────────────────────────────────────────────────────────────────

def registro_de_ventas():
    try:
        with open(RUTA_JSON, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []




# ─────────────────────────────────────────────────────────────────────────────
# OBTENER CONTRASEÑA
# ─────────────────────────────────────────────────────────────────────────────

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def obtener_contraseña():
    try:
        with open(RUTA_ADMIN,"r",encoding="utf-8") as f:
            config = json.load(f)
        return config.get("password")
    
    except FileNotFoundError:
        config = {"password": hash_password("admin")}

        with open(RUTA_ADMIN, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        return config["password"]
    except Exception:
        return None



# ─────────────────────────────────────────────────────────────────────────────
# CONTRASEÑA
# ─────────────────────────────────────────────────────────────────────────────

# /////// VERIFICAR \\\\\\\\\
def verificar_contraseña(msg_error,ingresado,funcion):
    try:
        user_try = ingresado.get()
        if hash_password(user_try) == obtener_contraseña():
            funcion()
            return
        else:
            msg_error["text"] = "ERROR, contraseña incorrecta"
            msg_error["font"] = ("Segoe UI", 15)
    except Exception:
        msg_error["text"] = "Un error ha ocurrido, intente de nuevo"
        msg_error["font"] = ("Segoe UI", 15)


# /////// MOSTRAR \\\\\\\\\
def mostrar(boton,*inputs):
    for ingresado in inputs:
        if ingresado["show"] == "*":
            ingresado["show"] = ""
            boton["text"] = "Ocultar contraseña"
        else:
            ingresado["show"] = "*"
            boton["text"] = "Mostrar contraseña"


def ventana_contraseña(funcion):
    BG      = "#1E293B"
    btn_stock    = "#16A34A"
    btn_stock_pressed = "#15803D"
    FONT_BTN       = ("Segoe UI", 11, "bold")
    black_color = "#1A1F71"
    contra = "#FF647B"
    contra_press = "#FFA6B4"


    mini_window = tkinter.Toplevel()
    mini_window.title("Verificar contraseña")
    mini_window.geometry("550x220")
    mini_window.resizable(True, True)
    mini_window.configure(background=BG)


    frame_header = tkinter.Frame(mini_window, background=BG)
    frame_header.pack(fill="x", padx=20, pady=(12, 0))

    titulo = tkinter.Label(
        frame_header,
        text="VERIFICAR CONTRASEÑA",
        font=("Segoe UI", 16, "bold"),
        foreground="#FFFFFF",
        background=BG,
    )

    texto = tkinter.Label(
        frame_header,
        text="Esta es una area de administrador, antes de ingresar verifiquese",
        font=("Segoe UI", 10),
        foreground="#94A3B8",
        background=BG,
    )

    msg_error = tkinter.Label(
        frame_header,
        text="",
        font=("Segoe UI", 1),
        foreground="#FF647B",
        background=BG,
    )
    msg_error.pack()

    ingresado = tkinter.Entry(
        frame_header,
        font=("Arial",15),
        foreground= black_color,
        borderwidth=5,
        show="*"
    )

    titulo.pack()
    texto.pack()
    ingresado.pack()

    frame_botones = tkinter.Frame(mini_window, background=BG)
    frame_botones.pack(padx=20, pady=(12, 0))

    ingresar = tkinter.Button(
        frame_botones,
        text="Ingresar",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_stock,
        activebackground=btn_stock_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda: verificar_contraseña(msg_error,ingresado,funcion)
    )
    ingresar.pack(padx=8,side="left")

    mostrar_contra = tkinter.Button(
        frame_botones,
        text="Mostrar contraseña",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=contra,
        activebackground=contra_press,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda: mostrar(mostrar_contra,ingresado)
    )
    mostrar_contra.pack(padx=8,side="right")


# ─────────────────────────────────────────────────────────────────────────────
# CAMBIO CONTRASEÑA
# ─────────────────────────────────────────────────────────────────────────────

def confirmar_cambio(msg_error,ingresado,nueva,confirmar,ventana):
    try:
        cont_actual = ingresado.get()
        cont_nueva = nueva.get()
        cont_confirmar = confirmar.get()

        if hash_password(cont_actual) != obtener_contraseña():
            msg_error.config(text="La contraseña actual no coincide",font=("Segoe UI", 15))
            return
        
        if not cont_nueva.strip():
            msg_error.config(text="La contraseña nueva no puede estar vacia",font=("Segoe UI", 15))
            return

        if cont_nueva != cont_confirmar:
            msg_error.config(text="Las contraseñas no coinciden",font=("Segoe UI", 15))
            return
        
        if cont_nueva == cont_actual:
            msg_error.config(text="La contraseña nueva es igual a la contraseña actual",font=("Segoe UI", 15))
            return  
        
        nueva_contraseña_json = {"password": hash_password(cont_nueva)}

        with open(RUTA_ADMIN,"w",encoding="utf-8") as f:
            json.dump(nueva_contraseña_json,f,indent=4)

        msg_error.config(text="Contraseña actualizada correctamente",font=("Segoe UI", 15),foreground="#16A34A")
        ventana.after(2000, ventana.destroy)


    except Exception:
        msg_error["text"] = "Un error ha ocurrido, intente de nuevo"
        msg_error["font"] = ("Segoe UI", 15)


def ventana_cambio():
    BG      = "#1E293B"
    btn_stock    = "#16A34A"
    btn_stock_pressed = "#15803D"
    FONT_BTN       = ("Segoe UI", 11, "bold")
    black_color = "#1A1F71"
    contra = "#FF647B"
    contra_press = "#FFA6B4"
    btn_cancel         = "#EF4444"
    btn_cancel_pressed = "#DC2626"


    mini_window = tkinter.Toplevel()
    mini_window.title("Cambiar contraseña")
    mini_window.geometry("750x400")
    mini_window.resizable(True, True)
    mini_window.configure(background=BG)


    frame_header = tkinter.Frame(mini_window, background=BG)
    frame_header.pack(fill="x", padx=20, pady=(12, 0))

    # //////// HEADER \\\\\\\\
    titulo = tkinter.Label(
        frame_header,
        text="CAMBIAR CONTRASEÑA",
        font=("Segoe UI", 16, "bold"),
        foreground="#FFFFFF",
        background=BG,
    )


    msg_error = tkinter.Label(
        frame_header,
        text="",
        font=("Segoe UI", 1),
        foreground="#FF647B",
        background=BG,
    )
    msg_error.pack()
    
    # //////// INPUTS \\\\\\\\

    texto = tkinter.Label(
        frame_header,
        text="Ingrese su contraseña actual",
        font=("Segoe UI", 10),
        foreground="#94A3B8",
        background=BG,
    )

    ingresado = tkinter.Entry(
        frame_header,
        font=("Arial",15),
        foreground= black_color,
        borderwidth=5,
        show="*"
    )

    # NUEVA CONTRASEÑA
    texto_2 = tkinter.Label(
        frame_header,
        text="Ingrese su contraseña nueva",
        font=("Segoe UI", 10),
        foreground="#94A3B8",
        background=BG,
    )

    nueva = tkinter.Entry(
        frame_header,
        font=("Arial",15),
        foreground= black_color,
        borderwidth=5,
        show="*"
    )

    # CONFIRMACION

    texto_3 = tkinter.Label(
        frame_header,
        text="Confirme la nueva contraseña",
        font=("Segoe UI", 10),
        foreground="#94A3B8",
        background=BG,
    )

    confirmacion = tkinter.Entry(
        frame_header,
        font=("Arial",15),
        foreground= black_color,
        borderwidth=5,
        show="*"
    )

    titulo.pack()
    texto.pack(pady=(8,0))
    ingresado.pack(pady=(8,0))
    texto_2.pack(pady=(8,0))
    nueva.pack(pady=(8,0))
    texto_3.pack(pady=(8,0))
    confirmacion.pack(pady=(8,0))

    frame_botones = tkinter.Frame(mini_window, background=BG)
    frame_botones.pack(padx=20, pady=(12, 0))


    # //////// BOTONES \\\\\\\\
    guardar_cambio = tkinter.Button(
        frame_botones,
        text="Guardar cambios",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_stock,
        activebackground=btn_stock_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda: confirmar_cambio(msg_error,ingresado,nueva,confirmacion,mini_window)
    )
    guardar_cambio.pack(padx=8,side="left")

    mostrar_contra = tkinter.Button(
        frame_botones,
        text="Mostrar contraseñas",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=contra,
        activebackground=contra_press,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda: mostrar(mostrar_contra,ingresado,nueva,confirmacion)
    )
    mostrar_contra.pack(padx=8,side="left")

    cancelar = tkinter.Button(
        frame_botones,
        text="Cancelar",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_cancel,
        activebackground=btn_cancel_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=mini_window.destroy,
    )
    cancelar.pack(padx=8,side="left")


# ─────────────────────────────────────────────────────────────────────────────
# AGREGAR PRODUCTO
# ─────────────────────────────────────────────────────────────────────────────

def agregar_producto(mini_window,nombre,precio,stk_inicial,confirmado,msg_error,refrescar_stock):

    try:
        
        productos = cargar_productos()
        lista_nombres = [producto["producto"].lower() for producto in productos]

        # === VALIDANDO DATOS ===
        if not nombre.get().strip():
            msg_error["text"] = "Ingrese valores validos"
            msg_error["font"] = ("Segoe UI", 15)
            return

        if not precio.get().isdigit():
            msg_error["text"] = "Ingrese valores validos"
            msg_error["font"] = ("Segoe UI", 15)
            return
        
        if not stk_inicial.get().isdigit():
            msg_error["text"] = "Ingrese valores validos"
            msg_error["font"] = ("Segoe UI", 15)
            return
        
        if nombre.get().lower() in lista_nombres:
            msg_error["text"] = "El producto ya esta agregado"
            msg_error["font"] = ("Segoe UI", 15)
            return

        # ==== CONFIRMACION PRODUCTO ===
        firma_actual = (
            nombre.get().strip().lower(),
            precio.get().strip(),
            stk_inicial.get().strip()
        )

        if confirmado.get() != str(firma_actual):
            confirmado.set(str(firma_actual))

            msg_error.config(
                text=f"Pulse nuevamente para agregar: {nombre.get()}",
                font=("Segoe UI", 15),
                foreground="#FF9D23"
            )
            return

        nuevo = {
            "producto":nombre.get(),
            "costo":int(precio.get()),
            "stock":int(stk_inicial.get())
        }
        productos.append(nuevo)
        actualizar_productos(productos)
        msg_error.config(text="Producto agregado exitosamente",font=("Segoe UI", 15),foreground="#00A210")

        mini_window.after(1000, lambda: (mini_window.destroy(),refrescar_stock() ) )

    except Exception:
        msg_error["text"] = "Un error ha ocurrido, intente de nuevo"
        msg_error["font"] = ("Segoe UI", 15)


# ─────────────────────────────────────────────────────────────────────────────
# VENTANA
# ─────────────────────────────────────────────────────────────────────────────

def ventana_agregar(mini_window,refrescar_stock):
    for widget in mini_window.winfo_children():
        widget.destroy()

    confirmado = tkinter.StringVar(value="")
    BG      = "#1E293B"
    btn_stock    = "#16A34A"
    btn_stock_pressed = "#15803D"
    FONT_BTN       = ("Segoe UI", 11, "bold")
    black_color = "#1A1F71"
    contra = "#FF647B"
    contra_press = "#FFA6B4"
    btn_cancel         = "#EF4444"
    btn_cancel_pressed = "#DC2626"


    mini_window.title("Cambiar contraseña")
    mini_window.geometry("550x470")
    mini_window.resizable(True, True)
    mini_window.configure(background=BG)


    frame_header = tkinter.Frame(mini_window, background=BG)
    frame_header.pack(fill="x", padx=20, pady=(12, 0))

    # //////// HEADER \\\\\\\\
    titulo = tkinter.Label(
        frame_header,
        text="AGREGAR PRODUCTO",
        font=("Segoe UI", 16, "bold"),
        foreground="#FFFFFF",
        background=BG,
    )
    titulo.pack()

    # //// BOTONES SUPERIORES \\\\\\
    frame_botones_superior = tkinter.Frame(frame_header, background=BG)
    frame_botones_superior.pack(padx=20, pady=(12, 0))


    mostrar_eliminar = tkinter.Button(
        frame_botones_superior,
        text="Eliminar producto",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=contra,
        activebackground=contra_press,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda: ventana_eliminar(mini_window,refrescar_stock)
    )
    mostrar_eliminar.pack(padx=8,side="left")

    # ERROR
    msg_error = tkinter.Label(
        frame_header,
        text="",
        font=("Segoe UI", 1),
        foreground="#FF0026",
        background=BG,
    )
    msg_error.pack()

    
    # //////// INPUTS \\\\\\\\

    # NOMBRE
    texto = tkinter.Label(
        frame_header,
        text="Nombre del producto",
        font=("Segoe UI", 10, "bold"),
        foreground="#94A3B8",
        background=BG,
    )

    nombre = tkinter.Entry(
        frame_header,
        font=("Arial",15),
        foreground= black_color,
        borderwidth=5,
        width=30
    )

    # COSTO
    texto_2 = tkinter.Label(
        frame_header,
        text="Precio (COP)",
        font=("Segoe UI", 10, "bold"),
        foreground="#94A3B8",
        background=BG,
    )
    validar = frame_header.register(solo_numeros)
    precio = tkinter.Entry(
        frame_header,
        font=("Arial",15),
        foreground= black_color,
        borderwidth=5,
        validate="key",
        validatecommand=(validar,"%P")
    )

    # STOCK INICIAL

    texto_3 = tkinter.Label(
        frame_header,
        text="Ingrese el stock inicial",
        font=("Segoe UI", 10, "bold"),
        foreground="#94A3B8",
        background=BG
    )

    stk_inicial = tkinter.Entry(
        frame_header,
        font=("Arial",15),
        foreground= black_color,
        borderwidth=5,
        validate="key",
        validatecommand=(validar,"%P")
    )

 
    texto.pack(pady=(8,0))
    nombre.pack(pady=(8,0))
    texto_2.pack(pady=(8,0))
    precio.pack(pady=(8,0))
    texto_3.pack(pady=(8,0))
    stk_inicial.pack(pady=(8,0))

    def reiniciar_confirmacion(event=None):
        confirmado.set("")
        msg_error.config(text="", font=("Segoe UI", 1))

    nombre.bind("<KeyRelease>", reiniciar_confirmacion)
    precio.bind("<KeyRelease>", reiniciar_confirmacion)
    stk_inicial.bind("<KeyRelease>", reiniciar_confirmacion)


    # //////// BOTONES INFERIORES \\\\\\\\
    frame_botones_inferior = tkinter.Frame(mini_window, background=BG)
    frame_botones_inferior.pack(padx=20, pady=(12, 0))

    agregar = tkinter.Button(
        frame_botones_inferior,
        text="➕ Agregar",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_stock,
        activebackground=btn_stock_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda : agregar_producto(mini_window,nombre,precio,stk_inicial,confirmado,msg_error,refrescar_stock)
    )
    agregar.pack(padx=8,side="left")

    cancelar = tkinter.Button(
        frame_botones_inferior,
        text="✖️ Cancelar",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_cancel,
        activebackground=btn_cancel_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=mini_window.destroy,
    )
    cancelar.pack(padx=8,side="left")

# ─────────────────────────────────────────────────────────────────────────────
# ELIMINAR PRODUCTO
# ─────────────────────────────────────────────────────────────────────────────

def eliminar_producto(msg_error,var,confirmado,mini_window,refrescar_stock):
    try:
        ingresado = var.get().upper().strip()
        productos = cargar_productos()
        nombres = [p["producto"].upper() for p in productos]

        if ingresado not in nombres:
            msg_error["text"] = "Producto invalido, ingrese el producto directamente de la lista"
            msg_error["font"] = ("Segoe UI", 15)
            return
        
        if confirmado.get() != ingresado:
            confirmado.set(ingresado)

            msg_error.config(
                text=f"Pulse nuevamente para eliminar: {ingresado}",
                font=("Segoe UI", 15),
                foreground="#E40B00"
            )
            return
        
        productos = [producto for producto in productos if producto["producto"].upper() != ingresado]
        actualizar_productos(productos)

        msg_error.config(text="Producto eliminado exitosamente",font=("Segoe UI", 15),foreground="#00A210")

        mini_window.after(1000, lambda: (mini_window.destroy(),refrescar_stock() ) )

    except Exception:
        msg_error["text"] = "Un error ha ocurrido, intente de nuevo"
        msg_error["font"] = ("Segoe UI", 15)

# ─────────────────────────────────────────────────────────────────────────────
# VENTANA
# ─────────────────────────────────────────────────────────────────────────────
def ventana_eliminar(mini_window,refrescar_stock):
    for widget in mini_window.winfo_children():
        widget.destroy()


    BG      = "#1E293B"
    btn_stock    = "#16A34A"
    btn_stock_pressed = "#15803D"
    FONT_BTN       = ("Segoe UI", 11, "bold")
    contra = "#FF647B"
    btn_eliminar_pressed         = "#EF4444"
    btn_eliminar = "#DC2626"

    btn_pv = "#f59622"
    btn_pv_pressed = "#ff7514"

    productos = cargar_productos()
    nombres = [p["producto"].upper() for p in productos]


    mini_window.title("Cambiar contraseña")
    mini_window.geometry("550x470")
    mini_window.resizable(True, True)
    mini_window.configure(background=BG)


    frame_header = tkinter.Frame(mini_window, background=BG)
    frame_header.pack(fill="x", padx=20, pady=(12, 0))

    # //////// HEADER \\\\\\\\
    titulo = tkinter.Label(
        frame_header,
        text="ELIMINAR PRODUCTO",
        font=("Segoe UI", 16, "bold"),
        foreground="#FFFFFF",
        background=BG,
    )
    titulo.pack()

    # //// BOTONES SUPERIORES \\\\\\
    frame_botones_superior = tkinter.Frame(frame_header, background=BG)
    frame_botones_superior.pack(padx=20, pady=(12, 0))


    mostrar_agregar = tkinter.Button(
        frame_botones_superior,
        text="Agregar producto",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_stock,
        activebackground=btn_stock_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda: ventana_agregar(mini_window,refrescar_stock)
    )
    mostrar_agregar.pack(padx=8,side="left")

    # ERROR
    msg_error = tkinter.Label(
        frame_header,
        text="",
        font=("Segoe UI", 1),
        foreground=contra,
        background=BG,
    )
    msg_error.pack()

    
    # //////// INPUTS \\\\\\\\

    # NOMBRE
    texto = tkinter.Label(
        frame_header,
        text="Seleccione el producto a eliminar",
        font=("Segoe UI", 12, "bold"),
        foreground="#94A3B8",
        background=BG,
    )

    var = tkinter.StringVar()
    confirmado = tkinter.StringVar(value="")

    def reiniciar_confirmacion(*args):
        confirmado.set("")
        msg_error.config(text="", font=("Segoe UI", 1))

    var.trace_add("write", reiniciar_confirmacion)

    productos = ttk.Combobox(frame_header,values=nombres,textvariable=var,width=45)

    def filtrar_productos(event):
        ingresado = var.get().upper()
        filtrado = [p for p in nombres if ingresado in p]
        productos["values"] = filtrado
    productos.bind("<KeyRelease>",filtrar_productos)


    texto.pack(pady=(8,0))
    productos.pack(pady=(8,0))



    # //////// BOTONES INFERIORES \\\\\\\\
    frame_botones_inferior = tkinter.Frame(mini_window, background=BG)
    frame_botones_inferior.pack(padx=20, pady=(12, 0))

    agregar = tkinter.Button(
        frame_botones_inferior,
        text="🚮 Eliminar",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_eliminar,
        activebackground=btn_eliminar_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda : eliminar_producto(msg_error,var,confirmado,mini_window,refrescar_stock)
    )
    agregar.pack(padx=8,side="left")

    cancelar = tkinter.Button(
        frame_botones_inferior,
        text="✖️ Cancelar",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_pv,
        activebackground=btn_pv_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=mini_window.destroy,
    )
    cancelar.pack(padx=8,side="left")


def mini_ventana_madre(refrescar_stock):
    mini_window = tkinter.Toplevel()
    ventana_agregar(mini_window,refrescar_stock)
    

# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICAS
# ─────────────────────────────────────────────────────────────────────────────

def mostrar_graficas(registro):
    """
    Abre una ventana con dos gráficas:
      1. Recaudado agrupado (el usuario elige: Días / Semanas / Meses)
      2. Productos más vendidos (barras horizontales, siempre igual)
    """
    try:
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from collections import Counter, defaultdict
    except ImportError:
        return

    if not registro:
        return

    FORMATOS = [
        "%a %d %B %Y",
        "%a %d %b %Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
    ]

    def parsear_fecha(texto_fecha):
        parte = texto_fecha.split(",")[0].strip()
        for fmt in FORMATOS:
            try:
                return datetime.strptime(parte, fmt)
            except ValueError:
                continue
        return None

    puntos = []
    contador_productos = Counter()

    for venta in registro:
        fecha = parsear_fecha(venta["fecha"])
        try:
            total_num = int(venta["Total"].replace("$ ", "").replace(".", ""))
        except Exception:
            total_num = 0
        if fecha:
            puntos.append((fecha, total_num))
        for prod in venta["producto"]:
            contador_productos[prod["producto"]] += prod["cantidad"]

    agrupacion_auto = "dia"
    if puntos:
        fechas_validas = [p[0] for p in puntos]
        rango_dias = (max(fechas_validas) - min(fechas_validas)).days
        if rango_dias > 90:
            agrupacion_auto = "mes"
        elif rango_dias > 14:
            agrupacion_auto = "semana"

    def agrupar(modo):
        from collections import defaultdict
        acumulado = defaultdict(int)
        for fecha, total in puntos:
            if modo == "dia":
                clave = fecha.strftime("%d/%m/%y")
            elif modo == "semana":
                iso = fecha.isocalendar()
                clave = f"S{iso[1]:02d}\n{iso[0]}"
            else:
                clave = fecha.strftime("%b %Y")
            acumulado[clave] += total

        if modo == "semana":
            claves = sorted(acumulado.keys(),
                            key=lambda k: (int(k.split("\n")[1]), int(k.split("\n")[0][1:])))
        elif modo == "mes":
            claves = sorted(acumulado.keys(),
                            key=lambda k: datetime.strptime(k, "%b %Y"))
        else:
            claves = sorted(acumulado.keys(),
                            key=lambda k: datetime.strptime(k, "%d/%m/%y"))

        return claves, [acumulado[k] for k in claves]

    BG      = "#1E293B"
    BG_PLOT = "#0F172A"
    AZUL    = "#3B82F6"
    VERDE   = "#4ADE80"
    TEXTO   = "#CBD5E1"
    BTN_ACT = "#3B82F6"
    BTN_INK = "#334155"

    ventana_graf = tkinter.Toplevel()
    ventana_graf.title("Gráficas de Ventas")
    ventana_graf.geometry("1100x620")
    ventana_graf.configure(background=BG)
    ventana_graf.resizable(True, True)

    frame_header = tkinter.Frame(ventana_graf, background=BG)
    frame_header.pack(fill="x", padx=20, pady=(12, 0))

    tkinter.Label(
        frame_header,
        text="ANÁLISIS DE VENTAS",
        font=("Segoe UI", 16, "bold"),
        foreground="#FFFFFF",
        background=BG,
    ).pack(side="left")

    tkinter.Label(
        frame_header,
        text=f"{len(registro)} ventas registradas",
        font=("Segoe UI", 10),
        foreground="#94A3B8",
        background=BG,
    ).pack(side="left", padx=(12, 0))

    frame_toggle = tkinter.Frame(ventana_graf, background=BG)
    frame_toggle.pack(pady=(8, 4))

    tkinter.Label(
        frame_toggle,
        text="Agrupar por:",
        font=("Segoe UI", 10),
        foreground="#94A3B8",
        background=BG,
    ).pack(side="left", padx=(0, 8))

    OPCIONES = [("Días", "dia"), ("Semanas", "semana"), ("Meses", "mes")]
    botones_toggle = {}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor(BG)

    def redibujar(modo):
        for m, btn in botones_toggle.items():
            btn.configure(background=BTN_ACT if m == modo else BTN_INK, relief="flat")

        ax1.clear()

        if not puntos:
            ax1.text(0.5, 0.5, "No se pudieron leer las fechas",
                     ha="center", va="center", color=TEXTO,
                     transform=ax1.transAxes, fontsize=10)
            ax1.set_facecolor(BG_PLOT)
            canvas_graf.draw()
            return

        claves, valores = agrupar(modo)
        n = len(claves)
        fontsize_tick  = max(6, 9  - max(0, n - 16))
        fontsize_label = max(5, 7  - max(0, n - 16))

        bars = ax1.bar(range(n), valores, color=AZUL, edgecolor="#2563EB", linewidth=0.4)
        ax1.set_xticks(range(n))
        ax1.set_xticklabels(claves, rotation=40, ha="right", fontsize=fontsize_tick)
        ax1.set_facecolor(BG_PLOT)

        label_modo = {"dia": "día", "semana": "semana", "mes": "mes"}[modo]
        ax1.set_title(f"Recaudado por {label_modo}", color=TEXTO, fontsize=12, pad=10)
        ax1.set_ylabel("Total ($)", color=TEXTO, fontsize=9)
        ax1.tick_params(colors=TEXTO)
        ax1.spines["bottom"].set_color("#334155")
        ax1.spines["left"].set_color("#334155")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"${int(x):,}".replace(",", "."))
        )

        if n <= 30:
            max_val = max(valores) if valores else 1
            for bar, val in zip(bars, valores):
                ax1.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max_val * 0.012,
                    f"${val:,}".replace(",", "."),
                    ha="center", va="bottom",
                    color=TEXTO, fontsize=fontsize_label,
                )

        fig.tight_layout(pad=2.5)
        canvas_graf.draw()

    for label, modo in OPCIONES:
        btn = tkinter.Button(
            frame_toggle,
            text=label,
            font=("Segoe UI", 10, "bold"),
            foreground="#FFFFFF",
            background=BTN_INK,
            activebackground=BTN_ACT,
            activeforeground="#FFFFFF",
            relief="flat",
            padx=16, pady=5,
            cursor="hand2",
            command=lambda m=modo: redibujar(m),
        )
        btn.pack(side="left", padx=4)
        botones_toggle[modo] = btn

    if contador_productos:
        top_n      = 10
        items      = contador_productos.most_common(top_n)
        nombres    = [i[0] for i in reversed(items)]
        cantidades = [i[1] for i in reversed(items)]

        bars2 = ax2.barh(nombres, cantidades, color=VERDE, edgecolor="#16A34A", linewidth=0.4)
        ax2.set_facecolor(BG_PLOT)
        ax2.set_title(f"Top {top_n} productos más vendidos", color=TEXTO, fontsize=12, pad=10)
        ax2.set_xlabel("Unidades vendidas", color=TEXTO, fontsize=9)
        ax2.tick_params(colors=TEXTO, labelsize=8)
        ax2.spines["bottom"].set_color("#334155")
        ax2.spines["left"].set_color("#334155")
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        max_cant = max(cantidades)
        for bar, val in zip(bars2, cantidades):
            ax2.text(val + max_cant * 0.01, bar.get_y() + bar.get_height() / 2,
                     str(val), va="center", color=TEXTO, fontsize=8)
    else:
        ax2.text(0.5, 0.5, "Sin datos de productos", ha="center", va="center",
                 color=TEXTO, transform=ax2.transAxes, fontsize=10)
        ax2.set_facecolor(BG_PLOT)

    canvas_graf = FigureCanvasTkAgg(fig, master=ventana_graf)
    canvas_graf.draw()
    canvas_graf.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=(0, 16))

    redibujar(agrupacion_auto)

