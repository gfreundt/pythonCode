from ttkbootstrap import StringVar, END
import ttkbootstrap as ttkb
from proyectos.cargar import Cargar


class Zonas:

    def __init__(self, cursor, conn):
        self.FONTS = (
            "Helvetica 10",
            "Helvetica 12",
            "Helvetica 12 bold",
            "Helvetica 15 bold",
            "Helvetica 10 bold",
            "Helvetica 20 bold",
        )
        self.cursor = cursor
        self.conn = conn

        self.secuencia_elegida = None
        self.secuencia_elegida2 = None

    def gui_pre_cargar(self):

        # abrir dialogo para elegir archivo
        cargar = Cargar(self)
        cargar.gui("proyectos")

    def gui_post_cargar(self):

        # capturar nombre de proyecto y libro que vienen del dialogo para elegir archivo
        self.nombre_proyecto = self.archivo_elegido[0]
        self.libro_origen = self.archivo_elegido[1]

        # definir ventana
        self.window = ttkb.Toplevel()
        self.window.geometry("900x950")

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
            text="Zona 1",
            command=lambda: self.listado(lista=0),
        )
        b2 = ttkb.Button(
            self.frame_left,
            text="Zona 2",
            command=lambda: self.listado(lista=1),
        )
        b3 = ttkb.Button(
            self.frame_left,
            text="Zona 3",
            command=lambda: self.listado(lista=2),
        )
        b4 = ttkb.Button(
            self.frame_left,
            text="Zona 4",
            command=lambda: self.listado(lista=3),
        )
        b8 = ttkb.Button(
            self.frame_left,
            text="Zona 5",
            command=lambda: self.listado(lista=4),
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
        b4.pack(padx=15, pady=10)
        b8.pack(padx=15, pady=10)
        b5.pack(padx=15, pady=10)

        # frame derecho
        ttkb.Label(self.frame_right, text="Nombre Categoria: ").grid(
            row=0, column=0, padx=20, pady=5
        )

        self.nombre_cat = StringVar(value="")
        self.e2 = ttkb.Entry(self.frame_right, textvariable=self.nombre_cat)
        self.e2.grid(row=0, column=1, padx=20, pady=5)
        self.table = ttkb.Treeview(self.frame_right, bootstyle="primary")
        self.table["height"] = 30
        self.table.column(
            "#0",
            width=350,
            stretch="no",
        )
        self.table.grid(row=1, column=1, columnspan=2, padx=20, pady=10)

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
        self.dato_nuevo = StringVar(value="")
        self.e1 = ttkb.Entry(self.frame_bottom, textvariable=self.dato_nuevo)
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

        self.col0 = f"Zona{lista+1}"

        # nombre de columna dependiendo de tabla seleccionada
        self.table.heading("#0", text=self.col0, anchor="center")

        # borrar datos anteriores
        for item in self.table.get_children():
            self.table.delete(item)

        # ingresar nombre de zona seleccionada de proyecto elegido
        self.cursor.execute(
            f"SELECT NombreZona FROM 'Zonas' WHERE NombreProyecto = '{self.nombre_proyecto}' AND Zona = {lista+1}"
        )
        self.nombre_cat.set(value=self.cursor.fetchone()[0])

        # ingresar opciones para zona seleccionada de proyecto elegido
        self.cursor.execute(
            f"SELECT Opcion FROM 'ZonasOpciones' JOIN 'Zonas' ON ZonaID = ZonaID_FK WHERE Zona = {lista+1}"
        )
        row_data = [i[0] for i in self.cursor.fetchall()]
        for row in row_data:
            self.table.insert(parent="", index=END, text=(row))

        # seleccionar primera fila
        if row_data:
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
