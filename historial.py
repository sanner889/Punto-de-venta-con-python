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
btn_color  = "#3B82F6"
btn_pressed= "#2563EB"
btn_stock    = "#16A34A"
btn_stock_pressed = "#15803D"
color_titulo    = "#FFFFFF"
color_subtitulo = "#94A3B8"
color_texto     = "#1E293B"
color_header_col= "#334155"
bg_footer  = "#1E293B"
error = "#b50d0d"

FONT_TITULO    = ("Segoe UI", 32, "bold")
FONT_SUBTITULO = ("Segoe UI", 18)
FONT_HEADER    = ("Segoe UI", 18, "bold")
FONT_COL       = ("Segoe UI", 11, "bold")
FONT_BODY      = ("Segoe UI", 12)
FONT_TOTAL     = ("Segoe UI", 13, "bold")
FONT_BTN       = ("Segoe UI", 11, "bold")
FONT_FOOTER    = ("Segoe UI", 12, "bold")
FONT_PAG       = ("Segoe UI", 10, "bold")

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTE DE PAGINACIÓN — cambiar aquí si se quiere otro tamaño de página
# ─────────────────────────────────────────────────────────────────────────────
VENTAS_POR_PAGINA = 20


def mostrar_historial(window, ir_a_punto_de_venta, ir_a_stock):
    window.geometry("1225x700")
    window.minsize(1000, 500)
    window.title("Historial de Ventas")
    window.config(background=bg_main)

    frame = tkinter.Frame(window, background=bg_header)
    frame.pack(fill="x")

    # ─────────────────────────────────────────────────────────────────────────
    # VARIABLES
    # ─────────────────────────────────────────────────────────────────────────

    registro = module.registro_de_ventas()
    total_recaudad = 0
    for venta in registro:
        try:
            numero = venta["Total"].replace("$ ", "").replace(".", "")
            total_recaudad += int(numero)
        except Exception:
            pass

    # variables de paginación.
    # El registro se invierte para que la página 1 muestre las ventas más recientes.
    registro_invertido = list(reversed(registro))
    total_ventas       = len(registro_invertido)
    total_paginas      = max(1, -(-total_ventas // VENTAS_POR_PAGINA))  # ceil sin math
    pagina_actual      = tkinter.IntVar(value=1)

    # ─────────────────────────────────────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────────────────────────────────────

    titulo = tkinter.Label(
        frame,
        text="HISTORIAL DE VENTA",
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
    titulo.pack(pady=(20, 0))
    subtitulo.pack()

    msg_error = tkinter.Label(
        frame,
        text="",
        font=("Arial", 1),
        foreground=error,
        background=bg_header
    )
    msg_error.pack()

    # ── Botones de acción (sin cambios funcionales)
    frame_botones = tkinter.Frame(frame, background=bg_header)
    frame_botones.pack(pady=8)

    boton_graficas = tkinter.Button(
        frame_botones,
        text="📊  Ver Gráficas",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_color,
        activebackground=btn_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda: module.mostrar_graficas(registro)
    )
    boton_graficas.pack(padx=8, side="left")

    boton_excel = tkinter.Button(
        frame_botones,
        text="🗃️  Exportar Excel",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background=btn_stock,
        activebackground=btn_stock_pressed,
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda: module.exportar_excel(msg_error)
    )
    boton_excel.pack(padx=8, side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # CONTENEDOR CON SCROLL — sin cambios
    # ─────────────────────────────────────────────────────────────────────────

    container = tkinter.Frame(window, background=bg_main)
    container.pack(fill="both", expand=True)

    canvas = tkinter.Canvas(container, background=bg_table, highlightthickness=0)
    scrollbar = tkinter.Scrollbar(container, orient="vertical", command=canvas.yview)

    frame_tabla = tkinter.Frame(canvas, background=bg_table)
    canvas.create_window((0, 0), window=frame_tabla, anchor="nw")

    def configurar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(1, width=canvas.winfo_width())

    frame_tabla.bind("<Configure>", configurar_scroll)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ─────────────────────────────────────────────────────────────────────────
    # COLUMNAS — sin cambios
    # ─────────────────────────────────────────────────────────────────────────

    columnas = ["ID", "PRODUCTOS", "CANTIDAD", "TOTAL", "PAGADO", "DEVUELTAS", "FECHA"]
    pesos    = [1,    3,           1,           2,       2,         2,           3]

    for i, peso in enumerate(pesos):
        frame_tabla.columnconfigure(i, weight=peso, minsize=80)

    # Encabezados: se dibujan UNA sola vez y se mantienen en row=0 siempre.
    # dibujar_pagina() solo borra filas con row > 0, así que nunca los toca.
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

    # ─────────────────────────────────────────────────────────────────────────
    # FOOTER — se construye ANTES de dibujar_pagina para que boton_anterior
    # y boton_siguiente ya existan cuando la función intente actualizarlos.
    # ─────────────────────────────────────────────────────────────────────────

    footer = tkinter.Frame(window, background=bg_footer, pady=10)
    footer.pack(side="bottom", fill="x")

    # ── Izquierda: total de ventas
    total_de_ventas = tkinter.Label(
        footer,
        text=f"🧾 Total de ventas: {len(registro)}",
        font=FONT_FOOTER,
        foreground="#94A3B8",
        background=bg_footer
    )
    total_de_ventas.pack(padx=20, side="left")

    # ── Centro-izquierda: botones de navegación entre vistas 
    boton_punto_venta = tkinter.Button(
        footer,
        text="🛒  Punto de Venta",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background="#334155",
        activebackground="#475569",
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=ir_a_punto_de_venta,
    )
    boton_punto_venta.pack(pady=(0, 12), side="left", expand=True)

    boton_volver_stock = tkinter.Button(
        footer,
        text="📦  Ver Stock",
        font=FONT_BTN,
        foreground="#FFFFFF",
        background="#334155",
        activebackground="#475569",
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=lambda: module.ventana_contraseña(ir_a_stock),
    )
    boton_volver_stock.pack(pady=(0, 12), side="left", expand=True)



    # CAMBIO 3 — controles de paginación en el footer.
    # Frame propio para mantenerlos agrupados y centrados entre los botones
    # de navegación y el label de total recaudado.
    frame_paginacion = tkinter.Frame(footer, background=bg_footer)
    frame_paginacion.pack(side="left", expand=True)

    boton_anterior = tkinter.Button(
        frame_paginacion,
        text="◀",
        font=FONT_PAG,
        foreground="#FFFFFF",
        background="#334155",
        activebackground="#475569",
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        width=3,
        command=lambda: dibujar_pagina(pagina_actual.get() - 1)
    )
    boton_anterior.pack(side="left", padx=(0, 4))

    # Spinbox con validación de tecla — solo acepta dígitos.
    # Sin esto, escribir una letra lanza TclError al hacer pagina_actual.get().
    def _solo_numeros(valor):
        return valor.isdigit() or valor == ""

    validar_numero = frame_paginacion.register(_solo_numeros)

    spinbox_pagina = tkinter.Spinbox(
        frame_paginacion,
        from_=1,
        to=max(1, total_paginas),
        width=3,
        font=FONT_PAG,
        foreground=color_texto,
        relief="flat",
        justify="center",
        textvariable=pagina_actual,
        validate="key",
        validatecommand=(validar_numero, "%P"),
        command=lambda: dibujar_pagina(pagina_actual.get())
    )
    spinbox_pagina.pack(side="left", padx=4)

    # Navegar también al presionar Enter o al perder el foco (clic en otro lado)
    def _ir_desde_spinbox(event=None):
        texto = spinbox_pagina.get()
        if texto.isdigit():
            dibujar_pagina(int(texto))
        else:
            pagina_actual.set(pagina_actual.get())  # restaurar valor válido

    spinbox_pagina.bind("<Return>",   _ir_desde_spinbox)
    spinbox_pagina.bind("<FocusOut>", _ir_desde_spinbox)

    tkinter.Label(
        frame_paginacion,
        text=f"/ {total_paginas}",
        font=FONT_PAG,
        foreground="#94A3B8",
        background=bg_footer
    ).pack(side="left", padx=(0, 4))

    boton_siguiente = tkinter.Button(
        frame_paginacion,
        text="▶",
        font=FONT_PAG,
        foreground="#FFFFFF",
        background="#334155",
        activebackground="#475569",
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        width=3,
        command=lambda: dibujar_pagina(pagina_actual.get() + 1)
    )
    boton_siguiente.pack(side="left", padx=(4, 0))

    # ── Derecha: total recaudado (sin cambios)
    recaudado = tkinter.Label(
        footer,
        text=f"💰  Total recaudado: {module.puntos_de_mil(total_recaudad)}",
        font=FONT_FOOTER,
        foreground="#4ADE80",
        background=bg_footer
    )
    recaudado.pack(padx=20, side="right")

    # ─────────────────────────────────────────────────────────────────────────
    # _actualizar_botones — definida ANTES de dibujar_pagina para evitar
    # cualquier riesgo de NameError en el momento de la llamada.
    # ─────────────────────────────────────────────────────────────────────────

    def _actualizar_botones():
        """Deshabilita ◀ en la página 1 y ▶ en la última."""
        pagina = pagina_actual.get()
        boton_anterior.config(state="disabled" if pagina <= 1            else "normal")
        boton_siguiente.config(state="disabled" if pagina >= total_paginas else "normal")

    # ─────────────────────────────────────────────────────────────────────────
    # CAMBIO 4 — dibujar_pagina reemplaza el for fijo original.
    # Toda la lógica de renderizado de filas vive aquí; se llama al inicio
    # y cada vez que el usuario cambia de página.
    # ─────────────────────────────────────────────────────────────────────────

    def dibujar_pagina(pagina):
        """Limpia la tabla y dibuja las ventas de la página indicada."""

        # Captura segura: pagina_actual.get() puede lanzar TclError si el
        # Spinbox quedó vacío o con texto no entero.
        try:
            pagina = int(pagina)
        except (ValueError, tkinter.TclError):
            msg_error.config(
                text="⚠️  Ingresa un número de página válido.",
                font=("Segoe UI", 11)
            )
            return

        # Validar rango
        if pagina < 1 or pagina > total_paginas:
            msg_error.config(
                text=f"⚠️  Página {pagina} no existe. Hay {total_paginas} página(s).",
                font=("Segoe UI", 11)
            )
            return

        msg_error.config(text="", font=("Arial", 1))
        pagina_actual.set(pagina)

        # Borrar todas las filas anteriores manteniendo los encabezados (row=0)
        for widget in frame_tabla.winfo_children():
            info = widget.grid_info()
            if info and int(info["row"]) > 0:
                widget.destroy()

        # Slice de la página: página 1 → [0:20], página 2 → [20:40], etc.
        inicio        = (pagina - 1) * VENTAS_POR_PAGINA
        fin           = inicio + VENTAS_POR_PAGINA
        ventas_pagina = registro_invertido[inicio:fin]

        # Sin ventas en absoluto
        if not ventas_pagina:
            tkinter.Label(
                frame_tabla,
                text="NO HAY VENTAS REGISTRADAS",
                font=FONT_SUBTITULO,
                foreground=bg_header,
                background=bg_table,
                pady=30
            ).grid(row=2, column=0, columnspan=7)
            _actualizar_botones()
            canvas.yview_moveto(0)
            return

        # Dibujar filas
        row = 0
        for index, venta in enumerate(ventas_pagina):
            row += 2
            background_fila = bg_row_par if index % 2 == 0 else bg_row_imp

            # Línea separadora
            tkinter.Frame(
                frame_tabla, height=2, background="#AFC8E7"
            ).grid(row=row + 1, column=0, columnspan=7, sticky="we")

            # ── ID
            ID_venta = tkinter.Label(
                frame_tabla,
                text=str(venta["id"]),
                foreground=color_texto,
                font=FONT_HEADER,
                background=background_fila,
                anchor="center"
            )

            # ── PRODUCTOS
            texto = "\n\n".join(p["producto"] for p in venta["producto"])
            productos = tkinter.Label(
                frame_tabla,
                text=texto,
                foreground=color_texto,
                font=FONT_BODY,
                background=background_fila,
                anchor="w",
                justify="left"
            )

            # ── CANTIDADES
            cantidad_txt = "\n\n".join(str(p["cantidad"]) for p in venta["producto"])
            cantidades = tkinter.Label(
                frame_tabla,
                text=cantidad_txt,
                foreground=color_texto,
                font=FONT_BODY,
                background=background_fila,
            )

            # ── TOTAL
            total = tkinter.Label(
                frame_tabla,
                text=venta["Total"],
                foreground=color_texto,
                font=FONT_BODY,
                background=background_fila,
                anchor="center"
            )

            # ── PAGADO
            pagado = tkinter.Label(
                frame_tabla,
                text=module.puntos_de_mil(venta["pagado"]),
                foreground=color_texto,
                font=FONT_BODY,
                background=background_fila
            )

            # ── DEVUELTAS
            devueltas = tkinter.Label(
                frame_tabla,
                text=module.puntos_de_mil(venta["devueltas"]),
                foreground=color_texto,
                font=FONT_BODY,
                background=background_fila,
                anchor="center"
            )

            # ── FECHA
            fecha = tkinter.Label(
                frame_tabla,
                text=venta["fecha"],
                foreground=color_texto,
                font=FONT_BODY,
                background=background_fila,
                anchor="center"
            )

            # ── Grid
            ID_venta.grid(column=0,   row=row, pady=10, sticky="nswe")
            productos.grid(row=row,   column=1, pady=10, sticky="nsew")
            cantidades.grid(column=2, row=row,  pady=10, sticky="nswe")
            total.grid(column=3,      row=row,  pady=10, sticky="nswe")
            pagado.grid(column=4,     row=row,  pady=10, sticky="nswe")
            devueltas.grid(column=5,  row=row,  pady=10, sticky="nswe")
            fecha.grid(column=6,      row=row,  pady=10, sticky="nswe")

        _actualizar_botones()
        canvas.yview_moveto(0)   # resetear scroll al tope al cambiar página

    # ── Arrancar en la página 1
    dibujar_pagina(1)

    window.mainloop()