from tkinter import StringVar, END
import ttkbootstrap as ttkb
from pprint import pprint


class Editar:

    def __init__(self, cursor, conn, nombre_proyecto):
        self.cursor = cursor
        self.conn = conn
        self.nombre_proyecto = nombre_proyecto

    def gui(self, frame):

        self.frame = frame

        self.cursor.execute(f"SELECT * FROM '{self.nombre_proyecto}'")
        data = self.cursor.fetchall()

        secuencias = [i[1] for i in data]
        secuencia_elegida = StringVar(value=secuencias[0])

        ttkb.OptionMenu(
            frame,
            secuencia_elegida,
            "GGMK",
            *secuencias,
            command=lambda secuencia_elegida: self.asigna_valor_campos(
                secuencia_elegida
            ),
        ).grid(column=0, row=0)

        opciones = {
            "cod_puerta": ["", "Tipo A", "Tipo B", "Tipo C"],
            "tip_puerta": ["", "Puerta A", "Puerta B", "Puerta C"],
        }

        self.rptas = [StringVar() for _ in range(11)]

        self.campos = [
            ("Nombre", 1, ttkb.Entry(frame, textvariable=self.rptas[0])),
            (
                "Copias",
                1,
                ttkb.Spinbox(frame, from_=0, to=999, textvariable=self.rptas[1]),
            ),
            (
                "CodigoPuerta",
                1,
                ttkb.OptionMenu(
                    frame,
                    self.rptas[2],
                    *opciones["cod_puerta"],
                ),
            ),
            (
                "TipoPuerta",
                1,
                ttkb.OptionMenu(
                    frame,
                    self.rptas[3],
                    *opciones["tip_puerta"],
                ),
            ),
            (
                "TipoCerradura",
                1,
                ttkb.OptionMenu(
                    frame,
                    self.rptas[4],
                    *opciones["cod_puerta"],
                ),
            ),
            ("Zona1", 2, ttkb.Entry(frame, textvariable=self.rptas[5])),
            ("Zona2", 2, ttkb.Entry(frame, textvariable=self.rptas[6])),
            ("Zona3", 2, ttkb.Entry(frame, textvariable=self.rptas[7])),
            ("Zona4", 2, ttkb.Entry(frame, textvariable=self.rptas[8])),
            ("ZonaCodigo", 2, ttkb.Entry(frame, textvariable=self.rptas[9])),
            ("Notas", 3, ttkb.Entry(frame, textvariable=self.rptas[10])),
        ]

        cols = [0] * 10
        for campo in self.campos:
            ttkb.Label(frame, text=campo[0]).grid(
                column=(campo[1] * 2) - 1, row=cols[campo[1]]
            )
            campo[2].grid(column=(campo[1] * 2), row=cols[campo[1]], pady=5, padx=10)

            cols[campo[1]] += 1

        ttkb.Button(
            frame,
            text="Guardar",
            command=lambda: self.boton_grabar(),
            bootstyle="success",
        ).grid(row=0, column=self.campos[-1][1] * 2 + 1, padx=30, pady=5)

        self.secuencia_activa = "GGMK"
        self.asigna_valor_campos(secuencia_elegida="GGMK", initial=True)

    def boton_grabar(self):

        self.grabar()
        self.lock_frame()

    def grabar(self):

        self.cursor.execute(
            f"""UPDATE '{self.nombre_proyecto}'
                SET Nombre=?,
                Copias = ?,
                CodigoPuerta = ?,
                TipoPuerta = ?, 
                TipoCerradura = ?, 
                Zona1 = ?, 
                Zona2 = ?, 
                Zona3 = ?, 
                Zona4 = ?, 
                ZonaCodigo = ?, 
                Notas = ? 
                WHERE 
                Secuencia = '{self.secuencia_activa}'""",
            [i.get() for i in self.rptas],
        )

        self.conn.commit()

    def asigna_valor_campos(self, secuencia_elegida, initial=False):

        # graba valores de registro activo antes de cambiar de registro
        if not initial:
            self.grabar()

        self.cursor.execute(
            f"""SELECT Nombre,
                Copias,
                CodigoPuerta,
                TipoPuerta,
                TipoCerradura,
                Zona1,
                Zona2,
                Zona3,
                Zona4,
                ZonaCodigo,
                Notas
                FROM '{self.nombre_proyecto}'
                WHERE Secuencia = '{secuencia_elegida}'"""
        )

        data = self.cursor.fetchone()

        for indice, _ in enumerate(self.campos):
            self.rptas[indice].set(data[indice] if data[indice] else "")

        self.secuencia_activa = secuencia_elegida

    def lock_frame(self, unlock=False):
        for widget in self.frame.winfo_children():
            if unlock:
                widget.config(state="normal")
            else:
                widget.config(state="disabled")
