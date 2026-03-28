import tkinter
from tkinter import ttk
from datetime import datetime
import os
import json
import pandas as pd

def puntos_de_mil(numero):
    try:
        numero = int(numero)
        return f"$ {numero:,}".replace(",", ".") # 100 000 000 000
    except:
        return "$ 0"


def calcular_total(precio_unitario,cantidad_de_productos,label_total):
    if not precio_unitario:
        return
    numero_de_productos = cantidad_de_productos.get()
    if numero_de_productos.isdigit():
        numero_de_productos = int(numero_de_productos)

        total = str(precio_unitario*numero_de_productos)
        label_total["text"] = puntos_de_mil(total)




# ─────────────────────────────────────────────────────────────────────────────
# ACTUALIZAR TOTAL
# ─────────────────────────────────────────────────────────────────────────────

def actualizar_total_general(filas,label_text):
    total = 0
    for fila in filas:
        texto = fila["total"]["text"]
        # Limpiar el texto y convertir a número
        numero = texto.replace("$ ", "").replace(".", "")
        if numero:
            try:
                total += int(numero)
            except:
                pass

    label_text["text"] = puntos_de_mil(str(total))

# ─────────────────────────────────────────────────────────────────────────────
# ELIMINAR FILA
# ─────────────────────────────────────────────────────────────────────────────

def eliminar_fila(fila,filas,label_text,devueltas_total_de_todo,ingresado,precio_total_de_todo):
    for widget in fila.values():
        if isinstance(widget,ttk.Combobox):
            widget.set("")
            continue
        elif isinstance(widget,tkinter.Label):
            widget["text"] = "$ 0"
    ingresado.delete(0,tkinter.END) #eliminacion de ingresado hecho con ayuda de IA
    devueltas_total_de_todo["text"] = "$ 0"
    actualizar_total_general(filas,label_text)
    obtener_devueltas(precio_total_de_todo,ingresado,devueltas_total_de_todo)

# ─────────────────────────────────────────────────────────────────────────────
# ELIMINAR TODOS LOS DATOS
# ─────────────────────────────────────────────────────────────────────────────

def eliminar_datos_todo(filas,label_text,devueltas_total_de_todo,ingresado,precio_total_de_todo):
    for fila in filas:
        eliminar_fila(fila,filas,label_text,devueltas_total_de_todo,ingresado,precio_total_de_todo)


def obtener_devueltas(precio_total_de_todo,ingresado,devueltas_total_de_todo):
    
    try:
        precio_total = precio_total_de_todo["text"].replace("$ ", "").replace(".", "")
        precio_total = int(precio_total)
    except:
        return
        
    if ingresado.get().isdigit():
        pago = int(ingresado.get())
    try:
        devueltas = pago - precio_total
    except:
        return
    if devueltas < 0 :
        devueltas_total_de_todo["text"] = "Pago insuficiente"
    else:
        devueltas_total_de_todo["text"] = puntos_de_mil(devueltas)

# ─────────────────────────────────────────────────────────────────────────────
# GUARDAR VENTA
# ─────────────────────────────────────────────────────────────────────────────

def guardar_venta(label_total,filas,mensaje_exito,devueltas_total_de_todo,ingresado,precio_total_de_todo):

    ruta = os.path.join(os.getcwd(), "Registro_Ventas.json")
    ruta_excel = "Registro_de_ventas.xlsx"
    filas_excel = []


    try:
        with open(ruta, "r") as f:
            ventas = json.load(f)
    except:
        ventas = []
    

    now = datetime.now()
    tiempo = now.strftime("%a %d %B %Y, %I:%M:%S %p")


    if ingresado.get().isdigit():
        pago = int(ingresado.get())
    elif ingresado.get() == "":
        mensaje_exito["text"] = "⚠️ Ingrese la cantidad con la que pago el cliente"
        return
    else:
        mensaje_exito["text"] = "⚠️ Pago del cliente invalido"
        return
    
    devueltas = devueltas_total_de_todo["text"].replace("$ ", "").replace(".", "")
    if not devueltas.isdigit():
        mensaje_exito["text"] = "⚠️ Pago insuficiente"
        return

    productos_lista = []
    for fila in filas:
        producto = fila["producto"].get()
        cantidad = fila["cantidad"].get()

        if producto and cantidad.isdigit():
            productos_lista.append({
                "producto":producto,
                "cantidad":int(cantidad)
            })
    if not productos_lista:
        mensaje_exito["text"] = "⚠️ Agrega al menos un producto con cantidad válida"
        return
    venta = {
        "id":len(ventas)+1,
        "producto":productos_lista,
        "Total":label_total["text"],
        "pagado":pago,
        "devueltas":devueltas,
        "fecha":tiempo
    }

    # // LISTA FILAS EXCEL //
    for item in productos_lista:
        filas_excel.append({
            "id":len(ventas)+1,
            "producto":item["producto"],
            "cantidad":item["cantidad"],
            "Total":label_total["text"],
            "pagado":pago,
            "devueltas":devueltas,
            "fecha":tiempo
        })

    df_nuevo = pd.DataFrame(filas_excel)

    ventas.append(venta)
    eliminar_datos_todo(filas,label_total,devueltas_total_de_todo,ingresado,precio_total_de_todo)
    mensaje_exito["text"] = "Venta guardada exitosamente!"
    
    with open(ruta,"w") as f:
        json.dump(ventas,f,indent=4,ensure_ascii=False)

    # //  EXCEL

    if os.path.exists(ruta_excel):
        df_viejo = pd.read_excel(ruta_excel)
        df_final = pd.concat([df_viejo,df_nuevo],ignore_index=True)
    else:
        df_final = df_nuevo
    df_final.to_excel(ruta_excel, index=False)