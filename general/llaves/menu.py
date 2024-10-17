from tkinter import Tk, Label, Button, PhotoImage, StringVar, Entry, OptionMenu
from PIL import Image, ImageTk
import libro, proyecto
import os, time, json


class Menu:

    def __init__(self):
        self.window = Tk()
        self.window.geometry("500x300")
        self.window.title("Sistema de Maestranza de Llaves REDTOWER v0.6")
        self.window.iconphoto(False, PhotoImage(file="key1.png"))

        # insertar logo
        self.image = ImageTk.PhotoImage(
            Image.open("LOGOS-CMYK-10-2048x1160.png").resize((205, 116))
        )
        Label(self.window, image=self.image).place(x=90, y=10)

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
        self.codigo_ggmk = StringVar()
        self.nombre_libro = StringVar()
        self.notas_libro = StringVar()

        # definir inputs y sus titulos, y los botones
        self.option1_widgets = [
            (Label(self.window, text="Codigo GGMK: "), (10, 150)),
            (Label(self.window, text="Nombre del Libro: "), (10, 170)),
            (Label(self.window, text="Notas: "), (10, 190)),
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
        w = libro.Libro(libro=self.nombre_libro.get(), notas=self.notas_libro.get())
        w.crea_libro(self.codigo_ggmk.get())
        arbol = w.genera_texto_arbol(detalle=False)
        w.muestra_arbol(arbol)

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
        self.servicio_elegido = "proyecto"
        self.elegir_libro()

    def menu_cargar_proyecto(self):
        proyecto.main()

    def elegir_libro(self):
        # borrar botones del menu principal
        for button in self.main_widgets:
            button[0].place_forget()

        # drop-down menu configuration
        self.selected = StringVar()
        options = [i for i in os.listdir() if i[0] == "L" and ".json" in i]
        self.selected.set(options[0])

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
        with open(self.selected.get(), "r") as file:
            libro_ggmk = json.load(file)

        # cargar libro
        if self.servicio_elegido == "libro":
            w = libro.Libro(libro=libro_ggmk["libro"], notas=libro_ggmk["notas"])
            w.carga_libro(ggmk=libro_ggmk)

        # nuevo proyecto
        elif self.servicio_elegido == "proyecto":
            p = proyecto.Proyecto(libro_ggmk)
            p.nuevo_proyecto()

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
menu.main_menu()
