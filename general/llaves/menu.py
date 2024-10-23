from tkinter import Tk, Label, Button, PhotoImage, StringVar, Entry, OptionMenu, Canvas
from PIL import Image, ImageTk
import libro as libro, proyecto
import sqlite3
from random import randrange


class Menu:

    def __init__(self):

        # cargar base de datos
        self.conn = sqlite3.connect("llaves.db", isolation_level="DEFERRED")
        self.cursor = self.conn.cursor()

        # GUI - inicializar
        winx, winy = (500, 300)
        self.window = Tk()
        self.window.configure(bg="white")
        x = (int(self.window.winfo_screenwidth()) - winx) // 2
        y = (int(self.window.winfo_screenheight()) - winy) // 3
        self.window.geometry(f"{winx}x{winy}+{x}+{y}")
        self.window.title("Sistema de Maestranza de Llaves REDTOWER v0.6")
        self.window.iconphoto(False, PhotoImage(file="key1.png"))

        # GUI - insertar logo
        self.image = ImageTk.PhotoImage(
            Image.open("LOGOS-CMYK-10-2048x1160.png").resize((205, 116))
        )
        Label(self.window, image=self.image).place(x=145, y=10)

        # GUI - empezar
        self.main_menu()

    def main_menu(self):

        # crear lineas
        canvas = Canvas(bg="white", border=-1)
        canvas.create_rectangle(10, 10, 90, 130)
        canvas.create_rectangle(110, 10, 190, 130)

        # crear botones del menu principal
        self.main_widgets = [
            (canvas, (80, 130)),
            (Button(text="Nuevo", padx=7, command=self.menu_nuevo_libro), (100, 150)),
            (Button(text="Cargar", padx=7, command=self.menu_cargar_libro), (100, 190)),
            (
                Button(text="Listado", padx=7, command=self.menu_cargar_libro),
                (100, 230),
            ),
            (
                Button(text="Nuevo", padx=7, command=self.menu_nuevo_proyecto),
                (200, 150),
            ),
            (
                Button(text="Cargar", padx=7, command=self.menu_cargar_proyecto),
                (200, 190),
            ),
            (
                Button(text="Listado", padx=7, command=self.menu_cargar_proyecto),
                (200, 230),
            ),
            (
                Button(text="Herramients", padx=7, command=self.menu_cargar_proyecto),
                (300, 150),
            ),
            (Button(text="Salir", padx=7, command=self.salir), (320, 230)),
            (Label(text="LIBROS", bg="white"), (105, 270)),
            (Label(text="PROYECTOS", bg="white"), (193, 270)),
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
            (Label(self.window, text="Codigo GGMK: "), (10, 170)),
            (Label(self.window, text="Formato: "), (10, 140)),
            (Label(self.window, text="Nombre del Libro: "), (10, 200)),
            (Label(self.window, text="Notas: "), (10, 230)),
            (OptionMenu(self.window, self.formato_libro, *options), (130, 140)),
            (
                Entry(
                    self.window,
                    textvariable=self.codigo_ggmk,
                    font=("calibre", 10, "normal"),
                ),
                (130, 170),
            ),
            (
                Entry(
                    self.window,
                    textvariable=self.nombre_libro,
                    font=("calibre", 10, "normal"),
                ),
                (130, 200),
            ),
            (
                Entry(
                    self.window,
                    textvariable=self.notas_libro,
                    font=("calibre", 10, "normal"),
                ),
                (130, 230),
            ),
            (Button(text="aleatoria", command=self.ggmk_aleatoria), (280, 170)),
            (Button(text="Crear Libro", command=self.nuevo_libro_crear), (370, 140)),
            (Button(text="Regresar", command=self.nuevo_regresar), (370, 180)),
        ]

        # colocar widgets definidos
        for button in self.option1_widgets:
            button[0].place(x=button[1][0], y=button[1][1])

    def ggmk_aleatoria(self):

        _codigo = "123456"  # ggmk invalida
        while not valida_codigo(_codigo):
            _codigo = "".join([str(randrange(0, 10)) for _ in range(6)])

        self.codigo_ggmk.set(value=_codigo)

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
            w.carga_libro(tabla=self.selected.get())

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


def valida_codigo(codigo):

    # string to tuple
    codigo = tuple(int(i) for i in codigo)

    # no puede haber 8 o 9 de diferencia entre pines
    for position in range(len(codigo) - 1):
        c = codigo[position]
        n = codigo[position + 1]
        if abs(n - c) >= 8:
            return False

    # no puede haber una secuencia [par-impar-par-impar-par-impar] o [impar-par-impar-par-impar-par]
    test = [int(i) % 2 for i in codigo]
    if test == [0, 1, 0, 1, 0, 1] or test == [1, 0, 1, 0, 1, 0]:
        return False

    # no pueden haber tres pines seguidos iguales
    for pos in range(4):
        if codigo[pos : pos + 3].count(codigo[pos]) == 3:
            return False

    return True


menu = Menu()

# L-511421-!6!3!0!1245!
