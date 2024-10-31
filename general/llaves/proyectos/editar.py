from tkinter import StringVar
import ttkbootstrap as ttkb


def gui(frames, cursor, nombre_proyecto):

    lock_frame(frames["top"])

    cursor.execute(f"SELECT * FROM '{nombre_proyecto}'")
    data = cursor.fetchall()

    secuencias = [i[1] for i in data]
    secuencia_elegida = StringVar(value=secuencias[0])

    ttkb.OptionMenu(frames["bottom"], secuencia_elegida, *secuencias).grid(
        column=0, row=0
    )

    opciones = {"cod_puerta": ["Tipo A", "Tipo A", "Tipo B", "Tipo C"]}

    rptas = asigna_valor_campos(cursor, nombre_proyecto, secuencia_elegida.get())

    campos = [
        ("Nombre", 1, ttkb.Entry(frames["bottom"], textvariable=rptas["nombre"])),
        (
            "Copias",
            1,
            ttkb.Spinbox(
                frames["bottom"], from_=0, to=1000, textvariable=rptas["copias"]
            ),
        ),
        (
            "CodigoPuerta",
            1,
            ttkb.OptionMenu(
                frames["bottom"], rptas["cod_puerta"], *opciones["cod_puerta"]
            ),
        ),
        (
            "TipoPuerta",
            1,
            ttkb.OptionMenu(
                frames["bottom"], rptas["tip_puerta"], *opciones["cod_puerta"]
            ),
        ),
        (
            "TipoCerradura",
            1,
            ttkb.OptionMenu(
                frames["bottom"], rptas["tip_cerr"], *opciones["cod_puerta"]
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
            padx=7, pady=5, column=(campo[1] * 2) - 1, row=cols[campo[1]]
        )
        campo[2].grid(column=(campo[1] * 2), row=cols[campo[1]])

        cols[campo[1]] += 1

    ttkb.Button(
        frames["bottom"],
        text="Guardar",
        command=lambda: boton_grabar(secuencia_elegida.get(), rptas, nombre_proyecto),
        bootstyle="success",
    ).grid(row=0, column=campos[-1][1] * 2 + 1, padx=30, pady=5)
    ttkb.Button(
        frames["bottom"],
        text="Regresar",
        command=lambda: boton_regresar(frames),
        bootstyle="warning",
    ).grid(row=1, column=campos[-1][1] * 2 + 1, padx=30, pady=5)


def boton_grabar(secuencia_elegida, rptas, nombre_proyecto):
    for k, v in rptas.items():
        print(v.get())


def boton_regresar(frames):
    lock_frame(frames["bottom"])
    lock_frame(frames["top"], unlock=True)


def asigna_valor_campos(cursor, nombre_proyecto, secuencia_elegida):
    cursor.execute(
        f"SELECT * FROM '{nombre_proyecto}' WHERE Secuencia = '{secuencia_elegida}'"
    )
    r = cursor.fetchone()

    return {
        "nombre": StringVar(value=r[2] if r[2] else ""),
        "copias": StringVar(value=r[3]),
        "cod_puerta": StringVar(value=r[4] if r[4] else ""),
        "tip_puerta": StringVar(value=r[5] if r[5] else ""),
        "tip_cerr": StringVar(value=r[6] if r[6] else ""),
        "zona1": StringVar(value=r[7] if r[7] else ""),
        "zona2": StringVar(value=r[8] if r[8] else ""),
        "zona3": StringVar(value=r[9] if r[9] else ""),
        "zona4": StringVar(value=r[10] if r[10] else ""),
        "zona_cod": StringVar(value=r[11] if r[11] else ""),
        "notas": StringVar(value=r[12] if r[12] else ""),
    }


def lock_frame(frame, unlock=False):
    for widget in frame.winfo_children():
        if unlock:
            widget.config(state="normal")
        else:
            widget.config(state="disabled")
