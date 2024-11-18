from copy import deepcopy as copy
from tkinter import PhotoImage, StringVar, ARC
from PIL import Image, ImageTk
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
        "Helvetica 20 bold",
    )

    window = ttkb.Toplevel()
    winx, winy = (1350, 1500)
    x = main.win_posx - 120
    y = main.win_posy - 120
    window.geometry(f"{winx}x{winy}+{x}+{y}")
    window.title("Fabrica de Proyecto")
    window.iconphoto(False, PhotoImage(file=os.path.join("static", "key1.png")))

    # activar todas las partes del dashboard
    _llaves = dashboard_llaves(window, FONTS=FONTS, main=main)
    _cils = dashboard_cilindros(window, FONTS=FONTS, main=main)
    dashboard_pines(window, FONTS=FONTS, main=main)
    dashboard_meters(window, data=(_llaves, _cils), FONTS=FONTS)
    editar_llave(window, data=None, FONTS=FONTS, main=main)
    editar_cilindro(window, data=None, FONTS=FONTS, main=main)
    ttkb.Button(
        window,
        text="Finalizar",
        command=lambda: boton_regresar(window),
        bootstyle="danger",
    ).grid(row=4, column=0, columnspan=4, pady=50)


def boton_regresar(window):
    window.destroy()


def dashboard_llaves(window, FONTS, main):

    data = {}

    for jerarquia in ("GGMK", "GMK", "MK", "K"):

        main.cursor.execute(
            f"SELECT SUM(copias), SUM(FabricadoLlaveCopias) FROM 'P-895185-(5)(21)()(340)-003' WHERE Jerarquia = '{jerarquia}'"
        )
        data.update({jerarquia: main.cursor.fetchone()})

    frame = ttkb.LabelFrame(
        window, bootstyle="success", text=" Avance Creacion de Llaves "
    )
    frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

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
        ttkb.Label(frame, text=str(columna), font=FONTS[4]).grid(
            column=col, row=6, padx=10
        )

    return (totales[1], totales[3])


def dashboard_cilindros(window, FONTS, main):

    main.cursor.execute(
        f"SELECT COUNT(*), SUM(FabricadoCilindro) FROM 'P-895185-(5)(21)()(340)-003' WHERE Jerarquia = 'K'"
    )
    data = main.cursor.fetchone()

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
    ttkb.Label(frame, text=str(data[1])).grid(column=0, row=2)
    ttkb.Label(frame, text=str(data[0] - data[1])).grid(column=1, row=2)
    ttkb.Label(frame, text=str(data[0])).grid(column=2, row=2)
    ttkb.Label(frame, text=f"{data[1]/data[0]:.1%}").grid(column=3, row=2)

    return (data[1], data[0])


def dashboard_pines(window, FONTS, main):

    main.cursor.execute(
        f"SELECT Cilindro from 'L-895185-(5)(21)()(340)' AS t1 JOIN 'P-895185-(5)(21)()(340)-003' AS t2 ON t1.Secuencia = t2.Secuencia WHERE FabricadoCilindro > 0"
    )
    cil_ok = "".join([i[0] for i in main.cursor.fetchall()])

    main.cursor.execute(
        f"SELECT Cilindro from 'L-895185-(5)(21)()(340)' AS t1 JOIN 'P-895185-(5)(21)()(340)-003' AS t2 ON t1.Secuencia = t2.Secuencia"
    )
    cil_tot = "".join([i[0] for i in main.cursor.fetchall()])

    pines = [(cil_ok.count(str(i)), cil_tot.count(str(i))) for i in range(1, 9)]

    frame = ttkb.LabelFrame(window, text=" Uso de Pines ", bootstyle="danger")
    frame.grid(row=0, column=2, columnspan=2, rowspan=2, padx=10, pady=5)

    columnas = ["Tamaño Pin", "Completos", "Pendientes", "Totales", "% Completos"]

    # nombres de columnas
    for col, columna in enumerate(columnas):
        ttkb.Label(frame, text=columna, font=FONTS[4]).grid(
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
        ttkb.Label(frame, text=str(columna), font=FONTS[4]).grid(
            column=col, row=12, padx=10
        )


def dashboard_meters(window, data, FONTS):

    data = (
        data[0][0] / data[0][1],
        data[1][0] / data[1][1],
        (data[0][0] + data[1][0]) / (data[0][1] + data[1][1]),
    )

    frame = ttkb.LabelFrame(
        window, bootstyle="primary", text=" Avance Acumulado del Proyecto "
    )
    frame.grid(row=2, column=0, columnspan=4, padx=10, pady=70)

    for i, txt in enumerate(["Llaves", "Cilindros", "Total"]):

        ttkb.Meter(
            frame,
            metersize=180,
            padding=5,
            amountused=round(data[i] * 100, 1),
            bootstyle="info",
            subtextstyle="success",
            textright="%",
            subtext=txt,
        ).grid(row=0, column=i, padx=40, pady=10)


def editar_llave(window, data, FONTS, main):

    # extraer informacion necesaria de la bd
    main.cursor.execute(
        f"SELECT Secuencia, Copias, FabricadoLlaveCopias, CodigoLlave from 'P-895185-(5)(21)()(340)-003'"
    )
    data = {i[0]: [str(i[1]), str(i[2]), str(i[3])] for i in main.cursor.fetchall()}

    # crear frame que contiene todos los widgets
    frame = ttkb.LabelFrame(
        window, border=2, text=" Armado de Llaves ", bootstyle="primary"
    )
    frame.grid(row=3, column=0, columnspan=2, padx=10, pady=30)

    # crear drop-down de lista de todas las llaves
    values = list(data.keys())
    v = StringVar(value=values[0])
    ttkb.OptionMenu(
        frame,
        v,
        *values,
        command=lambda x: dibujar_llave(data[x], canvas=canvas, avance=avance),
    ).grid(row=1, column=0, pady=10)

    # crear canvas donde se dibuja la llave segun el codigo
    canvas = ttkb.Canvas(frame, width=500, height=200, bg="yellow")
    canvas.grid(row=2, column=0, columnspan=2, pady=50, padx=20)

    avance = ttkb.Label(frame, text=f"Siguiente Copia:")
    avance.grid(row=1, column=1, pady=10, padx=10)

    # crear frame con botones de sumar o restar copias listas y pasar al siguiente codigo
    button_frame = ttkb.Frame(frame)
    button_frame.grid(row=3, column=0, columnspan=3, pady=20)
    ttkb.Button(
        button_frame,
        text="Copia lista",
        command=lambda: copia_lista(main, data[v.get()], canvas, avance),
        bootstyle="success",
    ).grid(row=0, column=0, padx=20, pady=10)
    ttkb.Button(
        button_frame,
        text="Eliminar copia",
        command=lambda: eliminar_copia(main, data[v.get()], canvas, avance),
        bootstyle="warning",
    ).grid(row=0, column=1, padx=20, pady=10)
    ttkb.Button(
        button_frame,
        text="Siguiente código",
        command=siguiente_codigo,
        bootstyle="primary",
    ).grid(row=0, column=2, padx=20, pady=10)

    dibujar_llave(data=data[v.get()], canvas=canvas, avance=avance)


def dibujar_llave(data, canvas, avance):

    canvas.delete("all")

    FACTOR = 1
    points_fixed = [225, 125, 245, 125, 245, 55, 25, 55, 5, 90, 25, 125]
    points_vary = []

    for x, diente in enumerate(data[2]):
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
        text=data[2],
        fill="white",
        font=("Helvetica 10 bold"),
        angle=90,
    )

    # extraer llaves fabricadas completas y total de llaves para el codigo elegido
    _total, _completas = data[0], data[1]
    if int(_total) == int(_completas):
        _label_text = " Copias completas "
        # TODO: block button
    else:
        _siguiente = int(_completas) + 1
        _label_text = f"Siguiente copia: {_siguiente} / {_total}"

    # crear texto de copias hechas y totales
    avance.config(text=_label_text)


def copia_lista(main, data, canvas, avance):

    data[1] = int(data[1]) + 1
    main.cursor.execute(
        f"UPDATE 'P-895185-(5)(21)()(340)-003' SET FabricadoLlaveCopias = {data[1]} WHERE CodigoLlave = '{data[2]}'"
    )

    dibujar_llave(data=data, canvas=canvas, avance=avance)


def eliminar_copia(main, data, canvas, avance):
    data[1] = int(data[1]) - 1
    main.cursor.execute(
        f"UPDATE 'P-895185-(5)(21)()(340)-003' SET FabricadoLlaveCopias = {data[1]} WHERE CodigoLlave = '{data[2]}'"
    )

    dibujar_llave(data=data, canvas=canvas, avance=avance)


def siguiente_codigo():
    return


def editar_cilindro(window, data, FONTS, main):

    data = "[1:8][2:6][6][4][1:6][1:2]"

    global img

    frame = ttkb.LabelFrame(window, bootstyle="primary", text=" Armado de Cilindros ")
    frame.grid(row=3, column=2, columnspan=2, padx=10, pady=15)

    values = ["K-001-002-003", "K-001-002-002", "K-001-002-004"]
    v = StringVar(value=values[0])
    ttkb.OptionMenu(frame, v, *values).grid(row=1, column=0, pady=10)

    canvas = ttkb.Canvas(frame, width=500, height=200)
    canvas.grid(row=2, column=0, columnspan=2, pady=50, padx=40)

    # Load an image in the script
    img = ImageTk.PhotoImage(Image.open(os.path.join("static", "cerradura3.png")))

    # Add image to the Canvas Items
    canvas.create_line(50, 0, 350, 0, width=4, fill="white")
    canvas.create_line(50, 200, 350, 200, width=4, fill="white")
    canvas.create_oval(0, 0, 100, 200, outline="white", fill="black", width=4)
    canvas.create_image(50, 100, image=img)
    canvas.create_arc(
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
    for x, pinpos in enumerate(data.split("]")[:-1]):
        pines = (
            (0, int(pinpos[1:2]))
            if len(pinpos) == 2
            else (int(pinpos[1:2]), int(pinpos[3:5]))
        )
        if pines[0] > 0:
            canvas.create_text(
                130 + x * 45, 60, text=pines[0], fill="white", font=FONTS[5]
            )
        canvas.create_text(
            130 + x * 45, 140, text=pines[1], fill="white", font=FONTS[5]
        )

    button_frame = ttkb.Frame(frame)
    button_frame.grid(row=3, column=0, columnspan=3, pady=20)

    ttkb.Button(
        button_frame, text="Cilindro listo", command=copia_lista, bootstyle="success"
    ).grid(row=0, column=0, padx=20, pady=10)
    ttkb.Button(
        button_frame,
        text="Eliminar cilindro",
        command=eliminar_copia,
        bootstyle="warning",
    ).grid(row=0, column=1, padx=20, pady=10)
    ttkb.Button(
        button_frame,
        text="Siguiente código",
        command=siguiente_codigo,
        bootstyle="primary",
    ).grid(row=0, column=2, padx=20, pady=10)
