from tkinter import PhotoImage, END
import ttkbootstrap as ttkb
from ttkbootstrap.tableview import Tableview
import os
import libros.visor


def gui(main):

    # main.window.withdraw()

    window = ttkb.Toplevel()
    window.geometry(f"1300x{int(int(window.winfo_screenheight())*.45)}+400+500")
    window.title("Cargar Libro")
    window.iconphoto(False, PhotoImage(file=os.path.join("static", "key1.png")))

    # GUI - Bottom Frame: botones del menu
    bottom_frame = ttkb.Frame(window)

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
        height=min(30, len(row_data) + 1),
        bootstyle="darkly",
    )

    dt.pack(padx=20, pady=30)

    # alinea los titulos de columna y los campos al medio
    for col in range(10):
        dt.align_heading_center(cid=col)
        dt.align_column_center(cid=col)

    # crea y coloca botones
    ttkb.Button(
        bottom_frame,
        text="Seleccionar",
        command=lambda: seleccion(
            window,
            dt,
            cursor=main.cursor,
            previous_window=main.window,
        ),
        bootstyle="success",
    ).grid(row=0, column=0, pady=20)
    ttkb.Button(
        bottom_frame,
        text="Regresar",
        command=lambda: regresar(main, window),
        bootstyle="warning",
    ).grid(row=0, column=1, padx=30)

    bottom_frame.pack(pady=10)


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

    for i, m in enumerate(data):
        for j, n in enumerate(m):
            # elimina cero
            if n == 0:
                new_data[i][j] = ""
            # inserta separador de miles en cifras
            if type(n) is int:
                new_data[i][j] = f"{data[i][j]:,}"

    return new_data
