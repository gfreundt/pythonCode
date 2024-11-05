from copy import deepcopy as copy
from tkinter import PhotoImage, StringVar
import ttkbootstrap as ttkb
from pprint import pprint
from datetime import datetime as dt
import os


def gui(main):

    window = ttkb.Toplevel()
    winx, winy = (1200, 900)
    x = main.win_posx + 150
    y = main.win_posy + 150
    window.geometry(f"{winx}x{winy}+{x}+{y}")
    window.title("Fabrica de Proyecto")
    window.iconphoto(False, PhotoImage(file=os.path.join("static", "key1.png")))

    frame_llaves = ttkb.Frame(window)
    frame_cilindros = ttkb.Frame(window)
    frame_pines = ttkb.Frame(window)
    frame_meters = [ttkb.Frame(window) for _ in range(4)]
    frame_bottom = ttkb.Frame(window)

    frame_llaves.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
    frame_cilindros.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
    frame_pines.grid(row=0, column=2, columnspan=2, rowspan=2, padx=10, pady=5)
    for i in range(4):
        frame_meters[i].grid(row=2, column=i)
    frame_bottom.grid(row=3, column=0, columnspan=4, padx=10, pady=5)

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

    llaves(frame=frame_llaves, data=data_llaves)
    pines(frame=frame_pines, pines=data_pines)
    cilindros(frame=frame_cilindros, cilindros=data_cilindros)
    meters(frames=frame_meters, data=data_meters)

    # frame input
    ttkb.Label(frame_bottom, text="Avancemos...").pack()


def llaves(frame, data):

    # frame llaves
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


def cilindros(frame, cilindros):
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


def pines(frame, pines):

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


def meters(frames, data):

    for i, frame in enumerate(frames):

        ttkb.Meter(
            frame,
            metersize=180,
            padding=5,
            amountused=data[i] * 100,
        ).pack()
