from tkinter import IntVar, END
import ttkbootstrap as ttkb
from ttkbootstrap.tableview import Tableview
from datetime import datetime as dt
import time


class Cargar:

    def __init__(self, previous):

        self.cursor = previous.cursor
        self.conn = previous.conn

    def gui(self, previous):

        window = ttkb.Toplevel()
        window.geometry("1400x1300")

        cursor.execute("SELECT * FROM proyectos")

        col_data = [
            "Codigo",
            "Libro Origen",
            "GGMK",
            "Nombre",
            "Notas",
            "Creacion",
            "GMKs",
            "MKs",
            "SMKs",
            "Ks",
        ]

        row_data = aplica_formato(cursor.fetchall())

        dt_view = Tableview(
            window,
            coldata=col_data,
            rowdata=row_data,
            autofit=True,
            autoalign=True,
            height=min(60, len(row_data)),
        )

        dt_view.pack(padx=20, pady=10)

        # crea y coloca botones
        ttkb.Button(
            window,
            text="Seleccionar",
            command=lambda: seleccionar(
                main_window=main_window,
                this_window=window,
                dt_view=dt_view,
                cursor=cursor,
                conn=conn,
            ),
        ).pack(pady=20)
        ttkb.Button(window, text="Regresar", command=lambda: regresar(window)).pack(
            pady=20
        )

    def aplica_formato(data):
        new_data = [list(i) for i in data]

        # elimina cero
        for i, m in enumerate(data):
            for j, n in enumerate(m):
                if n == 0:
                    new_data[i][j] = ""

        return new_data

    def seleccionar(main_window, this_window, dt_view, cursor, conn):
        selected = dt_view.get_rows(selected=True)
        this_window.destroy()
        proyectos.visor.mostrar(
            cursor=cursor,
            conn=conn,
            nombre_proyecto=selected[0].values[0],
            nombre_libro=selected[0].values[1],
            main_window=main_window,
        )

    def regresar(window):
        window.destroy()
