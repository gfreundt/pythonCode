from copy import deepcopy as copy
from tkinter import PhotoImage, StringVar
import ttkbootstrap as ttkb
from pprint import pprint
from datetime import datetime as dt
import os


def gui(main):

    FONTS = (
        "Helvetica 10",
        "Helvetica 12",
        "Helvetica 12 bold",
        "Helvetica 15 bold",
        "Helvetica 10 bold",
    )

    window = ttkb.Toplevel()
    winx, winy = (1250, 1400)
    x = main.win_posx + 20
    y = main.win_posy + 20
    window.geometry(f"{winx}x{winy}+{x}+{y}")
    window.title("Fabrica de Proyecto")
    window.iconphoto(False, PhotoImage(file=os.path.join("static", "key1.png")))

    main.cursor.execute("SELECT * FROM 'P-895185-(5)(21)()(340)-000'")
    toda_data = main.cursor.fetchall()

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
    ]
    data_cilindros = (199, 87)
    data_meters = (0.23, 0.65, 0.87, 0.12)

    # activar todas las partes del dashboard
    llaves(window, data=toda_data, FONTS=FONTS, main=main)
    pines(window, pines=data_pines, FONTS=FONTS)
    cilindros(window, cilindros=data_cilindros, FONTS=FONTS)
    meters(window, data=data_meters, FONTS=FONTS)
    editar_llave(window, data=None, FONTS=FONTS)
    editar_cilindro(window, data=None, FONTS=FONTS)


def llaves(window, data, FONTS, main):

    main.cursor.execute(
        "SELECT sum(copias)  FROM 'P-895185-(5)(21)()(340)-000' WHERE Secuencia LIKE 'K-%'"
    )

    data = {"GGMK": (1, 0), "GMK": (7, 3), "MK": (11, 2), "K": (108, 12)}

    frame = ttkb.LabelFrame(
        window, bootstyle="success", text=" Avance Creacion de Llaves "
    )
    frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

    # ttkb.Label(frame, text="Avance Creacion de Llaves", font=FONTS[2]).grid(
    #     row=0, column=0, columnspan=5, pady=5
    # )

    columnas = ["Nivel de Llave", "Completas", "Pendientes", "Totales", "% Completas"]

    # nombres de columnas
    for col, columna in enumerate(columnas):
        ttkb.Label(frame, text=columna, font=FONTS[4]).grid(
            column=col, row=1, padx=10, pady=5
        )

    # filas
    totales = [0, 0, 0, 0]
    for row, (fila, data) in enumerate(data.items(), start=2):
        ttkb.Label(frame, text=fila, font=FONTS[0]).grid(column=0, row=row)
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
        ttkb.Label(frame, text=str(columna), font=FONTS[4]).grid(
            column=col, row=6, padx=10
        )


def cilindros(window, cilindros, FONTS):

    frame = ttkb.LabelFrame(
        window, text=" Avance Creacion de Cilindros ", bootstyle="warning"
    )
    frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    columnas = ["Completos", "Pendientes", "Totales", "% Completos"]

    # nombres de columnas
    for col, columna in enumerate(columnas):
        ttkb.Label(frame, text=columna, font=FONTS[4]).grid(
            column=col, row=1, padx=10, pady=5
        )

    # filas
    ttkb.Label(frame, text=str(cilindros[0])).grid(column=0, row=2)
    ttkb.Label(frame, text=str(cilindros[1])).grid(column=1, row=2)
    ttkb.Label(frame, text=str(cilindros[0] + cilindros[1])).grid(column=2, row=2)
    ttkb.Label(frame, text=f"{cilindros[0]/(cilindros[0]+cilindros[1]):.1%}").grid(
        column=3, row=2
    )


def pines(window, pines, FONTS):

    frame = ttkb.LabelFrame(window, text=" Uso de Pines ", bootstyle="danger")
    frame.grid(row=0, column=2, columnspan=2, rowspan=2, padx=10, pady=5)

    columnas = ["Tamaño Pin", "Completos", "Pendientes", "Totales", "% Completos"]

    # nombres de columnas
    for col, columna in enumerate(columnas):
        ttkb.Label(frame, text=columna).grid(column=col, row=1, padx=10, pady=5)

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


def meters(window, data, FONTS):

    frame = ttkb.LabelFrame(
        window, bootstyle="primary", text=" Avance Acumulado del Proyecto "
    )
    frame.grid(row=2, column=0, columnspan=4, padx=10, pady=70)

    for i, txt in enumerate(["Llaves", "Cilindros", "Total"]):

        ttkb.Meter(
            frame,
            metersize=180,
            padding=5,
            amountused=data[i] * 100,
            bootstyle="info",
            subtextstyle="success",
            textright="%",
            subtext=txt,
        ).grid(row=0, column=i, padx=40, pady=10)


def editar_llave(window, data, FONTS):

    frame = ttkb.LabelFrame(
        window, border=2, text=" Armado de Llaves ", bootstyle="primary"
    )
    frame.grid(row=3, column=0, columnspan=2, padx=10, pady=30)

    values = ["K-001-002-003", "K-001-002-002", "K-001-002-004"]
    v = StringVar(value=values[0])
    ttkb.OptionMenu(frame, v, *values).grid(row=1, column=0, pady=10)

    codigo = "135739"

    canvas = ttkb.Canvas(frame, width=500, height=200, bg="yellow")
    canvas.grid(row=2, column=0, columnspan=2, pady=20)
    FACTOR = 1
    points_fixed = [10, 21, 0, 14, 10, 7, 70, 7, 90, 0, 110, 14, 90, 21, 70, 21]
    points_fixed = [80, 4, 10, 4, 0, 22, 10, 34]

    points_fixed = [25, 125, 5, 90, 25, 55, 245, 55, 245, 125, 225, 125]
    points_fixed = [225, 125, 245, 125, 245, 55, 25, 55, 5, 90, 25, 125]

    points_vary = []
    for x, diente in enumerate(codigo):
        canvas.create_text(
            46 + (30 * x),
            160,
            text=diente,
            fill="white",
            font=("Helvetica 15 bold"),
        )
        points_vary.append(30 + (30 * x))
        points_vary.append(125)
        points_vary.append(45 + (30 * x))
        points_vary.append(125 - 3 * int(diente))
    points_vary += [215, 125]

    canvas.create_polygon(
        [i * FACTOR for i in points_fixed + points_vary],
        fill="black",
        outline="white",
        width=4,
    )
    canvas.create_line(240, 80, 50, 80, fill="white", width=4)
    canvas.create_oval(240, 0, 420, 180, outline="white", fill="black", width=4)
    canvas.create_arc(
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

    canvas.create_text(
        323,
        95,
        text=codigo,
        fill="white",
        font=("Helvetica 10 bold"),
        angle=90,
    )


def editar_cilindro(window, data, FONTS):

    frame = ttkb.LabelFrame(window, bootstyle="primary", text=" Armado de Cilindros ")
    frame.grid(row=3, column=2, columnspan=2, padx=10, pady=15)
    ttkb.Label(frame, text="right").pack()
