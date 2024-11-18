from tkinter import StringVar
import ttkbootstrap as ttkb
from pprint import pprint


def gui(frames, cursor, conn, nombre_proyecto):

    cursor.execute(f"SELECT * FROM '{nombre_proyecto}'")
    data = cursor.fetchall()

    secuencias = [i[1] for i in data]
    secuencia_elegida = StringVar(value=secuencias[0])

    ttkb.OptionMenu(
        frames["bottom"],
        secuencia_elegida,
        "GGMK",
        *secuencias,
        command=lambda x: eleccion_secuencia(x),
    ).grid(column=0, row=0)

    opciones = {
        "cod_puerta": ["Tipo A", "Tipo B", "Tipo C"],
        "tip_puerta": ["Puerta A", "Puerta B", "Puerta C"],
    }

    rptas = asigna_valor_campos(cursor, nombre_proyecto, secuencia_elegida.get())

    campos = [
        ("Nombre", 1, ttkb.Entry(frames["bottom"], textvariable=rptas["nombre"])),
        (
            "Copias",
            1,
            ttkb.Spinbox(
                frames["bottom"], from_=0, to=999, textvariable=rptas["copias"]
            ),
        ),
        (
            "CodigoPuerta",
            1,
            ttkb.OptionMenu(
                frames["bottom"],
                rptas["cod_puerta"],
                "",
                *opciones["cod_puerta"],
            ),
        ),
        (
            "TipoPuerta",
            1,
            ttkb.OptionMenu(
                frames["bottom"],
                rptas["tip_puerta"],
                "",
                *opciones["tip_puerta"],
            ),
        ),
        (
            "TipoCerradura",
            1,
            ttkb.OptionMenu(
                frames["bottom"],
                rptas["tip_cerr"],
                "",
                *opciones["cod_puerta"],
            ),
        ),
        ("Zona1", 2, ttkb.Entry(frames["bottom"], textvariable=rptas["zona1"])),
        ("Zona2", 2, ttkb.Entry(frames["bottom"], textvariable=rptas["zona2"])),
        ("Zona3", 2, ttkb.Entry(frames["bottom"], textvariable=rptas["zona3"])),
        ("Zona4", 2, ttkb.Entry(frames["bottom"], textvariable=rptas["zona4"])),
        (
            "ZonaCodigo",
            2,
            ttkb.Entry(frames["bottom"], textvariable=rptas["zona_cod"]),
        ),
        ("Notas", 3, ttkb.Entry(frames["bottom"], textvariable=rptas["notas"])),
    ]

    cols = [0] * 10
    for campo in campos:
        ttkb.Label(frames["bottom"], text=campo[0]).grid(
            column=(campo[1] * 2) - 1, row=cols[campo[1]]
        )
        campo[2].grid(column=(campo[1] * 2), row=cols[campo[1]], pady=5, padx=10)

        cols[campo[1]] += 1

    ttkb.Button(
        frames["bottom"],
        text="Guardar",
        command=lambda: boton_grabar(
            secuencia_elegida.get(), rptas, cursor, conn, nombre_proyecto
        ),
        bootstyle="success",
    ).grid(row=0, column=campos[-1][1] * 2 + 1, padx=30, pady=5)

    # empezar con los botones de edicion inactivos
    lock_frame(frames["bottom"])


def boton_grabar(secuencia_elegida, rptas, cursor, conn, nombre_proyecto):

    cursor.execute(
        f"""UPDATE '{nombre_proyecto}'
            SET Nombre='{rptas["nombre"].get()}',
            Copias = {rptas["copias"].get()},
            CodigoPuerta = '{rptas["cod_puerta"].get()}',
            TipoPuerta = '{rptas["tip_puerta"].get()}', 
            TipoCerradura = '{rptas["tip_cerr"].get()}', 
            Zona1 = '{rptas["zona1"].get()}', 
            Zona2 = '{rptas["zona2"].get()}', 
            Zona3 = '{rptas["zona3"].get()}', 
            Zona4 = '{rptas["zona4"].get()}', 
            ZonaCodigo = '{rptas["zona_cod"].get()}', 
            Notas = '{rptas["notas"].get()}' 
            WHERE 
            Secuencia = '{secuencia_elegida}'"""
    )

    conn.commit()


def asigna_valor_campos(cursor, nombre_proyecto, secuencia_elegida):
    cursor.execute(
        f"SELECT * FROM '{nombre_proyecto}' WHERE Secuencia = '{secuencia_elegida}'"
    )
    r = cursor.fetchone()

    return {
        "nombre": StringVar(value=r[2] if r[2] else ""),
        "copias": StringVar(value=r[5]),
        "cod_puerta": StringVar(value=r[6] if r[6] else ""),
        "tip_puerta": StringVar(value=r[7] if r[7] else ""),
        "tip_cerr": StringVar(value=r[8] if r[8] else ""),
        "zona1": StringVar(value=r[9] if r[9] else ""),
        "zona2": StringVar(value=r[10] if r[10] else ""),
        "zona3": StringVar(value=r[11] if r[11] else ""),
        "zona4": StringVar(value=r[12] if r[12] else ""),
        "zona_cod": StringVar(value=r[13] if r[13] else ""),
        "notas": StringVar(value=r[14] if r[14] else ""),
    }


def lock_frame(frame, unlock=False):
    for widget in frame.winfo_children():
        if unlock:
            widget.config(state="normal")
        else:
            widget.config(state="disabled")
