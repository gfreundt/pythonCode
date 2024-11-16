from copy import deepcopy as copy
from tkinter import PhotoImage, StringVar, ARC, DoubleVar
from PIL import Image, ImageTk
import ttkbootstrap as ttkb
from pprint import pprint
from datetime import datetime as dt
import os


class Fabrica:

    def __init__(self, cursor, conn, x, y):
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
        self.main_win_posx = x
        self.main_win_posy = y

        self.secuencia_elegida = None
        self.secuencia_elegida2 = None

        self.cursor.execute(f"SELECT LibroOrigen from 'P-895185-(5)(21)()(340)-005'")
        self.libro_origen = self.cursor.fetchone()[0]

    def gui(self):

        # crear y configurar ventana
        self.window = ttkb.Toplevel()
        winx, winy = (1350, 1500)
        x = self.main_win_posx - 120
        y = self.main_win_posy - 120
        self.window.geometry(f"{winx}x{winy}+{x}+{y}")
        self.window.title("Fabrica de Proyecto")
        self.window.iconphoto(
            False, PhotoImage(file=os.path.join("static", "key1.png"))
        )

        # crear dashboard por primera vez
        self.editar_llave()
        self.editar_cilindro()
        self.actualizar_dashboard()

        # agregar boton finalizar
        ttkb.Button(
            self.window,
            text="Finalizar",
            command=lambda: self.boton_finalizar(),
            bootstyle="danger",
        ).grid(row=4, column=0, columnspan=4, pady=50)

    def boton_finalizar(self):

        # grabar bd y regresar a menu principal
        self.conn.commit()
        self.window.destroy()

    def actualizar_dashboard(self):

        # activar/actualizar todas las partes del dashboard
        totales_llaves = self.dashboard_llaves()
        totales_cils = self.dashboard_cilindros()
        self.dashboard_pines()
        self.dashboard_meters(totales_llaves, totales_cils)
        self.dibujar_llave()
        self.dibujar_cilindro()

    def dashboard_llaves(self):

        data = {}

        for jerarquia in ("GGMK", "GMK", "MK", "K"):
            self.cursor.execute(
                f"SELECT SUM(copias), SUM(FabricadoLlaveCopias) FROM 'P-895185-(5)(21)()(340)-005' WHERE Jerarquia = '{jerarquia}'"
            )
            data.update({jerarquia: self.cursor.fetchone()})

        frame = ttkb.LabelFrame(
            self.window, bootstyle="success", text=" Avance Creacion de Llaves "
        )
        frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

        columnas = [
            "Nivel de Llave",
            "Completas",
            "Pendientes",
            "Totales",
            "% Completas",
        ]

        # nombres de columnas
        for col, columna in enumerate(columnas):
            ttkb.Label(frame, text=columna, font=self.FONTS[4]).grid(
                column=col, row=1, padx=10, pady=5
            )

        # filas
        totales = [0, 0, 0, 0]
        for row, (fila, data) in enumerate(data.items(), start=2):
            ttkb.Label(frame, text=fila, font=self.FONTS[0]).grid(column=0, row=row)
            ttkb.Label(frame, text=str(data[1])).grid(column=1, row=row)
            ttkb.Label(frame, text=str(data[0] - data[1])).grid(column=2, row=row)
            ttkb.Label(frame, text=str(data[0])).grid(column=3, row=row)
            ttkb.Label(frame, text=f"{data[1]/data[0]:.1%}").grid(column=4, row=row)
            totales[0] += data[1]

            totales[2] += data[0]

        # fila totales
        totales[1] = totales[2] - totales[0]
        totales[3] = f"{totales[0] / totales[2]:.1%}"
        totales = ["Total"] + totales
        for col, columna in enumerate(totales):
            ttkb.Label(frame, text=str(columna), font=self.FONTS[4]).grid(
                column=col, row=6, padx=10
            )

        return (totales[1], totales[3])

    def dashboard_cilindros(self):

        self.cursor.execute(
            f"SELECT COUNT(*), SUM(FabricadoCilindro) FROM 'P-895185-(5)(21)()(340)-005' WHERE Jerarquia = 'K'"
        )
        data = self.cursor.fetchone()

        frame = ttkb.LabelFrame(
            self.window, text=" Avance Creacion de Cilindros ", bootstyle="warning"
        )
        frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        columnas = ["Completos", "Pendientes", "Totales", "% Completos"]

        # nombres de columnas
        for col, columna in enumerate(columnas):
            ttkb.Label(frame, text=columna, font=self.FONTS[4]).grid(
                column=col, row=1, padx=10, pady=5
            )

        # filas
        ttkb.Label(frame, text=str(data[1])).grid(column=0, row=2)
        ttkb.Label(frame, text=str(data[0] - data[1])).grid(column=1, row=2)
        ttkb.Label(frame, text=str(data[0])).grid(column=2, row=2)
        ttkb.Label(frame, text=f"{data[1]/data[0]:.1%}").grid(column=3, row=2)

        return (data[1], data[0])

    def dashboard_pines(self):

        self.cursor.execute(
            f"SELECT Cilindro from 'L-895185-(5)(21)()(340)' AS t1 JOIN 'P-895185-(5)(21)()(340)-005' AS t2 ON t1.Secuencia = t2.Secuencia WHERE FabricadoCilindro > 0"
        )
        cil_ok = "".join([i[0] for i in self.cursor.fetchall()])

        self.cursor.execute(
            f"SELECT Cilindro from 'L-895185-(5)(21)()(340)' AS t1 JOIN 'P-895185-(5)(21)()(340)-005' AS t2 ON t1.Secuencia = t2.Secuencia"
        )
        cil_tot = "".join([i[0] for i in self.cursor.fetchall()])

        pines = [(cil_ok.count(str(i)), cil_tot.count(str(i))) for i in range(1, 9)]

        frame = ttkb.LabelFrame(self.window, text=" Uso de Pines ", bootstyle="danger")
        frame.grid(row=0, column=2, columnspan=2, rowspan=2, padx=10, pady=5)

        columnas = ["Tamaño Pin", "Completos", "Pendientes", "Totales", "% Completos"]

        # nombres de columnas
        for col, columna in enumerate(columnas):
            ttkb.Label(frame, text=columna, font=self.FONTS[4]).grid(
                column=col, row=1, padx=10, pady=5
            )

        # filas
        totales = [0, 0, 0, 0]
        for row, pines in enumerate(pines, start=2):
            ttkb.Label(frame, text=str(row - 1)).grid(column=0, row=row)
            ttkb.Label(frame, text=str(pines[0])).grid(column=1, row=row)
            ttkb.Label(frame, text=str(pines[1] - pines[0])).grid(column=2, row=row)
            ttkb.Label(frame, text=str(pines[1])).grid(column=3, row=row)
            ttkb.Label(frame, text=f"{pines[0]/pines[1] if pines[1] else 1:.1%}").grid(
                column=4, row=row
            )
            totales[0] += pines[0]
            totales[1] += pines[1]
            totales[2] += pines[0] + pines[1]

        # fila totales
        totales[3] = f"{totales[0] / (totales[0]+totales[1]):.1%}"
        totales = ["Total"] + totales
        for col, columna in enumerate(totales):
            ttkb.Label(frame, text=str(columna), font=self.FONTS[4]).grid(
                column=col, row=12, padx=10
            )

    def dashboard_meters(self, totales_llaves, totales_cils):

        values = (
            totales_llaves[0] / totales_llaves[1],
            totales_cils[0] / totales_cils[1],
            (totales_llaves[0] + totales_cils[0])
            / (totales_llaves[1] + totales_cils[1]),
        )

        frame = ttkb.LabelFrame(
            self.window, bootstyle="primary", text=" Avance Acumulado del Proyecto "
        )
        frame.grid(row=2, column=0, columnspan=4, padx=10, pady=70)

        for i, txt in enumerate(["Llaves", "Cilindros", "Total"]):

            ttkb.Meter(
                frame,
                metersize=180,
                padding=5,
                amountused=round(values[i] * 100, 1),
                bootstyle="info",
                subtextstyle="success",
                textright="%",
                subtext=txt,
            ).grid(row=0, column=i, padx=40, pady=10)

    def editar_llave(self):

        # extraer informacion necesaria de la bd
        self.cursor.execute(
            f"SELECT Secuencia, Copias, FabricadoLlaveCopias, CodigoLlave from 'P-895185-(5)(21)()(340)-005'"
        )
        self.llaves_data = {
            i[0]: [str(i[1]), str(i[2]), str(i[3])] for i in self.cursor.fetchall()
        }

        # crear frame que contiene todos los widgets
        frame = ttkb.LabelFrame(
            self.window, border=2, text=" Armado de Llaves ", bootstyle="primary"
        )
        frame.grid(row=3, column=0, columnspan=2, padx=10, pady=30)

        # crear drop-down de lista de todas las llaves
        values = list(self.llaves_data.keys())
        if not self.secuencia_elegida:
            self.secuencia_elegida = StringVar(value=values[0])

        self.dropdown_secuencias = ttkb.OptionMenu(
            frame,
            self.secuencia_elegida,
            *values,
            command=lambda x: self.dibujar_llave(self.llaves_data[x]),
        )
        self.dropdown_secuencias.grid(row=1, column=0, pady=10)

        # crear canvas donde se dibuja la llave segun el codigo
        self.canvas1 = ttkb.Canvas(frame, width=500, height=200, bg="yellow")
        self.canvas1.grid(row=2, column=0, columnspan=2, pady=50, padx=20)

        self.avance = ttkb.Label(frame)
        self.avance.grid(row=1, column=1, pady=10, padx=10)

        # crear frame con botones de sumar o restar copias listas y pasar al siguiente codigo
        button_frame = ttkb.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        self.boton_copia_lista = ttkb.Button(
            button_frame,
            text="Copia lista",
            command=lambda: self.copia_lista(
                self.llaves_data[self.secuencia_elegida.get()]
            ),
            bootstyle="success",
        )
        self.boton_copia_lista.grid(row=0, column=0, padx=20, pady=10)
        self.boton_eliminar_copia = ttkb.Button(
            button_frame,
            text="Eliminar copia",
            command=lambda: self.eliminar_copia(
                self.llaves_data[self.secuencia_elegida.get()]
            ),
            bootstyle="warning",
        )
        self.boton_eliminar_copia.grid(row=0, column=1, padx=20, pady=10)
        self.boton_siguiente_codigo = ttkb.Button(
            button_frame,
            text="Siguiente código",
            command=self.siguiente_codigo,
            bootstyle="primary",
        )
        self.boton_siguiente_codigo.grid(row=0, column=2, padx=20, pady=10)

        # self.dibujar_llave()

    def dibujar_llave(self, data=None):

        if not data:
            data = self.llaves_data[self.secuencia_elegida.get()]

        # partes fijas de esquema de llave
        points_fixed = [225, 125, 245, 125, 245, 55, 25, 55, 5, 90, 25, 125]
        points_vary = []

        # borrar dibujos y empezar de nuevo
        self.canvas1.delete("all")

        # partes variables de equema de llaves
        for x, diente in enumerate(str(data[2])):
            self.canvas1.create_text(
                46 + (30 * x),
                160,
                text=diente,
                fill="white",
                font=self.FONTS[3],
            )
            points_vary.append(30 + (30 * x))
            points_vary.append(125)
            points_vary.append(45 + (30 * x))
            points_vary.append(125 - 3 * int(diente))

        # union entre partes fija y variable
        points_vary += [215, 125]

        # dibujar llave
        self.canvas1.create_polygon(
            [i for i in points_fixed + points_vary],
            fill="black",
            outline="white",
            width=4,
        )
        self.canvas1.create_line(240, 80, 50, 80, fill="white", width=4)
        self.canvas1.create_oval(
            240, 0, 420, 180, outline="white", fill="black", width=4
        )
        self.canvas1.create_arc(
            390,
            150,
            295,
            30,
            outline="white",
            fill="#222222",
            width=4,
            start=270,
            extent=180,
        )
        self.canvas1.create_text(
            323,
            95,
            text=data[2],
            fill="white",
            font=self.FONTS[4],
            angle=90,
        )

        # extrae llaves fabricadas completas y total de llaves para el codigo elegido
        _total, _completas = int(data[0]), int(data[1])

        if _total == _completas:

            # desactiva boton para mas copias completas
            self.boton_copia_lista["state"] = "disable"
            self.boton_eliminar_copia["state"] = "normal"

            _label_text = f" Copias completas ({_completas})"

        else:

            # desactiva boton para reducir copias si ya esta en 0
            self.boton_eliminar_copia["state"] = (
                "disable" if _completas == 0 else "normal"
            )
            self.boton_copia_lista["state"] = "normal"

            _siguiente = _completas + 1
            _label_text = f"Siguiente copia: {_siguiente} / {_total}"

        # crear texto de copias hechas y totales
        self.avance.config(text=_label_text)

    def copia_lista(self, data):

        # aumenta una copia al total de copias listas
        data[1] = int(data[1]) + 1
        self.cursor.execute(
            f"UPDATE 'P-895185-(5)(21)()(340)-005' SET FabricadoLlaveCopias = {data[1]} WHERE CodigoLlave = '{data[2]}'"
        )
        self.actualizar_dashboard()

    def eliminar_copia(self, data):

        # activa boton de siguiente codigo en caso este desactivado
        self.boton_siguiente_codigo["state"] = "normal"

        # reduce una copia al total de copias listas
        data[1] = int(data[1]) - 1
        self.cursor.execute(
            f"UPDATE 'P-895185-(5)(21)()(340)-005' SET FabricadoLlaveCopias = {data[1]} WHERE CodigoLlave = '{data[2]}'"
        )
        self.actualizar_dashboard()

    def siguiente_codigo(self):
        # extraer informacion necesaria de la bd
        self.cursor.execute(
            f"SELECT Secuencia, Copias, FabricadoLlaveCopias, CodigoLlave from 'P-895185-(5)(21)()(340)-005' WHERE FabricadoLlaveCopias < Copias"
        )
        data = self.cursor.fetchone()

        # si no hay mas llaves pendientes desactivar boton
        if not data:
            self.boton_siguiente_codigo["state"] = "disable"
            return

        # actualizar con primera llave pendiente
        self.secuencia_elegida.set(data[0])
        self.dibujar_llave(data=data[1:])

    def editar_cilindro(self):

        # extraer informacion necesaria de la bd

        self.cursor.execute(
            f"SELECT T1.Secuencia, FabricadoCilindro, Cilindro, CodigoLlave FROM 'P-895185-(5)(21)()(340)-005' AS T1 JOIN '{self.libro_origen}' AS T2 ON T1.Secuencia = T2.Secuencia"
        )
        self.cilindros_data = {i[0]: [i[1], i[2], i[3]] for i in self.cursor.fetchall()}

        # crear frame que contiene todos los widgets
        frame = ttkb.LabelFrame(
            self.window, bootstyle="primary", text=" Armado de Cilindros "
        )
        frame.grid(row=3, column=2, columnspan=2, padx=10, pady=15)

        # crear drop-down de lista de todas las llaves jerarquia K
        values = list(self.cilindros_data.keys())
        if not self.secuencia_elegida2:
            self.secuencia_elegida2 = StringVar(value=values[0])

        self.dropdown_secuencias2 = ttkb.OptionMenu(
            frame,
            self.secuencia_elegida2,
            *values,
            command=lambda x: self.dibujar_cilindro(self.cilindros_data[x]),
        )
        self.dropdown_secuencias2.grid(row=1, column=0, pady=10)

        # crear canvas donde se dibuja el cilindro
        self.canvas2 = ttkb.Canvas(frame, width=500, height=200)
        self.canvas2.grid(row=2, column=0, columnspan=2, pady=50, padx=40)

        self.avance2 = ttkb.Label(frame)
        self.avance2.grid(row=1, column=1, pady=10, padx=10)

        # crear frame con botones de sumar o restar copias listas y pasar al siguiente codigo
        button_frame = ttkb.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)

        self.boton_cil_listo = ttkb.Button(
            button_frame,
            text="Cilindro listo",
            command=lambda: self.cilindro_listo(
                self.cilindros_data[self.secuencia_elegida2.get()]
            ),
            bootstyle="success",
        )
        self.boton_cil_listo.grid(row=0, column=0, padx=20, pady=10)
        self.boton_cil_eliminado = ttkb.Button(
            button_frame,
            text="Eliminar cilindro",
            command=lambda: self.eliminar_cilindro(
                self.cilindros_data[self.secuencia_elegida2.get()]
            ),
            bootstyle="warning",
        )
        self.boton_cil_eliminado.grid(row=0, column=1, padx=20, pady=10)
        self.boton_siguiente_cil = ttkb.Button(
            button_frame,
            text="Siguiente cilindro",
            command=lambda: self.siguiente_cilindro(),
            bootstyle="primary",
        )
        self.boton_siguiente_cil.grid(row=0, column=2, padx=20, pady=10)

        # self.dibujar_cilindro()

    def dibujar_cilindro(self, data=None):

        if not data:
            data = self.cilindros_data[self.secuencia_elegida2.get()]

        self.canvas2.delete("all")

        # Load an image in the script
        self.img = ImageTk.PhotoImage(
            Image.open(os.path.join("static", "cerradura3.png"))
        )

        # Add image to the Canvas Items
        self.canvas2.create_line(50, 0, 350, 0, width=4, fill="white")
        self.canvas2.create_line(50, 200, 350, 200, width=4, fill="white")
        self.canvas2.create_oval(0, 0, 100, 200, outline="white", fill="black", width=4)
        self.canvas2.create_image(50, 100, image=self.img)
        self.canvas2.create_arc(
            300,
            0,
            400,
            200,
            outline="white",
            fill="black",
            width=4,
            start=270,
            extent=180,
            style=ARC,
        )

        # Insert pins
        for x, pinpos in enumerate(data[1].split("]")[:-1]):
            pines = (
                (0, int(pinpos[1:2]))
                if len(pinpos) == 2
                else (int(pinpos[1:2]), int(pinpos[3:5]))
            )
            if pines[0] > 0:
                self.canvas2.create_text(
                    130 + x * 45, 60, text=pines[0], fill="white", font=self.FONTS[5]
                )
            self.canvas2.create_text(
                130 + x * 45, 140, text=pines[1], fill="white", font=self.FONTS[5]
            )

        # extrae si cilindro esta fabricado
        _fabricado = data[0]

        if _fabricado:

            # desactiva boton para mas copias completas
            self.boton_cil_listo["state"] = "disable"
            self.boton_cil_eliminado["state"] = "normal"

            _label_text = f"Cilindro completo"

        else:

            # desactiva boton para reducir copias si ya esta en 0
            self.boton_cil_listo["state"] = "normal"
            self.boton_cil_eliminado["state"] = "disable"

            _label_text = f"Cilindro pendiente"

        # crear texto de copias hechas y totales
        self.avance2.config(text=_label_text)

    def cilindro_listo(self, data):

        # aumenta una copia al total de copias listas
        data[0] += 1
        self.cursor.execute(
            f"UPDATE 'P-895185-(5)(21)()(340)-005' SET FabricadoCilindro = {data[0]} WHERE CodigoLlave = '{data[2]}'"
        )
        self.actualizar_dashboard()

    def eliminar_cilindro(self, data):

        # activa boton de siguiente codigo en caso este desactivado
        self.boton_siguiente_cil["state"] = "normal"

        # reduce una copia al total de copias listas
        data[0] -= 1
        self.cursor.execute(
            f"UPDATE 'P-895185-(5)(21)()(340)-005' SET FabricadoCilindro = {data[0]} WHERE CodigoLlave = '{data[2]}'"
        )
        self.actualizar_dashboard()

    def siguiente_cilindro(self):

        # extraer informacion necesaria de la bd
        self.cursor.execute(
            f"SELECT T1.Secuencia, FabricadoCilindro, Cilindro, CodigoLlave FROM 'P-895185-(5)(21)()(340)-005' AS T1 JOIN '{self.libro_origen}' AS T2 ON T1.Secuencia = T2.Secuencia WHERE FabricadoCilindro = 0 AND Jerarquia = 'K'"
        )
        data = self.cursor.fetchone()

        # si no hay mas llaves pendientes desactivar boton
        if not data:
            self.boton_siguiente_codigo["state"] = "disable"
            return

        # actualizar con primera llave pendiente
        self.secuencia_elegida2.set(data[0])
        self.dibujar_cilindro(data=data[1:])
