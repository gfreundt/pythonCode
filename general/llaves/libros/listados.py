from tkinter import END, StringVar
import ttkbootstrap as ttkb
from PIL import Image, ImageTk
import os


class Listados:

    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def gui(self):

        # definir ventana
        self.window = ttkb.Toplevel()
        self.window.geometry("700x1000")

        # definir y colocar frames de ventana principal
        self.frame_left = ttkb.Frame(self.window)
        self.frame_right = ttkb.Frame(self.window)
        self.frame_bottom = ttkb.Frame(self.window)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10)
        self.frame_bottom.grid(row=1, column=1, padx=10, pady=10)

        # frame izquierdo
        ttkb.Label(self.frame_left, text="Elegir Lista").pack(padx=15, pady=10)
        b1 = ttkb.Button(
            self.frame_left,
            text="Tipos de Puerta",
            command=lambda: self.listado(lista=0),
        )
        b2 = ttkb.Button(
            self.frame_left,
            text="Codigos de Puerta",
            command=lambda: self.listado(lista=1),
        )
        b3 = ttkb.Button(
            self.frame_left,
            text="Tipos de Cerradura",
            command=lambda: self.listado(lista=2),
        )
        b5 = ttkb.Button(
            self.frame_left,
            text="Regresar",
            command=lambda: self.regresar(),
            bootstyle="warning",
        )

        b1.pack(padx=15, pady=10)
        b2.pack(padx=15, pady=10)
        b3.pack(padx=15, pady=10)
        b5.pack(padx=15, pady=20)

        # frame derecho
        self.table = ttkb.Treeview(self.frame_right, bootstyle="primary")
        self.table["height"] = 30
        self.table.column(
            "#0",
            width=350,
            stretch="no",
        )
        self.table.pack(padx=20, pady=10, expand=1)

        # frame inferior
        self.b6 = ttkb.Button(
            self.frame_bottom,
            text="Nuevo",
            command=lambda: self.nuevo_guardar(),
        )
        self.b7 = ttkb.Button(
            self.frame_bottom,
            text="Eliminar",
            command=lambda: self.eliminar(),
            bootstyle="danger",
        )
        self.dato_ingresado = StringVar(value="")
        self.e1 = ttkb.Entry(self.frame_bottom, textvariable=self.dato_ingresado)
        self.b8 = ttkb.Button(
            self.frame_bottom,
            text="Cancelar",
            command=lambda: self.volver_listado(),
            bootstyle="warning",
        )

        self.b6.grid(row=0, column=0, padx=15, pady=10)
        self.b7.grid(row=0, column=1, padx=15, pady=10)

        # empezar con la primera tabla para tener algo cargado
        self.listado(lista=0)

    def listado(self, lista):

        self.col0, self.tabla = (
            ("Tipo de Puerta", "TiposPuertas"),
            ("Codigo de Puerta", "CodigosPuertas"),
            ("Tipo de Cerradura", "TiposCerraduras"),
        )[lista]

        # nombre de columna dependiendo de tabla seleccionada
        self.table.heading("#0", text=self.col0, anchor="center")

        # borrar datos anteriores
        for item in self.table.get_children():
            self.table.delete(item)

        # ingresar datos de tabla seleccionada
        self.cursor.execute(f"SELECT * FROM '{self.tabla}'")
        row_data = [i[0] for i in self.cursor.fetchall()]
        for row in row_data:
            self.table.insert(parent="", index=END, text=(row))

        # seleccionar primera fila
        self.table.selection_set(self.table.get_children()[0])

    def regresar(self):
        self.window.destroy()

    def nuevo_guardar(self):
        if self.b6.cget("text") == "Nuevo":
            # activar e1 (ingresar nombre de nuevo)
            self.e1.grid(row=0, column=1, padx=5)
            # desactivar b7 (eliminar)
            self.b7.grid_forget()
            # cambiar color y texto b6 (de 'nuevo' a 'guardar')
            self.b6.config(text="Guardar", bootstyle="success")
            # activar boton b8 (no guardar)
            self.b8.grid(row=1, column=0, padx=5)
            # desactivar botones de eleccion de tablas y regresar
            for widget in self.frame_left.winfo_children():
                widget.configure(state="disabled")

        else:
            self.cursor.execute(
                f"INSERT INTO '{self.tabla}' VALUES ('{self.dato_ingresado.get()}')"
            )
            self.conn.commit()
            self.table.insert(parent="", index=END, text=(self.dato_ingresado.get()))

            self.volver_listado()

    def volver_listado(self):
        # desactivar e1 (ingresar nombre de nuevo)
        self.e1.grid_forget()
        # reactivar b7 (eliminar)
        self.b7.grid(row=0, column=1, padx=15, pady=10)
        # cambiar color y texto b6 (de 'guardar' a 'nuevo')
        self.b6.config(text="Nuevo", bootstyle="primary")
        # desactivar boton b8 (no guardar)
        self.b8.grid_forget()
        # reactivar botones de eleccion de tablas y regresar
        for widget in self.frame_left.winfo_children():
            widget.configure(state="normal")
        # limpiar campo de ingreso de nombre nuevo
        self.dato_ingresado.set(value="")

    def eliminar(self):
        # TODO: mensaje de confirmacion
        _dato = self.table.item(self.table.focus())["text"]
        self.table.delete(self.table.selection())
        _campo = self.col0.split()[0]
        self.cursor.execute(f"DELETE FROM '{self.tabla}' WHERE {_campo} = '{_dato}'")
