from tkinter import END
import ttkbootstrap as ttkb
from ttkbootstrap.tableview import Tableview
import libros.visor


def gui(main):

    main.window.withdraw()

    window = ttkb.Toplevel()
    window.geometry("1900x1300")

    main.cursor.execute("SELECT * FROM libros")

    col_data = [
        "Codigo",
        "GGMK",
        "Formato",
        "Nombre",
        "Notas",
        "Creacion",
        "GMKs",
        "MKs",
        "SMKs",
        "Ks",
    ]

    row_data = aplica_formato(main.cursor.fetchall())

    dt = Tableview(
        window,
        coldata=col_data,
        rowdata=row_data,
        autofit=True,
        autoalign=True,
        height=min(60, len(row_data)),
    )

    dt.pack(padx=20, pady=10)

    # crea y coloca botones
    ttkb.Button(
        window,
        text="Seleccionar",
        command=lambda: seleccion(
            window, dt, cursor=main.cursor, previous_window=main.window
        ),
    ).pack(pady=20)
    ttkb.Button(window, text="Regresar", command=lambda: regresar(main, window)).pack(
        pady=20
    )


def regresar(main, window):
    window.destroy()
    main.window.deiconify()


def seleccion(window, dt, cursor, previous_window):

    selected = dt.get_rows(selected=True)
    window.destroy()
    libros.visor.mostrar(
        cursor=cursor,
        nombre_tabla=selected[0].values[0],
        main_window=previous_window,
    )


def aplica_formato(data):
    new_data = [list(i) for i in data]

    # elimina cero
    for i, m in enumerate(data):
        for j, n in enumerate(m):
            if n == 0:
                new_data[i][j] = ""

    return new_data