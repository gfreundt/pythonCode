from copy import deepcopy as copy
from tkinter import PhotoImage, StringVar
import ttkbootstrap as ttkb
from pprint import pprint
from datetime import datetime as dt
import os


def gui(main):

    window = ttkb.Toplevel()
    winx, winy = (1500, 1400)
    x = main.win_posx + 20
    y = main.win_posy + 20
    window.geometry(f"{winx}x{winy}+{x}+{y}")
    window.title("Fabrica de Proyecto")
    window.iconphoto(False, PhotoImage(file=os.path.join("static", "key1.png")))

    data_llaves = {"GGMK": (1, 0), "GMK": (7, 3), "MK": (11, 2), "K": (108, 12)}

    data_pines = [
        (23, 11),
        (89, 55),
        (109, 11),
        (77, 9),
        (23, 11),
        (89, 55),
        (109, 11),
        (77, 9),
        (23, 11),
        (89, 55),
    ]
    data_cilindros = (199, 87)
    data_meters = (0.23, 0.65, 0.87, 0.12)

    llaves(window, data=data_llaves)
    pines(window, pines=data_pines)
    cilindros(window, cilindros=data_cilindros)
    meters(window, data=data_meters)
    editar(window)


def llaves(window, data):

    frame = ttkb.Frame(window)
    frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

    ttkb.Label(frame, text="Avance Creacion de Llaves").grid(
        row=0, column=0, columnspan=5, pady=5
    )

    columnas = ["Nivel de Llave", "Completas", "Pendientes", "Totales", "% Completas"]

    # nombres de columnas
    for col, columna in enumerate(columnas):
        ttkb.Label(frame, text=columna).grid(column=col, row=1, padx=10)

    # filas
    totales = [0, 0, 0, 0]
    for row, (fila, data) in enumerate(data.items(), start=2):
        ttkb.Label(frame, text=fila).grid(column=0, row=row)
        ttkb.Label(frame, text=str(data[0])).grid(column=1, row=row)
        ttkb.Label(frame, text=str(data[1])).grid(column=2, row=row)
        ttkb.Label(frame, text=str(data[0] + data[1])).grid(column=3, row=row)
        ttkb.Label(frame, text=f"{data[0]/(data[0]+data[1]):.1%}").grid(
            column=4, row=row
        )
        totales[0] += data[0]
        totales[1] += data[1]
        totales[2] += data[0] + data[1]

    # fila totales
    totales[3] = f"{totales[0] / (totales[0]+totales[1]):.1%}"
    totales = ["Total"] + totales
    for col, columna in enumerate(totales):
        ttkb.Label(frame, text=str(columna)).grid(column=col, row=6, padx=10)


def cilindros(window, cilindros):

    frame = ttkb.Frame(window)
    frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    # frame llaves
    ttkb.Label(frame, text="Avance Creacion de Cilindros").grid(
        row=0, column=0, columnspan=5, pady=5
    )

    columnas = ["Completos", "Pendientes", "Totales", "% Completos"]

    # nombres de columnas
    for col, columna in enumerate(columnas):
        ttkb.Label(frame, text=columna).grid(column=col, row=1, padx=10)

    # filas
    ttkb.Label(frame, text=str(cilindros[0])).grid(column=0, row=2)
    ttkb.Label(frame, text=str(cilindros[1])).grid(column=1, row=2)
    ttkb.Label(frame, text=str(cilindros[0] + cilindros[1])).grid(column=2, row=2)
    ttkb.Label(frame, text=f"{cilindros[0]/(cilindros[0]+cilindros[1]):.1%}").grid(
        column=3, row=2
    )


def pines(window, pines):

    frame = ttkb.Frame(window)
    frame.grid(row=0, column=2, columnspan=2, rowspan=2, padx=10, pady=5)

    ttkb.Label(frame, text="Uso de Pines").grid(row=0, column=0, columnspan=5)

    columnas = ["Tamaño Pin", "Completos", "Pendientes", "Totales", "% Completos"]

    # nombres de columnas
    for col, columna in enumerate(columnas):
        ttkb.Label(frame, text=columna).grid(column=col, row=1, padx=10)

    # filas
    totales = [0, 0, 0, 0]
    for row, pines in enumerate(pines, start=2):
        ttkb.Label(frame, text=str(row - 1)).grid(column=0, row=row)
        ttkb.Label(frame, text=str(pines[0])).grid(column=1, row=row)
        ttkb.Label(frame, text=str(pines[1])).grid(column=2, row=row)
        ttkb.Label(frame, text=str(pines[0] + pines[1])).grid(column=3, row=row)
        ttkb.Label(frame, text=f"{pines[0]/(pines[0]+pines[1]):.1%}").grid(
            column=4, row=row
        )
        totales[0] += pines[0]
        totales[1] += pines[1]
        totales[2] += pines[0] + pines[1]

    # fila totales
    totales[3] = f"{totales[0] / (totales[0]+totales[1]):.1%}"
    totales = ["Total"] + totales
    for col, columna in enumerate(totales):
        ttkb.Label(frame, text=str(columna)).grid(column=col, row=12, padx=10)


def meters(window, data):

    frame = ttkb.Frame(window)
    frame.grid(row=2, column=0, columnspan=4, padx=10, pady=5)

    for i in range(3):

        ttkb.Meter(
            frame,
            metersize=180,
            padding=5,
            amountused=data[i] * 100,
        ).grid(row=0, column=i)


def editar(window):

    frame_llave = ttkb.Frame(window)
    frame_llave.grid(row=3, column=0, columnspan=2, padx=10, pady=5)
    ttkb.Label(frame_llave, text="left").grid(row=0, column=0)

    frame_cil = ttkb.Frame(window)
    frame_cil.grid(row=3, column=2, columnspan=2, padx=10, pady=5)
    ttkb.Label(frame_cil, text="right").pack()

    values = ["K-001-002-003", "K-001-002-002", "K-001-002-004"]
    v = StringVar(value=values[0])
    ttkb.OptionMenu(frame_llave, v, *values).grid(row=1, column=0)

    codigo = "453984"

    canvas = ttkb.Canvas(frame_llave, width=500, height=200)
    canvas.grid(row=2, column=0, columnspan=2)
    FACTOR = 4
    points_fixed = [10, 30, 0, 20, 10, 10, 70, 10, 90, 0, 110, 20, 90, 30, 70, 30]
    points_fixed = [70, 30, 90, 30, 110, 20, 90, 0, 70, 10, 10, 10, 0, 20, 10, 30]
    points_vary = []
    for x, diente in enumerate(codigo):
        points_vary.append(10 + (10 * x))
        points_vary.append(30)
        points_vary.append(15 + (10 * x))
        points_vary.append(30 + int(diente))

    canvas.create_polygon(
        [i * FACTOR for i in points_fixed + points_vary], outline="white", width=3
    )
