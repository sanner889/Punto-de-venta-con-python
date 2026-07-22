import tkinter
from tkinter import ttk
import module

row = 0




black_color = "#1A1F71"
bg_main  = "#D1D4D9"
bg_header = "#1E293B"
color_header_col= "#334155"
bg_table = "#E6ECF1"
bg_total = "#F3F4F6"
bg_footer  = "#1E293B"

btn_color = "#3B82F6"
btn_pressed = "#2563EB"
btn_delete = "#EF4444"
btn_delete_pressed = "#DC2626"
btn_stock = "#f59622"
btn_stock_pressed = "#ff7514"
color_titulo   = "#FFFFFF"
color_subtitulo= "#94A3B8"
btn_success= "#16A34A"
btn_press_success = "#15803D"
color_subtitulo= "#94A3B8"
color_texto    = "#1E293B"


color_pago = "#c4dafa"
texto_pago = "#005187"

FONT_TITULO    = ("Segoe UI", 32, "bold")
FONT_SUBTITULO = ("Segoe UI", 18)
FONT_COL       = ("Segoe UI", 18, "bold")
FONT_BODY      = ("Segoe UI", 12)
FONT_TOTAL     = ("Segoe UI", 13, "bold")
FONT_BTN       = ("Segoe UI", 11, "bold")




def frame_final(window,ir_a_historial,ir_a_stock):
    productos = module.cargar_productos()
    productos_ordenados = sorted(productos,key=lambda p: p["producto"].lower())


    window.geometry("1000x750")
    window.minsize(1000, 650)
    window.title("Control de Ventas")
    window.config(background=bg_footer)


    nombres = [item["producto"] for item in productos_ordenados]
    cantidad = [str(n) for n in range(1,100)]
    filas = []

    frame = tkinter.Frame(window,background=bg_header)
    frame.pack(fill="x")
    # ──────────────────────────────────────────────────────────────────────────────────
    # CONTENEDOR CON SCROLL (SOLUCIÓN AL CRECIMIENTO INFINITO) # HECHO CON AYUDA DE IA
    # ──────────────────────────────────────────────────────────────────────────────────

    container = tkinter.Frame(window,background=bg_main)
    container.pack(fill="both",expand=True)

    canvas = tkinter.Canvas(container,background=bg_table,highlightthickness=0)
    scrollbar = tkinter.Scrollbar(container,orient="vertical",command=canvas.yview) #yview enlaza canvas con scrollbar

    frame_tabla = tkinter.Frame(canvas, background=bg_table)

    # Crear ventana dentro del canvas
    canvas.create_window((0,0),window=frame_tabla,anchor="nw")

    # Ajustar scroll automáticamente
    def configurar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame_tabla.bind("<Configure>", configurar_scroll)

    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        first, last = canvas.yview()

        # Si está arriba y el usuario intenta seguir subiendo
        if first <= 0 and event.delta > 0:
            return

        # Si está abajo y el usuario intenta seguir bajando
        if last >= 1 and event.delta < 0:
            return

        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # // EL RESTO NO FUE HECHO CON IA

    # // TITULO PRINCIPAL //

    titulo = tkinter.Label(
        frame,
        text="PUNTO DE VENTA",
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

    # ─────────────────────────────────────────────────────────────────────────────
    # TABLAS DE PRODUCTOS
    # ─────────────────────────────────────────────────────────────────────────────

    # TITULOS

    # ─────────────────────────────────────────────────────────────────────────
    # COLUMNAS — sin cambios
    # ─────────────────────────────────────────────────────────────────────────

    # EL PESO NO ESTA BIEN CONFIGURADO (ES EL COPIA Y PEGA DEL DE HISTORIAL)
    # PERO AHI FUNCIONA PERFECTAMENTE
    columnas = ["PRODUCTO", "# DE PRODUCTOS", "COSTO INDIVIDUAL", "COSTO TOTAL", "     "]
    pesos    = [1,    3,           1,           2,       2,         2,           3]

    for i, peso in enumerate(pesos):
        frame_tabla.columnconfigure(i, weight=peso, minsize=80)

    for posicion, columna in enumerate(columnas):
        encabezado = tkinter.Label(
            frame_tabla,
            text=columna,
            font=FONT_COL,
            foreground="#FFFFFF",
            background=color_header_col,
            padx=12, pady=10
        )
        encabezado.grid(row=0, column=posicion, sticky="we")


    # ─────────────────────────────────────────────────────────────────────────────
    # CREACION DE VALORES DEFECTO
    # ─────────────────────────────────────────────────────────────────────────────

    generar_total = tkinter.Label(
        frame_tabla,
        text="TOTAL: ",
        font=("Arial",15),
        foreground= black_color
    )

    precio_total_de_todo = tkinter.Label(
        frame_tabla,
        text="$ 0",
        font=("Arial",15),
        foreground= texto_pago,
        background=color_pago
    )

    boton_crear_fila = tkinter.Button(
        frame_tabla,
        text="+ Crear Fila",
        font=("Arial",15),
        foreground="white",
        background=btn_color,
        activebackground=btn_pressed,
        activeforeground="white",
        borderwidth=5,
        command= lambda: crear_fila_completa()
    )

    boton_eliminar_fila = tkinter.Button(
        frame_tabla,
        text="X Eliminar datos",
        font=("Arial",15),
        foreground="white",
        background=btn_delete,
        activebackground=btn_delete_pressed,
        activeforeground="white",
        borderwidth=5,
        command= lambda: module.eliminar_datos_todo(filas,precio_total_de_todo,devueltas_total_de_todo,ingresado,precio_total_de_todo)
    )

    ingresado_label = tkinter.Label(
        frame_tabla,
        text="PAGA CON: ",
        font=("Arial",15),
        foreground= black_color
    )
    ingresado = tkinter.Entry(
        frame_tabla,
        font=("Arial",15),
        foreground= black_color,
        borderwidth=5
    )

    devueltas_label = tkinter.Label(
        frame_tabla,
        text="DEVUELTAS: ",
        font=("Arial",15),
        foreground= black_color
    )

    devueltas_total_de_todo = tkinter.Label(
        frame_tabla,
        text="$ 0",
        font=("Arial",15),
        foreground= texto_pago,
        background=color_pago
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # BORRAR FILA COMPLETAMENTE Y REUBICAR LAS DEMAS
    # ─────────────────────────────────────────────────────────────────────────────

    def borrar_fila(fila, filas, label_text):
        global row



        if row >2:
            # // Eliminar widgets //
            for widget in fila.values():
                widget.destroy()
            filas.remove(fila)
            row -=1

            # // RE ubicar filas
            for i,f in enumerate(filas):
                new_row = i +1
                f["producto"].grid(row=new_row,column=0,pady=10)
                f["cantidad"].grid(row=new_row,column=1,pady=10)
                f["precio"].grid(row=new_row,column=2)
                f["total"].grid(row=new_row,column=3)
                f["boton"].grid(row=new_row,column=4)
            
            # // RE UBICAR EXTRAS

            generar_total.grid(row=row +1,column=2,pady=10)
            precio_total_de_todo.grid(row=row +1,column=3,pady=10)
            boton_crear_fila.grid(row=row+1,column=0,pady=10)
            boton_eliminar_fila.grid(row=row+1,column=1,pady=10)

            ingresado_label.grid(row=row+2,column=2,pady=10)
            ingresado.grid(row=row+2,column=3,pady=10)
            devueltas_label.grid(row=row+3,column=2,pady=10)
            devueltas_total_de_todo.grid(row=row+3,column=3,pady=10)
            module.actualizar_total_general(filas, label_text)
            module.obtener_devueltas(precio_total_de_todo,ingresado,devueltas_total_de_todo)
            




    # ─────────────────────────────────────────────────────────────────────────────
    # CREAR UNA FILA
    # ─────────────────────────────────────────────────────────────────────────────

    def crear_fila_completa():
        global row
        row+=1

        

        # /////////////////////////////////////////////////////////////////////////////
        # LISTA DE PRODUCTOS
        # /////////////////////////////////////////////////////////////////////////////
        var = tkinter.StringVar()
        lista_productos = ttk.Combobox(frame_tabla,values=nombres,textvariable=var,width=28)

        def filtrar_productos(event):
            text = var.get().upper()
            filtrado = [p for p in nombres if text in p.upper()]
            lista_productos["values"] = filtrado
        lista_productos.bind("<KeyRelease>",filtrar_productos)

        lista_productos.grid(row=row,column=0,pady=10,padx=(10,0))

        # /////////////////////////////////////////////////////////////////////////////
        # CANTIDAD DE PRODUCTOS
        # /////////////////////////////////////////////////////////////////////////////

        var2 = tkinter.StringVar()
        cantidad_de_productos = ttk.Combobox(frame_tabla,values=cantidad,textvariable=var2)
        cantidad_de_productos.grid(row=row,column=1,pady=10)

        cantidad_de_productos.current(0)


        # /////////////////////////////////////////////////////////////////////////////
        # COSTO INDIVIDUAL
        # /////////////////////////////////////////////////////////////////////////////
        precio_individual = tkinter.Label(
            frame_tabla,
            text=f"$ 0",
            relief="solid",
            font=("Arial",14),
            borderwidth=2 
        )

        # /////////////////////////////////////////////////////////////////////////////
        # COSTO TOTAL
        # /////////////////////////////////////////////////////////////////////////////
        costo_total = tkinter.Label(
            frame_tabla,
            text=f"$ 0",
            relief="solid",
            font=("Arial",14),
            borderwidth=2 
        )

        precio_individual.grid(row=row,column=2)
        costo_total.grid(row=row,column=3)

        # /////////////////////////////////////////////////////////////////////////////
        # FUNCIONES ACTUALIZAR TOTAL
        # /////////////////////////////////////////////////////////////////////////////

        def poner_precio(event):
            producto = lista_productos.get()
            precio = [p["costo"] for p in productos if p["producto"] == producto]
            if precio:
                precio_unitario = str(precio[0])
                precio_individual["text"] = module.puntos_de_mil(precio_unitario)

                # // COSTO TOTAL
                module.calcular_total(int(precio_unitario),cantidad_de_productos,costo_total)
            module.actualizar_total_general(filas,precio_total_de_todo)
            module.obtener_devueltas(precio_total_de_todo,ingresado,devueltas_total_de_todo)

        # AL SOLTAR PRODUCTO
        lista_productos.bind("<<ComboboxSelected>>",poner_precio)

        def total_cambio_cantidad(event):
            producto = lista_productos.get()
            precio = [p["costo"] for p in productos if p["producto"] == producto]

            if precio:
                precio_unitario = str(precio[0])
                module.calcular_total(int(precio_unitario),cantidad_de_productos,costo_total)
            module.actualizar_total_general(filas,precio_total_de_todo)
            module.obtener_devueltas(precio_total_de_todo,ingresado,devueltas_total_de_todo)

        # AL SOLTAR CANTIDAD
        cantidad_de_productos.bind("<<ComboboxSelected>>",total_cambio_cantidad)
        cantidad_de_productos.bind("<KeyRelease>",total_cambio_cantidad)

        def Devueltas(event):
            module.obtener_devueltas(precio_total_de_todo,ingresado,devueltas_total_de_todo)

        ingresado.bind("<KeyRelease>",Devueltas)

        # /////////////////////////////////////////////////////////////////////////////
        # ELIMINAR FILA DE DATOS
        # /////////////////////////////////////////////////////////////////////////////
        boton_eliminar = tkinter.Button(
            frame_tabla,
            text="❌",
            font=("Arial",15),
            background=btn_delete,
            foreground="white",
            activebackground=btn_delete_pressed,
            activeforeground="white",
            borderwidth=3,
            command= lambda: borrar_fila(fila_info,filas,precio_total_de_todo)
        ) 
        boton_eliminar.grid(row=row,column=4)

        # /////////////////////////////////////////////////////////////////////////////
        # GUARDAR FILAS — boton incluido para poder destruirlo y re-grillarlo
        # /////////////////////////////////////////////////////////////////////////////
        fila_info = {
            "producto": lista_productos,
            "cantidad": cantidad_de_productos,
            "precio": precio_individual,
            "total": costo_total,
            "boton": boton_eliminar,
        }

        filas.append(fila_info)



        # /////////////////////////////////////////////////////////////////////////////
        # DESEMPAQUE BOTONES Y PARTES DEL FONDO
        # /////////////////////////////////////////////////////////////////////////////

        generar_total.grid(row=row +1,column=2,pady=10)
        precio_total_de_todo.grid(row=row +1,column=3,pady=10)
        boton_crear_fila.grid(row=row+1,column=0,pady=10)
        boton_eliminar_fila.grid(row=row+1,column=1,pady=10)
        ingresado_label.grid(row=row+2,column=2,pady=10)
        ingresado.grid(row=row+2,column=3,pady=10)
        devueltas_label.grid(row=row+3,column=2,pady=10)
        devueltas_total_de_todo.grid(row=row+3,column=3,pady=10)

    frame_extra =tkinter.Frame(window,background=bg_footer)

    mensaje_exito = tkinter.Label(
        frame_extra,
        text="",
        font=("Arial",15),
        foreground= btn_delete_pressed,
        background=bg_footer
    )


    boton_historial = tkinter.Button(
        frame_extra,
        text="📋  Ver Historial",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_color,
        activebackground=btn_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        padx=16, pady=6,
        cursor="hand2",
        command=lambda: module.ventana_contraseña(ir_a_historial)
    )
    boton_historial.grid(row=2,column=0,pady=(6, 12),padx=5)

    boton_stock = tkinter.Button(
        frame_extra,
        text="📦  Ver Stock",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_stock,
        activebackground=btn_stock_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        padx=16, pady=6,
        cursor="hand2",
        command=lambda: module.ventana_contraseña(ir_a_stock)
    )
    boton_stock.grid(row=2,column=1,pady=(6,12),padx=5)

    boton_registrar_venta = tkinter.Button(
        frame_extra,
        text="✔ Registrar venta",
        font=("Arial",16),
        background=btn_success,
        foreground="white",
        border=10,
        activebackground=btn_press_success,
        activeforeground="white",
        command= lambda: module.guardar_venta(precio_total_de_todo,filas,mensaje_exito,devueltas_total_de_todo,ingresado,precio_total_de_todo)
    )




    # ─────────────────────────────────────────────────────────────────────────────
    # DESEMPACAR LOS ATRIBUTOS
    # ─────────────────────────────────────────────────────────────────────────────



    frame_extra.pack(pady=10)
    titulo.pack()
    subtitulo.pack()
    mensaje_exito.grid(row=0,column=0,columnspan=2)
    boton_registrar_venta.grid(row=1,pady=(10,0),column=0,columnspan=2)

    for i in range(5):
        crear_fila_completa()

