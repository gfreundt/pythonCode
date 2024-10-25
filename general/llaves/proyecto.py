from copy import deepcopy as copy
from tkinter import Tk, Label, Button, Text, Spinbox, IntVar, END, Entry
from pprint import pprint
from datetime import datetime as dt
from visor import Visor


class Proyecto:

    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor()

    def nuevo_proyecto(self, tabla):

        self.window2 = Tk()
        self.window2.geometry("1000x1300")
        self.text_area = Text(self.window2, height=100, width=80)
        self.text_area.place(x=10, y=60)
        self.ggmk = None

        self.nombre_tabla = tabla
        self.arbol = []
        self.spinbox_valor = IntVar(self.window2, value=1)

        self.vertical = 50

        self.boton1 = Button(
            self.window2, text="Agrega GMK", command=self.menu_agrega_gmk
        )
        self.boton1.place(x=700, y=70)

        self.boton2 = Button(
            self.window2, text="Agrega MK", command=self.menu_agrega_mk
        )
        self.boton2.place(x=730, y=100)
        self.boton2.config(state="disabled")

        self.boton3 = Button(
            self.window2, text="Nivel Completo", command=self.menu_nivel_completo
        )
        self.boton3.place(x=860, y=85)

        self.boton4 = Button(self.window2, text="Deshacer", command=self.menu_deshacer)
        self.boton4.place(x=860, y=135)

        self.cantidad_llaves = Spinbox(
            self.window2, from_=1, to=8, textvariable=self.spinbox_valor, width=2
        )
        self.cantidad_llaves.place(x=760, y=130)
        self.cantidad_llaves.config(state="disabled")

        self.nivel_boton = 0
        self.secuencia_gmk = -1

        self.muestra_arbol()

    def menu_agrega_gmk(self):
        self.boton1.config(state="disabled")
        self.boton2.config(state="active")

        self.arbol.append([])
        self.nivel_boton = 1
        self.secuencia_gmk += 1

        self.muestra_arbol()

    def menu_agrega_mk(self):
        self.nivel_boton = 2
        self.boton2.config(state="disabled")
        self.cantidad_llaves.config(state="normal")
        self.arbol[-1].append(0)

        self.muestra_arbol()

    def menu_agrega_k(self):
        self.arbol[self.secuencia_gmk].append(self.spinbox_valor.get())
        self.boton4.config(state="disabled")
        self.cantidad_llaves.config(state="disabled")

        self.muestra_arbol()

    def menu_nivel_completo(self):
        if self.nivel_boton == 0:
            self.ggmk = self.asigna_llaves()
            self.window2.destroy()
            self.vista = Visor(configuracion="proyecto", proceso=self)
            self.vista.mostrar()
            return
        elif self.nivel_boton == 1:
            self.nivel_boton = 0
            self.boton1.config(state="active")
            self.boton2.config(state="disabled")
        elif self.nivel_boton == 2:
            self.nivel_boton = 1
            self.arbol[-1][-1] = self.spinbox_valor.get()
            self.cantidad_llaves.config(state="disabled")
            self.boton2.config(state="active")

        self.muestra_arbol()

    def menu_deshacer():
        return

    def asigna_llaves(self):

        self.nombre_proyecto = "P" + self.nombre_tabla[1:]

        # copia estructura de tabla de libro a nuevo proyecto
        self.cursor.execute(f"DROP TABLE IF EXISTS '{self.nombre_proyecto}'")
        self.cursor.execute(
            f"CREATE TABLE '{self.nombre_proyecto}' (GGMK, GMK, MK, SMK, K, Secuencia, Cilindro, MP, TipoPuerta, Cerradura, Copias, Zona1, Zona2, Zona3, Zona4, ZonaCodigo, Notas)"
        )

        # extrae del libro la cantidad de GMK necesarias para el proyecto
        self.cursor.execute(
            f"SELECT DISTINCT GMK FROM '{self.nombre_tabla}' LIMIT {len(self.arbol)}"
        )
        required_gmks = [i[0] for i in self.cursor.fetchall()]

        # extrae del libro todas las MK necesarias para el proyecto
        for g, gmk in enumerate(required_gmks):
            self.cursor.execute(
                f"SELECT DISTINCT MK FROM '{self.nombre_tabla}' WHERE GMK = '{gmk}' LIMIT {len(self.arbol[g])}"
            )
            required_mks = [i[0] for i in self.cursor.fetchall()]

            # llena la tabla del proyecto con las llaves necesarias
            for m, mk in enumerate(required_mks):
                cmd = f"""  INSERT INTO '{self.nombre_proyecto}' (GGMK, GMK, MK, SMK, K, Secuencia, Cilindro, MP, Copias)
                            SELECT GGMK, GMK, MK, SMK, K, Secuencia, Cilindro, MP, 1
                            FROM '{self.nombre_tabla}' WHERE MK = '{mk}' LIMIT {self.arbol[g][m]}"""
                self.cursor.execute(cmd)

        self.conn.commit()

    def muestra_arbol(self):
        self.text_area.delete("1.0", "end")
        self.text_area.insert(END, self.genera_texto_arbol())

    def cargar_proyecto(self, tabla):
        self.nombre_tabla = tabla
        self.vista = Visor(configuracion="proyecto", proceso=self)
        self.vista.mostrar()

    def listado(self):
        self.window2 = Tk()
        self.window2.geometry("2000x1300")

        self.cursor.execute("SELECT * FROM proyectos")

        data = [
            (
                "Codigo",
                "GGMK",
                "Formato",
                "Nombre",
                "Notas",
                "Creacion",
                "GMKs",
                "MKs",
                "SMKs",
                "Ks",
            )
        ] + self.cursor.fetchall()

        for r, row in enumerate(data):
            for c, col in enumerate(row):
                self.e = Entry(self.window2, font=("calibre", 10, "normal"))
                self.e.grid(row=r, column=c)
                self.e.insert(END, col if col else "")

        Button(self.window2, text="Regresar", command=self.listado_regreso).place(
            x=500, y=100
        )

    def listado_regreso(self):
        self.window2.destroy()

    def genera_texto_arbol(self):
        totalx = 0
        total = 1

        output = f"GGMK\n"
        for p, gmk in enumerate(self.arbol, start=1):
            total += 1
            output += "|\n"
            output += f"|{'-'*9}GMK-{p:02d}\n"

            for q, mk in enumerate(gmk, start=1):
                total += 1
                output += f"{' ' if p==len(self.arbol) else '|'}{' '*9}|\n"
                output += f"|{' '*9}{' ' if p==len(self.arbol) else '|'}{'-'*9} MK-{p:02d}-{q:02d}\n"
                output += f"{' ' if p==len(self.arbol) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{' '*10}|\n"

                output += f"{' ' if p==len(self.arbol) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{' '*10}Unicas: {mk}\n"
                totalx += mk

        output += f"\nTotal Llaves: {total+totalx:,}\n"
        output += f"Total Puertas: {totalx:,}\n"

        return output
