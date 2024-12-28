from tkinter import StringVar, END
import ttkbootstrap as ttkb
from pprint import pprint


class Editar:

    def __init__(self, previous):
        self.cursor = previous.cursor
        self.conn = previous.conn
        self.nombre_proyecto = previous.nombre_proyecto

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

        self.cursor.execute("SELECT * FROM 'CodigosPuertas'")
        _cp = [i[0] for i in self.cursor.fetchall()]

        self.cursor.execute("SELECT * FROM 'TiposPuertas'")
        _tp = [i[0] for i in self.cursor.fetchall()]

        self.cursor.execute("SELECT * FROM 'TiposCerraduras'")
        _tc = [i[0] for i in self.cursor.fetchall()]

        self.cursor.execute(
            f"SELECT NombreZona, ZonaID FROM 'Zonas' WHERE NombreProyecto = '{self.nombre_proyecto}'"
        )
        _data = self.cursor.fetchall()
        _nz = [i[0] for i in _data]
        _ids = [i[1] for i in _data]

        print("ppp", _ids)

        _zo = []
        for id in _ids:
            self.cursor.execute(
                f"SELECT Opcion FROM 'ZonasOpciones' WHERE ZonaID_FK = {id}"
            )
            _zo.append([""] + [i[0] for i in self.cursor.fetchall()])

        opciones = {
            "tipo_puerta": [""] + _tp,
            "codigo_puerta": [""] + _cp,
            "tipo_cerradura": [""] + _tc,
            "zonas": _zo,
        }

        print(opciones)
        print(*opciones["zonas"][1])

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
                    *opciones["codigo_puerta"],
                ),
            ),
            (
                "TipoPuerta",
                1,
                ttkb.OptionMenu(
                    frame,
                    self.rptas[3],
                    *opciones["tipo_puerta"],
                ),
            ),
            (
                "TipoCerradura",
                1,
                ttkb.OptionMenu(
                    frame,
                    self.rptas[4],
                    *opciones["tipo_cerradura"],
                ),
            ),
            (_nz[0], 2, ttkb.OptionMenu(frame, self.rptas[5], *opciones["zonas"][0])),
            (_nz[1], 2, ttkb.OptionMenu(frame, self.rptas[6], *opciones["zonas"][1])),
            (_nz[2], 2, ttkb.OptionMenu(frame, self.rptas[7], *opciones["zonas"][2])),
            (_nz[3], 2, ttkb.OptionMenu(frame, self.rptas[8], *opciones["zonas"][3])),
            (_nz[4], 2, ttkb.OptionMenu(frame, self.rptas[9], *opciones["zonas"][4])),
        ]
        #     ("Notas", 3, ttkb.Entry(frame, self.rptas[10])),
        # ]

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

        # empezar con campos para editar bloqueados
        self.lock_frame()

    def boton_grabar(self):

        self.grabar()
        self.lock_frame()

    def grabar(self):

        self.cursor.execute(
            f"""UPDATE '{self.nombre_proyecto}'
                SET Nombre = ?,
                Copias = ?,
                CodigoPuerta = ?,
                TipoPuerta = ?, 
                TipoCerradura = ?, 
                Zona1 = ?, 
                Zona2 = ?, 
                Zona3 = ?, 
                Zona4 = ?, 
                Zona5 = ?, 
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
                Zona5,
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
