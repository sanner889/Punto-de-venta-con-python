# 🛒 Sistema de Punto de Venta  en Python con Tkinter

Este proyecto consiste en el desarrollo de una aplicación de escritorio que simula un sistema de punto de venta , diseñada utilizando el módulo gráfico Tkinter de Python. Su propósito principal es facilitar la gestión básica de ventas en un entorno tipo tienda, permitiendo al usuario seleccionar productos, calcular costos automáticamente, registrar pagos y almacenar la información de cada transacción en archivos estructurados.

La aplicación está pensada como una solución sencilla pero funcional, ideal para fines educativos, prácticas de programación o como base para proyectos más avanzados en gestión comercial.

El sistema cuenta con una interfaz gráfica intuitiva en la que el usuario puede interactuar fácilmente mediante listas desplegables, campos de entrada y botones. A través de esta interfaz, es posible agregar múltiples productos a una venta, indicar la cantidad de cada uno, visualizar el costo individual y el costo total por producto, y obtener el total general de la compra en tiempo real.

Uno de los aspectos más importantes del sistema es su capacidad para calcular automáticamente los valores monetarios. Cada vez que se selecciona un producto o se modifica la cantidad, el sistema actualiza de inmediato el costo correspondiente, así como el total general de la compra. Además, incluye una funcionalidad para ingresar el dinero con el que paga el cliente, calculando automáticamente el cambio (devueltas) o indicando si el pago es insuficiente.

El sistema también permite gestionar dinámicamente los productos dentro de la venta. El usuario puede agregar nuevas filas para incluir más productos, eliminar filas específicas o limpiar completamente la información de la venta actual. Esto brinda flexibilidad y control sobre cada transacción realizada.

En cuanto al almacenamiento de datos, la aplicación guarda cada venta en dos formatos diferentes: un archivo JSON y un archivo Excel. El archivo JSON permite mantener un registro estructurado de todas las ventas realizadas, mientras que el archivo Excel facilita la visualización y análisis de los datos en herramientas externas. Cada venta registrada incluye información como un identificador único, la lista de productos con sus cantidades, el total de la compra, el valor pagado por el cliente, el cambio entregado y la fecha y hora exacta de la transacción.

El proyecto está organizado en dos archivos principales. El archivo `venta.py` contiene toda la lógica relacionada con la interfaz gráfica, incluyendo la creación de la ventana, los componentes visuales y la interacción con el usuario. Por otro lado, el archivo `module.py` se encarga de la lógica interna del sistema, como los cálculos matemáticos, el formateo de precios, la validación de datos y el proceso de guardado de las ventas.

Para su funcionamiento, el sistema requiere Python 3 y la librería pandas, la cual se utiliza para la generación y manipulación del archivo Excel. Tkinter no requiere instalación adicional, ya que viene incluido con Python en la mayoría de los casos.

La ejecución del programa es sencilla: basta con ejecutar el archivo principal `venta.py`, lo que abrirá la interfaz gráfica del sistema y permitirá comenzar a registrar ventas de inmediato.

El sistema incluye diversas validaciones para garantizar el correcto funcionamiento. Por ejemplo, evita registrar ventas sin productos, verifica que el valor ingresado como pago sea válido y controla situaciones en las que el dinero recibido no es suficiente para cubrir el total de la compra.

Además, el diseño del proyecto permite una fácil personalización. Es posible modificar la lista de productos disponibles, ajustar los colores de la interfaz, cambiar las fuentes o adaptar la estructura general del sistema según las necesidades del usuario.

En términos generales, este proyecto representa una implementación práctica de conceptos clave en programación con Python, como el uso de interfaces gráficas, manejo de eventos, estructuras de datos, validación de entradas y almacenamiento de información. También sirve como una base sólida para futuras mejoras, como la integración con bases de datos, la implementación de reportes avanzados, la gestión de usuarios o la generación de facturas.

En conclusión, este sistema de punto de venta es una herramienta funcional y extensible que demuestra cómo se pueden combinar diferentes tecnologías de Python para construir aplicaciones útiles en contextos reales.
