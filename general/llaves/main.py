from tkinter import Button, PhotoImage, StringVar, OptionMenu
import ttkbootstrap as ttkb
from PIL import Image, ImageTk

import sqlite3
import os

import libros.nuevo, libros.cargar, libros.listados
import proyectos.nuevo, proyectos.visor, proyectos.fabrica, proyectos.zonas
import herramientas.configuraciones, herramientas.validaciones, herramientas.kpis


class MainMenu:

    def __init__(self):

        # cargar base de datos
        self.conn = sqlite3.connect("llaves.db", isolation_level="DEFERRED")
        self.cursor = self.conn.cursor()

        # definir tamano de ventana
        self.win_size_x, self.win_size_y = (800, 550)

        self.libros_listado = libros.listados.Listados(self.cursor, self.conn)

        self.proyectos_nuevo = proyectos.nuevo.Nuevo(self.cursor, self.conn)
        self.proyectos_visor = proyectos.visor.Visor(self.cursor, self.conn)
        self.proyectos_fabrica = proyectos.fabrica.Fabrica(self.cursor, self.conn)
        self.proyectos_listados = proyectos.zonas.Zonas(self.cursor, self.conn)

        self.herramientas_configuraciones = (
            herramientas.configuraciones.Configuraciones(self.cursor, self.conn)
        )
        self.herramientas_mantenimiento = herramientas.kpis.Kpis(self.cursor, self.conn)
        self.herramientas_validaciones = herramientas.validaciones.Validar(
            self.cursor, self.conn
        )

    def main_menu(self):

        # GUI - inicializar
        self.window = ttkb.Window(themename="darkly")
        self.win_posx = (int(self.window.winfo_screenwidth()) - self.win_size_x) // 2
        self.win_posy = (int(self.window.winfo_screenheight()) - self.win_size_y) // 3
        self.window.geometry(
            f"{self.win_size_x}x{self.win_size_y}+{self.win_posx}+{self.win_posy}"
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

        # definir cuatro grupos de botones: libros, proyectos, herramientas, salir
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

        # libros - botones: nuevo y cargar
        b1 = [
            ttkb.Button(
                bottom_frames[0], text="Nuevo", command=lambda: libros.nuevo.gui(self)
            ),
            ttkb.Button(
                bottom_frames[0],
                text="Cargar",
                command=lambda: libros.cargar.gui(self),
            ),
            ttkb.Button(
                bottom_frames[0],
                text="Listados",
                command=lambda: self.libros_listado.gui(),
            ),
        ]

        # proyectos - botones: nuevo, cargar, fabrica
        b2 = [
            ttkb.Button(
                bottom_frames[1],
                text="Nuevo",
                command=lambda: self.proyectos_nuevo.gui_pre_cargar(),
            ),
            ttkb.Button(
                bottom_frames[1],
                text="Cargar",
                command=lambda: self.proyectos_visor.gui_pre_cargar(self),
            ),
            ttkb.Button(
                bottom_frames[1],
                text="Fabrica",
                command=lambda: self.proyectos_fabrica.gui_pre_cargar(),
            ),
            ttkb.Button(
                bottom_frames[1],
                text="Zonas",
                command=lambda: self.proyectos_listados.gui_pre_cargar(),
            ),
        ]

        # herramientas - botones: cilindros, validaciones, configuracion
        b3 = [
            ttkb.Button(
                bottom_frames[2],
                text="Configuraciones",
                command=lambda: self.herramientas_configuraciones.gui(),
            ),
            ttkb.Button(
                bottom_frames[2],
                text="Validaciones",
                command=lambda: self.herramientas_validaciones.gui(),
            ),
            ttkb.Button(
                bottom_frames[2],
                text="Mantenimiento",
                command=lambda: self.herramientas_mantenimiento.gui(),
            ),
        ]

        # salir - unico boton
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


if __name__ == "__main__":
    menu = MainMenu()
    menu.main_menu()
