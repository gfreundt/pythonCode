from tkinter import Button, PhotoImage, StringVar, OptionMenu
import ttkbootstrap as ttkb
from PIL import Image, ImageTk

# import libro as libro, proyecto
import sqlite3
import os

from libros import cargar as listado_libro, nuevo as nuevo_libro


class Menu:

    def __init__(self):

        # cargar base de datos
        self.conn = sqlite3.connect("llaves.db", isolation_level="DEFERRED")
        self.cursor = self.conn.cursor()

        # instancias de trabajo
        # self.LIBRO = libro.Libro(conn=self.conn, cursor=self.cursor)
        # self.PROYECTO = proyecto.Proyecto(conn=self.conn, cursor=self.cursor)

        # GUI - inicializar
        win_size_x, win_size_y = (700, 550)
        self.window = ttkb.Window(themename="darkly")
        self.win_posx = (int(self.window.winfo_screenwidth()) - win_size_x) // 2
        self.win_posy = (int(self.window.winfo_screenheight()) - win_size_y) // 3
        self.window.geometry(
            f"{win_size_x}x{win_size_y}+{self.win_posx}+{self.win_posy}"
        )
        self.window.title("Sistema de Maestranza de Llaves v0.6")
        self.window.iconphoto(
            False, PhotoImage(file=os.path.join("static", "key1.png"))
        )

        # GUI - Top Frame: logo
        self.top_frame = ttkb.Frame(self.window)
        self.top_frame.pack(pady=10)

        # GUI - Bottom Frame: botones del menu
        self.bottom_frame = ttkb.Frame(self.window)
        self.bottom_frame.pack(pady=10)

        # Top Frame - insertar logo
        self.image = ImageTk.PhotoImage(
            Image.open(os.path.join("static", "LOGOS-CMYK-10-2048x1160.png")).resize(
                (400, 226)
            )
        )
        ttkb.Label(self.top_frame, image=self.image).grid(row=0, column=0, columnspan=3)

    def main_menu(self):

        # define and place three menu categories
        bottom_frames = [
            ttkb.LabelFrame(self.bottom_frame, text=" Libros ", bootstyle="info"),
            ttkb.LabelFrame(self.bottom_frame, text=" Proyectos ", bootstyle="success"),
            ttkb.LabelFrame(
                self.bottom_frame, text=" Herramientas ", bootstyle="warning"
            ),
            ttkb.LabelFrame(self.bottom_frame, text=" Fin ", bootstyle="danger"),
        ]

        for x, widget in enumerate(bottom_frames):
            widget.grid(row=0, column=x, padx=20)

        # buttons for Libros category
        b1 = [
            ttkb.Button(bottom_frames[0], text="Nuevo", command=self.nuevo_libro_crear),
            ttkb.Button(
                bottom_frames[0],
                text="Cargar",
                command=lambda: listado_libro.listado(self.cursor, self.window),
            ),
        ]

        # buttons for Proyectos category
        b2 = [
            ttkb.Button(
                bottom_frames[1], text="Nuevo", command=self.menu_nuevo_proyecto
            ),
            ttkb.Button(
                bottom_frames[1], text="Cargar", command=self.menu_cargar_proyecto
            ),
            ttkb.Button(
                bottom_frames[1], text="Fabrica", command=self.menu_fabrica_proyecto
            ),
        ]

        # buttons for Herramientas category
        b3 = [
            ttkb.Button(
                bottom_frames[2], text="Cilindros", command=self.menu_cilindros
            ),
            ttkb.Button(
                bottom_frames[2], text="Validaciones", command=self.menu_validaciones
            ),
            ttkb.Button(
                bottom_frames[2],
                text="Configuracion",
                command=self.menu_configuraciones,
            ),
        ]

        # buttons for Fin category
        b4 = [
            ttkb.Button(
                bottom_frames[3],
                text="Salir",
                command=self.menu_salir,
                bootstyle="danger",
            )
        ]

        for y, widget in enumerate(b1 + b2 + b3 + b4):
            widget.grid(row=y, column=0, pady=10, padx=18)

        self.window.mainloop()

    def nuevo_libro_crear(self):

        # llamar a crear libro
        nuevo_libro.gui(
            cursor=self.cursor,
            conn=self.conn,
            previous_window=self.window,
            window_posx=self.win_posx,
            window_posy=self.win_posy,
        )

    def nuevo_regresar(self):
        # desactivar botones de menu secundario
        for button in self.option1_widgets:
            button[0].place_forget()

        # reactivar botones de menu primario
        for button in self.main_widgets:
            button[0].place(x=button[1][0], y=button[1][1])

    def menu_cargar_libro(self):
        listado_libro.listado(self.cursor, window)

    def menu_nuevo_proyecto(self):
        self.servicio_elegido = "nuevo_proyecto"
        self.elegir_libro()

    def menu_cargar_proyecto(self):
        self.servicio_elegido = "cargar_proyecto"
        self.elegir_libro()

    def menu_fabrica_proyecto(self):
        return

    def menu_herramientas(self):
        return

    def menu_mantenimiento(self):
        return

    def menu_cilindros(self):
        return

    def menu_validaciones(self):
        return

    def menu_configuraciones(self):
        return

    def elegir_libro(self):
        # borrar botones del menu principal
        for button in self.main_widgets:
            button[0].place_forget()

        # buscar todas las tablas de libros
        self.cursor.execute(
            f"SELECT * FROM {'proyectos' if self.servicio_elegido == 'cargar_proyecto' else 'libros'}"
        )
        options = [i[0] for i in self.cursor.fetchall()]

        if not options:
            options = []

        self.selected = StringVar(value=options[0])

        self.option1_widgets = [
            (OptionMenu(self.window, self.selected, *options), (50, 120)),
            (
                Button(text="Elegir", command=self.elegir_libro_resultado),
                (250, 120),
            ),
            (Button(text="Regresar", command=self.elegir_libro_regresar), (250, 160)),
        ]

        # colocar widgets definidos
        for button in self.option1_widgets:
            button[0].place(x=button[1][0], y=button[1][1])

    def elegir_libro_resultado(self):

        # cargar libro
        if self.servicio_elegido == "libro":
            self.LIBRO.carga_libro(tabla=self.selected.get())

        # nuevo proyecto
        elif self.servicio_elegido == "nuevo_proyecto":
            self.PROYECTO.nuevo_proyecto(tabla=self.selected.get())

        # cargar proyecto
        elif self.servicio_elegido == "cargar_proyecto":
            self.PROYECTO.cargar_proyecto(tabla=self.selected.get())

    def elegir_libro_regresar(self):
        # desactivar botones de menu secundario
        for button in self.option1_widgets:
            button[0].place_forget()

        # reactivar botones de menu primario
        for button in self.main_widgets:
            button[0].place(x=button[1][0], y=button[1][1])

    def menu_salir(self):
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


def main():
    menu = Menu()
    menu.main_menu()


if __name__ == "__main__":
    main()
