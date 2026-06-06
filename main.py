import os
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image
from reportlab.lib.units import cm
import datetime

CLIENTES_FILE = "clientes.txt"
SERVICIOS_PC_FILE = "servicios_pc.txt"
SERVICIOS_CEL_FILE = "servicios_cel.txt"
TRABAJOS_FILE = "trabajos.txt"

# Funciones de guardado
def guardar_cliente(nombre, telefono, email):
    if not nombre or not telefono or not email:
        messagebox.showwarning("Error", "Completa todos los campos.")
        return
    with open(CLIENTES_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nombre};{telefono};{email}\n")
    messagebox.showinfo("Éxito", "Cliente registrado correctamente.")

def guardar_servicio_cel(nombre, precio):
    if not nombre or not precio:
        messagebox.showwarning("Error", "Completa todos los campos.")
        return
    try:
        precio = float(precio)
    except ValueError:
        messagebox.showwarning("Error", "El precio debe ser un número.")
        return
    with open(SERVICIOS_CEL_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nombre};{precio}\n")
    messagebox.showinfo("Éxito", "Servicio de celular registrado correctamente.")

def ventana_servicios_cel():
    win = tb.Toplevel(root)
    win.title("Registrar Servicio Celular")
    centrar_ventana(win, 400, 200)

    frame = tb.Frame(win)
    frame.pack(expand=True)

    tb.Label(frame, text="Nombre del servicio (Celular):").grid(row=0, column=0, pady=10, padx=10, sticky="e")
    tb.Label(frame, text="Precio:").grid(row=1, column=0, pady=10, padx=10, sticky="e")

    nombre = tb.Entry(frame, width=30)
    precio = tb.Entry(frame, width=30)

    nombre.grid(row=0, column=1, pady=10, padx=10)
    precio.grid(row=1, column=1, pady=10, padx=10)

    nombre.focus_set()

    def guardar_y_cerrar():
        guardar_servicio_cel(nombre.get(), precio.get())
        win.destroy()

    tb.Button(frame, text="Guardar", bootstyle="success", command=guardar_y_cerrar)\
        .grid(row=2, columnspan=2, pady=20)
    precio.bind("<Return>", lambda event: guardar_y_cerrar())

def mostrar_servicios_cel():
    win = tb.Toplevel(root)
    win.title("Lista de Servicios Celulares")
    centrar_ventana(win, 650, 400)

    tree = ttk.Treeview(win, columns=("Servicio", "Precio"), show="headings", height=15)
    tree.pack(fill="both", expand=True)

    tree.heading("Servicio", text="Servicio")
    tree.heading("Precio", text="Precio")

    tree.column("Servicio", anchor="center", width=450)
    tree.column("Precio", anchor="center", width=150)

    try:
        with open(SERVICIOS_CEL_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 2:
                    nombre, precio = partes
                    tree.insert("", "end", values=(nombre, f"${precio}"))
    except FileNotFoundError:
        tree.insert("", "end", values=("No hay servicios registrados aún", ""))

    # Botón eliminar
    def eliminar_servicio_cel():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Selecciona un servicio para eliminar.", parent=win)
            return
        valores = tree.item(seleccion[0], "values")
        nombre, precio = valores
        precio = precio.replace("$", "")

        confirmar = messagebox.askyesno("Confirmar eliminación",
                                        f"¿Seguro que deseas eliminar el servicio:\n{nombre}?",
                                        parent=win)
        if not confirmar:
            return

        with open(SERVICIOS_CEL_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        with open(SERVICIOS_CEL_FILE, "w", encoding="utf-8") as f:
            for linea in lineas:
                if linea.strip() != f"{nombre};{precio}":
                    f.write(linea)

        tree.delete(seleccion[0])
        messagebox.showinfo("Éxito", "Servicio eliminado correctamente.", parent=win)

    tb.Button(win, text="Eliminar Servicio Celular", bootstyle="danger", command=eliminar_servicio_cel).pack(pady=10)

def mostrar_servicios():
    win = tb.Toplevel(root)
    win.title("Lista de Servicios")
    centrar_ventana(win, 500, 400)
    text = tk.Text(win, width=50, height=20)
    text.pack()

    try:
        with open(SERVICIOS_PC_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            if not lineas:
                contenido = "No hay servicios registrados aún."
            else:
                contenido = f"{'Servicio':<25}{'Precio':<10}\n"
                contenido += "-"*35 + "\n"
                for linea in lineas:
                    partes = linea.strip().split(";")
                    if len(partes) == 2:
                        nombre, precio = partes
                        contenido += f"{nombre:<25}${precio:<10}\n"
    except FileNotFoundError:
        contenido = "No hay servicios registrados aún."

    text.insert(tk.END, contenido)
    text.config(state="disabled")  # ← ahora no editable

def guardar_trabajo(cliente, servicios):
    if not cliente or not servicios:
        messagebox.showwarning("Error", "Selecciona un cliente y al menos un servicio.")
        return
    with open(TRABAJOS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{cliente}: {', '.join(servicios)}\n")
    messagebox.showinfo("Éxito", "Trabajo registrado correctamente.")
    actualizar_lista_trabajos()

def mostrar_clientes():
    win = tb.Toplevel(root)
    win.title("Lista de Clientes")
    centrar_ventana(win, 800, 400)

    tree = ttk.Treeview(win, columns=("Nombre", "Teléfono", "Email"), show="headings", height=15)
    tree.pack(fill="both", expand=True)

    tree.heading("Nombre", text="Nombre")
    tree.heading("Teléfono", text="Teléfono")
    tree.heading("Email", text="Email")

    tree.column("Nombre", anchor="center", width=250)
    tree.column("Teléfono", anchor="center", width=150)
    tree.column("Email", anchor="center", width=350)

    try:
        with open(CLIENTES_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 3:
                    tree.insert("", "end", values=partes)
    except FileNotFoundError:
        tree.insert("", "end", values=("No hay clientes registrados aún", "", ""))

    # Botón eliminar
    def eliminar_cliente():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Selecciona un cliente para eliminar.", parent=win)
            return
        valores = tree.item(seleccion[0], "values")
        nombre, telefono, email = valores

        # Confirmación previa
        confirmar = messagebox.askyesno("Confirmar eliminación",
                                        f"¿Seguro que deseas eliminar al cliente:\n{nombre}?",
                                        parent=win)
        if not confirmar:
            return

        # Eliminar del archivo
        with open(CLIENTES_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        with open(CLIENTES_FILE, "w", encoding="utf-8") as f:
            for linea in lineas:
                if linea.strip() != f"{nombre};{telefono};{email}":
                    f.write(linea)

        # Eliminar de la tabla
        tree.delete(seleccion[0])
        messagebox.showinfo("Éxito", "Cliente eliminado correctamente.", parent=win)

    tb.Button(win, text="Eliminar Cliente", bootstyle="danger", command=eliminar_cliente).pack(pady=10)


def mostrar_servicios():
    win = tb.Toplevel(root)
    win.title("Lista de Servicios")
    centrar_ventana(win, 650, 400)

    tree = ttk.Treeview(win, columns=("Servicio", "Precio"), show="headings", height=15)
    tree.pack(fill="both", expand=True)

    tree.heading("Servicio", text="Servicio")
    tree.heading("Precio", text="Precio")

    tree.column("Servicio", anchor="center", width=450)
    tree.column("Precio", anchor="center", width=150)

    try:
        with open(SERVICIOS_PC_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 2:
                    nombre, precio = partes
                    tree.insert("", "end", values=(nombre, f"${precio}"))
    except FileNotFoundError:
        tree.insert("", "end", values=("No hay servicios registrados aún", ""))

    # Botón eliminar
    def eliminar_servicio():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Selecciona un servicio para eliminar.", parent=win)
            return
        valores = tree.item(seleccion[0], "values")
        nombre, precio = valores
        precio = precio.replace("$", "")

        # Confirmación previa
        confirmar = messagebox.askyesno("Confirmar eliminación",
                                        f"¿Seguro que deseas eliminar el servicio:\n{nombre}?",
                                        parent=win)
        if not confirmar:
            return

        # Eliminar del archivo
        with open(SERVICIOS_PC_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        with open(SERVICIOS_PC_FILE, "w", encoding="utf-8") as f:
            for linea in lineas:
                if linea.strip() != f"{nombre};{precio}":
                    f.write(linea)

        # Eliminar de la tabla
        tree.delete(seleccion[0])
        messagebox.showinfo("Éxito", "Servicio eliminado correctamente.", parent=win)

    tb.Button(win, text="Eliminar Servicio", bootstyle="danger", command=eliminar_servicio).pack(pady=10)


def actualizar_lista_trabajos():
    # Limpiar tabla
    for item in tree_trabajos.get_children():
        tree_trabajos.delete(item)

    try:
        with open(TRABAJOS_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            for linea in reversed(lineas):  # último trabajo primero
                partes = linea.split("|")
                cliente = partes[0].replace("Cliente:", "").strip()
                servicios = partes[1].replace("Servicios:", "").strip() if len(partes) > 1 else ""
                total = partes[2].replace("Total:", "").strip() if len(partes) > 2 else ""
                fecha = partes[3].replace("Fecha:", "").strip() if len(partes) > 3 else ""
                tree_trabajos.insert("", "end", values=(cliente, servicios, total, fecha))
    except FileNotFoundError:
        pass

def ventana_clientes():
    win = tb.Toplevel(root)
    win.title("Registrar Cliente")
    centrar_ventana(win, 400, 250)

    frame = tb.Frame(win)
    frame.pack(expand=True)

    tb.Label(frame, text="Nombre:").grid(row=0, column=0, pady=10, padx=10, sticky="e")
    tb.Label(frame, text="Teléfono:").grid(row=1, column=0, pady=10, padx=10, sticky="e")
    tb.Label(frame, text="Email:").grid(row=2, column=0, pady=10, padx=10, sticky="e")

    nombre = tb.Entry(frame, width=30)
    telefono = tb.Entry(frame, width=30)
    email = tb.Entry(frame, width=30)

    nombre.grid(row=0, column=1, pady=10, padx=10)
    telefono.grid(row=1, column=1, pady=10, padx=10)
    email.grid(row=2, column=1, pady=10, padx=10)

    nombre.focus_set()

    def guardar_y_cerrar():
        guardar_cliente(nombre.get(), telefono.get(), email.get())
        win.destroy()

    tb.Button(frame, text="Guardar", bootstyle="success", command=guardar_y_cerrar)\
        .grid(row=3, columnspan=2, pady=20)
    email.bind("<Return>", lambda event: guardar_y_cerrar())

def ventana_servicios():
    win = tb.Toplevel(root)
    win.title("Registrar Servicio")
    centrar_ventana(win, 400, 200)

    frame = tb.Frame(win)
    frame.pack(expand=True)

    tb.Label(frame, text="Nombre del servicio:").grid(row=0, column=0, pady=10, padx=10, sticky="e")
    tb.Label(frame, text="Precio:").grid(row=1, column=0, pady=10, padx=10, sticky="e")

    nombre = tb.Entry(frame, width=30)
    precio = tb.Entry(frame, width=30)

    nombre.grid(row=0, column=1, pady=10, padx=10)
    precio.grid(row=1, column=1, pady=10, padx=10)

    nombre.focus_set()

    def guardar_y_cerrar():
        guardar_servicio(nombre.get(), precio.get())
        win.destroy()

    tb.Button(frame, text="Guardar", bootstyle="primary", command=guardar_y_cerrar)\
        .grid(row=2, columnspan=2, pady=20)
    precio.bind("<Return>", lambda event: guardar_y_cerrar())

def ventana_trabajos():
    win = tb.Toplevel(root)
    win.title("Registrar Trabajo")
    centrar_ventana(win, 600, 500)

    # Cargar clientes
    clientes = []
    try:
        with open(CLIENTES_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) >= 1:
                    clientes.append(partes[0])
    except FileNotFoundError:
        clientes = []

    # Cargar servicios PC
    servicios_pc = []
    try:
        with open(SERVICIOS_PC_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 2:
                    nombre, precio = partes
                    servicios_pc.append((nombre, float(precio)))
    except FileNotFoundError:
        servicios_pc = []

    # Cargar servicios Celulares
    servicios_cel = []
    try:
        with open(SERVICIOS_CEL_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 2:
                    nombre, precio = partes
                    servicios_cel.append((nombre, float(precio)))
    except FileNotFoundError:
        servicios_cel = []

    # Selección de cliente
    tb.Label(win, text="Seleccionar Cliente:").pack()
    cliente_var = tk.StringVar()
    combo_clientes = ttk.Combobox(win, textvariable=cliente_var, values=clientes, width=50)
    combo_clientes.pack(pady=5)
    combo_clientes.focus_set()
    def abrir_lista(event):
        combo_clientes.event_generate("<Down>")
    combo_clientes.bind("<Button-1>", abrir_lista)

    # Selección de servicios PC
    tb.Label(win, text="Seleccionar Servicios de PC:").pack()
    listbox_pc = tk.Listbox(win, selectmode=tk.MULTIPLE, width=50, height=8)
    for nombre, precio in servicios_pc:
        listbox_pc.insert(tk.END, nombre)
    listbox_pc.pack(pady=5)

    # Selección de servicios Celulares
    tb.Label(win, text="Seleccionar Servicios de Celulares:").pack()
    listbox_cel = tk.Listbox(win, selectmode=tk.MULTIPLE, width=50, height=8)
    for nombre, precio in servicios_cel:
        listbox_cel.insert(tk.END, nombre)
    listbox_cel.pack(pady=5)

    # Guardar trabajo
    def guardar_y_cerrar():
        cliente = cliente_var.get()
        seleccionados_pc = [listbox_pc.get(i) for i in listbox_pc.curselection()]
        seleccionados_cel = [listbox_cel.get(i) for i in listbox_cel.curselection()]
        seleccionados = seleccionados_pc + seleccionados_cel

        if not cliente or not seleccionados:
            messagebox.showwarning("Error", "Selecciona un cliente y al menos un servicio.")
            return

        # Calcular total
        total = 0
        for sel in seleccionados_pc:
            for nombre, precio in servicios_pc:
                if nombre == sel:
                    total += precio
        for sel in seleccionados_cel:
            for nombre, precio in servicios_cel:
                if nombre == sel:
                    total += precio

        fecha = datetime.date.today().strftime("%d/%m/%Y")

        with open(TRABAJOS_FILE, "a", encoding="utf-8") as f:
            f.write(f"Cliente: {cliente} | Servicios: {', '.join(seleccionados)} | Total: ${total} | Fecha: {fecha}\n")

        messagebox.showinfo("Éxito", "Trabajo registrado correctamente.")
        actualizar_lista_trabajos()
        win.destroy()

    tb.Button(win, text="Guardar Trabajo", bootstyle="warning", command=guardar_y_cerrar).pack(pady=10)

def centrar_ventana(win, ancho=600, alto=400):
    win.update_idletasks()
    pantalla_ancho = win.winfo_screenwidth()
    pantalla_alto = win.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    win.geometry(f"{ancho}x{alto}+{x}+{y}")

# Ventana principal
root = tb.Window(themename="darkly")
root.title("Gestión de Servicio Técnico - Vesur")
centrar_ventana(root, 750, 600)

titulo = tb.Label(root, text="Vesur",
                  font=("Arial", 18, "bold"))
titulo.pack(pady=(10, 0))

subtitulo = tb.Label(root, text="Tecnología que responde",
                     font=("Arial", 12, "bold"))
subtitulo.pack(pady=(0, 10))

frame_botones = tb.Frame(root)
frame_botones.pack(pady=10)

tb.Button(frame_botones, text="Registrar Cliente", bootstyle="success", command=ventana_clientes).grid(row=0, column=0, padx=10)
tb.Button(frame_botones, text="Ver Clientes", bootstyle="info", command=mostrar_clientes).grid(row=1, column=0, pady=10)
tb.Button(frame_botones, text="Registrar Servicio PC", bootstyle="primary", command=ventana_servicios).grid(row=0, column=1, padx=10)
tb.Button(frame_botones, text="Ver Servicios PC", bootstyle="info", command=mostrar_servicios).grid(row=1, column=1, pady=10)
tb.Button(frame_botones, text="Registrar Servicio Celular", bootstyle="success", command=ventana_servicios_cel).grid(row=0, column=2, padx=10)
tb.Button(frame_botones, text="Ver Servicios Celular", bootstyle="info", command=mostrar_servicios_cel).grid(row=1, column=2, pady=10)
tb.Button(frame_botones, text="Registrar Trabajo", bootstyle="warning", command=ventana_trabajos).grid(row=0, column=3, padx=10)

tb.Label(root, text="Lista de Trabajos Realizados", font=("Arial", 14, "bold")).pack(pady=(10, 1))

tree_trabajos = ttk.Treeview(root, columns=("Cliente", "Servicios", "Total", "Fecha"), show="headings", height=15)
tree_trabajos.pack(pady=(0, 10), expand=True)

tree_trabajos.heading("Cliente", text="Cliente")
tree_trabajos.heading("Servicios", text="Servicios")
tree_trabajos.heading("Total", text="Total")
tree_trabajos.heading("Fecha", text="Fecha")

tree_trabajos.column("Cliente", anchor="center", width=150)
tree_trabajos.column("Servicios", anchor="center", width=300)
tree_trabajos.column("Total", anchor="center", width=100)
tree_trabajos.column("Fecha", anchor="center", width=100)

def guardar_servicio(nombre, precio):
    if not nombre or not precio:
        messagebox.showwarning("Error", "Completa todos los campos.")
        return
    try:
        precio = float(precio)
    except ValueError:
        messagebox.showwarning("Error", "El precio debe ser un número.")
        return
    with open(SERVICIOS_PC_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nombre};{precio}\n")
    messagebox.showinfo("Éxito", "Servicio registrado correctamente.")

def exportar_factura(cliente, telefono, email, servicios, total, fecha):
    # Abrir diálogo para elegir ubicación y nombre del archivo
    archivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        initialfile=f"Factura_{cliente.replace(' ', '_')}.pdf",
        title="Guardar factura como..."
    )

    if not archivo:  # si el usuario cancela
        return

    doc = SimpleDocTemplate(archivo, pagesize=A4)
    elementos = []
    estilos = getSampleStyleSheet()

    # Logo o encabezado con imagen
    logo = Image("vesur.jpeg", width=400, height=200)  # ajustá tamaño según tu imagen
    logo.hAlign = "CENTER"  # centrar la imagen
    elementos.append(logo)
    elementos.append(Spacer(1, 20))

    # Datos del cliente
    datos_cliente = Paragraph(
        f"<b>Datos del Cliente</b><br/>"
        f"<b>Nombre:</b> {cliente}<br/>"
        f"<b>Teléfono:</b> {telefono}<br/>"
        f"<b>Email:</b> {email}",
        estilos["Normal"]
    )
    elementos.append(datos_cliente)
    elementos.append(Spacer(1, 20))

    # Tabla de servicios
    data = [["Servicio", "Precio"]] + [[s[0], f"${s[1]}"] for s in servicios] + [["Total", total]]
    tabla = Table(data, colWidths=[300, 100])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,1), (-1,-1), colors.whitesmoke),
    ]))
    elementos.append(tabla)
    elementos.append(Spacer(1, 20))

    # Fecha
    fecha_trabajo = Paragraph(f"Fecha del trabajo: {fecha}", estilos["Normal"])
    elementos.append(fecha_trabajo)

    # Generar PDF en la ruta elegida
    doc.build(elementos)
    messagebox.showinfo("Factura generada", f"Factura exportada en:\n{archivo}")

def exportar_pdf_desde_seleccion():
    seleccion = tree_trabajos.selection()
    if not seleccion:
        return  # no mostrar cartel, simplemente no hace nada

    valores = tree_trabajos.item(seleccion[0], "values")
    cliente, servicios, total, fecha = valores

    # Buscar teléfono y email del cliente
    telefono, email = "", ""
    try:
        with open(CLIENTES_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(";")
                if datos[0] == cliente:
                    telefono, email = datos[1], datos[2]
                    break
    except FileNotFoundError:
        pass

    # Buscar precios de servicios
    servicios_con_precio = []
    try:
        with open(SERVICIOS_PC_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 2:  # solo procesar si tiene nombre y precio
                    nombre, precio = partes
                    for s in servicios.split(","):
                        if nombre.strip() == s.strip():
                            servicios_con_precio.append((nombre, precio))
    except FileNotFoundError:
        pass

    # Generar factura
    exportar_factura(cliente, telefono, email, servicios_con_precio, total, fecha)

tb.Button(root, text="Exportar a PDF", bootstyle="danger", command=exportar_pdf_desde_seleccion)\
    .pack(pady=10)

actualizar_lista_trabajos()
root.mainloop()