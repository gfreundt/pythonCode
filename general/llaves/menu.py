from tkinter import Tk, Label, Button, PhotoImage, StringVar, Entry, OptionMenu
from PIL import Image, ImageTk
import libro as libro, proyecto
import sqlite3


class Menu:

    def __init__(self):

        # cargar base de datos
        self.conn = sqlite3.connect("llaves.db", isolation_level="DEFERRED")
        self.cursor = self.conn.cursor()

        # GUI - inicializar
        self.window = Tk()
        self.window.geometry("500x300")
        self.window.title("Sistema de Maestranza de Llaves REDTOWER v0.6")
        self.window.iconphoto(False, PhotoImage(file="key1.png"))

        # GUI - insertar logo
        self.image = ImageTk.PhotoImage(
            Image.open("LOGOS-CMYK-10-2048x1160.png").resize((205, 116))
        )
        Label(self.window, image=self.image).place(x=90, y=10)

        # GUI - empezar
        self.main_menu()

    def main_menu(self):

        # crear botones del menu principal
        self.main_widgets = [
            (Button(text="Nuevo Libro", command=self.menu_nuevo_libro), (100, 150)),
            (Button(text="Cargar Libro", command=self.menu_cargar_libro), (200, 150)),
            (
                Button(text="Nuevo Proyecto", command=self.menu_nuevo_proyecto),
                (100, 180),
            ),
            (
                Button(text="Cargar Proyecto", command=self.menu_cargar_proyecto),
                (200, 180),
            ),
            (Button(text="Herramients", command=self.menu_cargar_proyecto), (300, 150)),
            (Button(text="Salir", command=self.salir), (300, 250)),
        ]

        for button in self.main_widgets:
            button[0].place(x=button[1][0], y=button[1][1])

        self.window.mainloop()

    def menu_nuevo_libro(self):

        # borrar botones del menu principal
        for button in self.main_widgets:
            button[0].place_forget()

        # definir variables de inputs
        self.formato_libro = StringVar(value="1-1-1-0-4")
        self.codigo_ggmk = StringVar()
        self.nombre_libro = StringVar()
        self.notas_libro = StringVar()

        # definir inputs y sus titulos, y los botones
        options = ["1-1-1-0-4", "1-1-2-0-3", "1-1-1-1-3"]
        self.option1_widgets = [
            (Label(self.window, text="Codigo GGMK: "), (10, 150)),
            (Label(self.window, text="Formato: "), (10, 120)),
            (Label(self.window, text="Nombre del Libro: "), (10, 170)),
            (Label(self.window, text="Notas: "), (10, 190)),
            (OptionMenu(self.window, self.formato_libro, *options), (130, 120)),
            (
                Entry(
                    self.window,
                    textvariable=self.codigo_ggmk,
                    font=("calibre", 10, "normal"),
                ),
                (130, 150),
            ),
            (
                Entry(
                    self.window,
                    textvariable=self.nombre_libro,
                    font=("calibre", 10, "normal"),
                ),
                (130, 170),
            ),
            (
                Entry(
                    self.window,
                    textvariable=self.notas_libro,
                    font=("calibre", 10, "normal"),
                ),
                (130, 190),
            ),
            (Button(text="Crear Libro", command=self.nuevo_libro_crear), (100, 250)),
            (Button(text="Regresar", command=self.nuevo_regresar), (200, 250)),
        ]

        # colocar widgets definidos
        for button in self.option1_widgets:
            button[0].place(x=button[1][0], y=button[1][1])

    def nuevo_libro_crear(self):
        # desactivar botones de menu secundario
        for button in self.option1_widgets:
            button[0].place_forget()

        # llamar a crear libro
        w = libro.Libro(self.conn)
        w.crea_libro(
            codigo_ggmk=self.codigo_ggmk.get(),
            libro_nombre=self.nombre_libro.get(),
            libro_notas=self.notas_libro.get(),
            formato=self.formato_libro.get(),
        )

        # reactivar botones de menu primario
        for button in self.main_widgets:
            button[0].place(x=button[1][0], y=button[1][1])

    def nuevo_regresar(self):
        # desactivar botones de menu secundario
        for button in self.option1_widgets:
            button[0].place_forget()

        # reactivar botones de menu primario
        for button in self.main_widgets:
            button[0].place(x=button[1][0], y=button[1][1])

    def menu_cargar_libro(self):
        self.servicio_elegido = "libro"
        self.elegir_libro()

    def menu_nuevo_proyecto(self):
        self.servicio_elegido = "nuevo_proyecto"
        self.elegir_libro()

    def menu_cargar_proyecto(self):
        self.servicio_elegido = "cargar_proyecto"
        self.elegir_libro()

    def elegir_libro(self):
        # borrar botones del menu principal
        for button in self.main_widgets:
            button[0].place_forget()

        # buscar todas las tablas de libros
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        options = [
            i[0]
            for i in self.cursor.fetchall()
            if i[0][0] == ("P" if self.servicio_elegido == "cargar_proyecto" else "L")
        ]

        self.selected = StringVar(value=options[0])

        self.option1_widgets = [
            (OptionMenu(self.window, self.selected, *options), (50, 120)),
            (
                Button(text="Elegir Libro", command=self.elegir_libro_resultado),
                (250, 120),
            ),
            (Button(text="Regresar", command=self.elegir_libro_regresar), (250, 160)),
        ]

        # colocar widgets definidos
        for button in self.option1_widgets:
            button[0].place(x=button[1][0], y=button[1][1])

    def elegir_libro_resultado(self):
        # cargar informacion de libro en diccionario
        self.cursor.execute(f"SELECT * FROM '{self.selected.get()}'")
        libro_data = self.cursor.fetchall()

        # cargar libro
        if self.servicio_elegido == "libro":
            w = libro.Libro(conn=self.conn)
            w.carga_libro(libro_data=libro_data)

        # nuevo proyecto
        elif self.servicio_elegido == "nuevo_proyecto":
            p = proyecto.Proyecto(conn=self.conn)
            p.nuevo_proyecto(tabla=self.selected.get())

        # cargar proyecto
        elif self.servicio_elegido == "cargar_proyecto":
            p = proyecto.Proyecto(conn=self.conn)
            p.cargar_proyecto(tabla=self.selected.get())

    def elegir_libro_regresar(self):
        # desactivar botones de menu secundario
        for button in self.option1_widgets:
            button[0].place_forget()

        # reactivar botones de menu primario
        for button in self.main_widgets:
            button[0].place(x=button[1][0], y=button[1][1])

    def salir(self):
        self.window.quit()


menu = Menu()

# L-511421-!6!3!0!1245!
