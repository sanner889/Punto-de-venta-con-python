import tkinter
import punto_de_venta
import historial
import stock

bg_main = "#D1D4D9"

window = tkinter.Tk()



def ir_a_historial():
    for widget in window.winfo_children():
        widget.destroy()
    historial.mostrar_historial(window,ir_a_punto_de_venta,ir_a_stock)

def ir_a_punto_de_venta():
    for widget in window.winfo_children():
        widget.destroy()
    punto_de_venta.row = 0
    punto_de_venta.frame_final(window,ir_a_historial,ir_a_stock)

def ir_a_stock():
    for widget in window.winfo_children():
        widget.destroy()
    stock.mostrar_stock(window,ir_a_historial,ir_a_punto_de_venta)

# Arrancar en punto de venta
punto_de_venta.frame_final(window, ir_a_historial,ir_a_stock)


window.mainloop()