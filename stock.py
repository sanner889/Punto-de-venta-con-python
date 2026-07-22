import tkinter
from tkinter import ttk
import module

# ─────────────────────────────────────────────────────────────────────────────
# COLORES Y FUENTES
# ─────────────────────────────────────────────────────────────────────────────
bg_main    = "#D1D4D9"
bg_header  = "#1E293B"
bg_table   = "#F8FAFC"
bg_row_par = "#FFFFFF"
bg_row_imp = "#E2EEFD"
bg_hover   = "#DBEAFE"
bg_total   = "#F3F4F6"

# /// botones
btn_color  = "#3B82F6"
btn_pressed= "#2563EB"
btn_stock    = "#16A34A"
btn_stock_pressed = "#15803D"
btn_pv = "#f59622"
btn_pv_pressed = "#ff7514"
btn_contraseña = "#7C3AED"
btn_contraseña_pressed = "#6D28D9"
btn_mod = "#FF6363"
btn_mod_pressed = "#FF8282"
#//texto
color_titulo    = "#FFFFFF"
color_subtitulo = "#94A3B8"
color_texto     = "#1E293B"
color_header_col= "#334155"
bg_footer  = "#1E293B"

FONT_TITULO    = ("Segoe UI", 32, "bold")
FONT_SUBTITULO = ("Segoe UI", 18)
FONT_HEADER    = ("Segoe UI", 18, "bold")
FONT_COL       = ("Segoe UI", 11, "bold")
FONT_BODY      = ("Segoe UI", 12)
FONT_TOTAL     = ("Segoe UI", 13, "bold")
FONT_BTN       = ("Segoe UI", 11, "bold")
FONT_FOOTER    = ("Segoe UI", 12, "bold")

def creacion(window,ir_a_historial,ir_a_punto_de_venta):

    def refrescar_stock():
        for widget in window.winfo_children():
            widget.destroy()

        mostrar_stock(
            window,
            ir_a_historial,
            ir_a_punto_de_venta
        )

    row = 0
    productos = module.cargar_productos()
    productos.sort(key=lambda p: p["producto"].lower())


    frame = tkinter.Frame(window,background=bg_header)
    frame.pack(fill="x")

    # ─────────────────────────────────────────────────────────────────────────────
    # HEADER 
    # ─────────────────────────────────────────────────────────────────────────────

    #  ──────── TITULOS ────────

    titulo = tkinter.Label(
        frame,
        text="REGISTRO DE STOCK",
        font=FONT_TITULO,
        foreground=color_titulo,
        background=bg_header,
    )

    subtitulo = tkinter.Label(
        frame,
        text="Tienda",
        font=FONT_SUBTITULO,
        foreground=color_subtitulo,
        background=bg_header,
    )

    titulo.pack(pady=(20,0))
    subtitulo.pack()

    msg = tkinter.Label(
        frame,
        text="",
        font=("Segoe UI", 1),
        foreground=btn_stock,
        background=bg_header,
    )
    msg.pack()

    #  ──────── BOTONES ────────
    
    #botones 1

    frame_botones_superior = tkinter.Frame(frame,background=bg_header)
    frame_botones_superior.pack(pady=(8,4))

    frame_botones_inferior = tkinter.Frame(frame,background=bg_header)
    frame_botones_inferior.pack(pady=(0,8))

    #  ──────── SUPERIORES ────────
    boton_historial = tkinter.Button(
        frame_botones_superior,
        text="📋  Ver Historial",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_color,
        activebackground=btn_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command= lambda: module.ventana_contraseña(ir_a_historial)
    )
    boton_historial.pack(side="left",padx=8)

    boton_punto_de_venta = tkinter.Button(
        frame_botones_superior,
        text="🛒  Ver Punto de Venta",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_pv,
        activebackground=btn_pv_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command= ir_a_punto_de_venta
    )
    boton_punto_de_venta.pack(side="left",padx=8)

     #  ──────── INFRERIORES  ────────

    boton_cambio_contraseña = tkinter.Button(
        frame_botones_inferior,
        text="🔑  Cambiar Contraseña",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_contraseña,
        activebackground=btn_contraseña_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command= module.ventana_cambio
    )
    boton_cambio_contraseña.pack(side="left",padx=8)

    boton_modificar_stock = tkinter.Button(
        frame_botones_inferior,
        text="✅ Agregar / ❎ Eliminar Producto",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_mod,
        activebackground=btn_mod_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda: module.mini_ventana_madre(refrescar_stock)
    )
    boton_modificar_stock.pack(side="left",padx=8)


    # ──────────────────────────────────────────────────────────────────────────────────
    # CONTENEDOR CON SCROLL (SOLUCIÓN AL CRECIMIENTO INFINITO) # HECHO CON AYUDA DE IA
    # ──────────────────────────────────────────────────────────────────────────────────

    container = tkinter.Frame(window, background=bg_main)
    container.pack(fill="both", expand=True)

    canvas = tkinter.Canvas(container, background=bg_table, highlightthickness=0)
    scrollbar = tkinter.Scrollbar(container, orient="vertical", command=canvas.yview)

    frame_tabla = tkinter.Frame(canvas, background=bg_table)
    canvas.create_window((0, 0), window=frame_tabla, anchor="nw")

    def configurar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Ajustar el ancho del frame interno al del canvas
        canvas.itemconfig(1, width=canvas.winfo_width())

    frame_tabla.bind("<Configure>", configurar_scroll)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    encabezados = ["Producto","Precio","Stock"]
    weight = [2,1,1]

    for i,peso in enumerate(weight):
        frame_tabla.columnconfigure(i,weight=peso,minsize=80)

    for posicion,columna in enumerate(encabezados):

        encabezado = tkinter.Label(
            frame_tabla,
            text=columna,
            font=FONT_COL,
            foreground="#FFFFFF",
            background=color_header_col,
            padx=12,pady=10
        ) 
        encabezado.grid(row=0,column=posicion,sticky="we")

    # ──────────────────────────────────────────────────────────────────────────────────
    # NO HAY PRODUCTOS
    # ──────────────────────────────────────────────────────────────────────────────────

    if not productos:
        aviso = tkinter.Label(
            frame_tabla,
            text="NO HAY VENTAS REGISTRADAS",
            font=FONT_SUBTITULO,
            foreground=bg_header,
            background=bg_table,
            pady=30
        )
        aviso.grid(row=2,column=0,columnspan=3)


    # ──────────────────────────────────────────────────────────────────────────────────
    # SI HAY PRODUCTOS
    # ──────────────────────────────────────────────────────────────────────────────────
    stock_var = []
    # Una sola vez, fuera del loop


    validar = frame_tabla.register(module.solo_numeros)

    for index,producto in enumerate(productos):
        row+=2

        def color_por_stock(stock):
            if stock == 0:
                return "#FEE2E2"   # rojo
            elif stock <= 5:
                return "#FFEDD5"   # naranja
            elif stock <= 10:
                return "#FEF9C3"   # amarillo
            else:
                return bg_row_par if index % 2 == 0 else bg_row_imp
            
        bg_row = color_por_stock(int(producto["stock"]))


        # ── LINEA ──
        linea = tkinter.Frame(frame_tabla,background="#AFC8E7",height=2)
        linea.grid(row=row+1,column=0,columnspan=3,sticky="we")

        # ── NOMBRE PRODUCTO ──
        nombre_producto = tkinter.Label(
            frame_tabla,
            text=producto["producto"],
            font=FONT_BODY,
            foreground=color_texto,
            background=bg_row,
        )
        nombre_producto.grid(row=row,column=0,sticky="nswe")

        # ── PRECIO ──
        default2 = tkinter.StringVar(value=producto["costo"])
        precio = tkinter.Entry(
            frame_tabla,
            textvariable=default2,
            font=FONT_BODY,
            foreground=color_texto,
            background=bg_row,
            width=7,
            validate="key",
            validatecommand=(validar, "%P")
        )
        precio.grid(row=row,column=1,sticky="nswe")

        # ── STCOK ──
        default = tkinter.StringVar(value=producto["stock"])
        stock = tkinter.Entry(
            frame_tabla,
            textvariable=default,
            font=FONT_BODY,
            foreground=color_texto,
            background=bg_row,
            width=7,
            validate="key",
            validatecommand=(validar, "%P")
        )

        stock_var.append((producto["producto"],default,default2))

        stock.grid(row=row,column=2,sticky="nswe")
    

    #  ──────── BOTONES GUARDADO ────────

    # //// FUNCIONES \\\\\
    def obtener_stock():
        return [
            {"producto": nombre, "stock": int(var.get()),"costo":int(cst.get())}
            for nombre, var,cst in stock_var
        ]



    def guardar_producto():
        datos = obtener_stock()
        for index,producto in enumerate(productos):
            saltar = False
            for actualizacion in datos:
                if actualizacion["producto"] == producto["producto"]:
                    productos[index]["stock"] = actualizacion["stock"]
                    productos[index]["costo"] = actualizacion["costo"]
                    saltar = True
            if saltar:
                continue    
        module.actualizar_productos(productos)

        msg.config(text="Cambio guardado exitosamente!",font=("Segoe UI", 15))
        window.after(2000, refrescar_stock)


        


    boton_guardar_stock = tkinter.Button(
        frame_botones_inferior,
        text="🧧  Guardar",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_stock,
        activebackground=btn_stock_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command= guardar_producto
    )
    boton_guardar_stock.pack(pady=8)



def mostrar_stock(window,ir_a_historial,ir_a_punto_de_venta):

    window.geometry("1225x700")
    window.minsize(1000, 500)
    window.title("Historial de Ventas")
    window.config(background=bg_main)

    creacion(window,ir_a_historial,ir_a_punto_de_venta)

