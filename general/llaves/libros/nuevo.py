from tkinter import PhotoImage, StringVar
import ttkbootstrap as ttkb
from PIL import Image, ImageTk
from datetime import datetime as dt
import os, random
from libros import generador
from herramientas import validaciones
import libros.visor


def gui(main):

    main.window.withdraw()

    # GUI - ventana secundaria
    winx, winy = (900, 400)
    window = ttkb.Toplevel()
    x = main.win_posx + 150
    y = main.win_posy + 150
    window.geometry(f"{winx}x{winy}+{x}+{y}")
    window.title("Crear Nuevo Libro")
    window.iconphoto(False, PhotoImage(file=os.path.join("static", "key1.png")))

    # GUI - Top Frame: logo
    top_frame = ttkb.Frame(window)
    top_frame.pack(pady=10)

    # GUI - Bottom Frame: botones del menu
    bottom_frame = ttkb.Frame(window)
    bottom_frame.pack(pady=10)

    # Top Frame - insertar logo
    image = ImageTk.PhotoImage(
        Image.open(os.path.join("static", "LOGOS-CMYK-10-2048x1160.png")).resize(
            (400, 226)
        )
    )
    ttkb.Label(top_frame, image=image).grid(row=0, column=0, columnspan=3)

    # GUI - capturar informacion de usuario para nuevo libro
    opciones_formato = ["1-1-1-0-4", "1-1-1-0-4", "1-1-2-0-3"]
    formato = StringVar(value=opciones_formato[0])
    codigo_ggmk = StringVar()
    nombre = StringVar()
    notas = StringVar()

    # crear y colocar titulos de campos
    titulos = [
        ttkb.Label(bottom_frame, text="Codigo GGMK: "),
        ttkb.Label(bottom_frame, text="Formato: "),
        ttkb.Label(bottom_frame, text="Nombre del Libro: "),
        ttkb.Label(bottom_frame, text="Notas: "),
    ]

    for y, titulo in enumerate(titulos):
        titulo.grid(row=y, column=0, padx=10, pady=10)

    # crear y colocar espacios para ingresar informacion
    inputs = [
        ttkb.Entry(
            bottom_frame,
            textvariable=codigo_ggmk,
            font=("calibre", 10, "normal"),
        ),
        ttkb.OptionMenu(bottom_frame, formato, *opciones_formato),
        ttkb.Entry(
            bottom_frame,
            textvariable=nombre,
            font=("calibre", 10, "normal"),
        ),
        ttkb.Entry(
            bottom_frame,
            textvariable=notas,
            font=("calibre", 10, "normal"),
        ),
    ]

    for y, inp in enumerate(inputs):
        inp.grid(row=y, column=1, padx=10, pady=10)

    # crear y colocar botones de accion
    ttkb.Button(
        bottom_frame,
        text="Aleatorio",
        command=lambda: ggmk_aleatoria(codigo_ggmk),
    ).grid(row=0, column=2)

    ttkb.Button(
        bottom_frame,
        text="Crear Libro",
        command=lambda: crear(
            inputs=inputs,
            codigo_ggmk=codigo_ggmk.get(),
            formato=formato.get(),
            nombre=nombre.get(),
            notas=notas.get(),
            conn=main.conn,
            cursor=main.cursor,
            previous_window=main.window,
            window=window,
        ),
        bootstyle="success",
    ).grid(row=2, column=3, padx=20, pady=10)

    ttkb.Button(
        bottom_frame,
        text="Regresar",
        command=lambda: regresar(main.window, window),
        bootstyle="warning",
    ).grid(row=3, column=3, padx=20, pady=10)


def crear(**kwargs):

    # revisa que codigo GGMK sea valido
    if validaciones.valida_codigo(kwargs["codigo_ggmk"]):
        kwargs["inputs"][0].configure(bootstyle="success")
        ttkb.Label(kwargs["window"], text="Creando Libro", bootstyle="success").pack(
            pady=5
        )
        kwargs["window"].update()
    else:
        kwargs["inputs"][0].configure(bootstyle="danger")
        ttkb.Label(kwargs["window"], text="Codigo Invalido", bootstyle="danger").pack(
            pady=5
        )
        return

    # conexion a base de datos
    conn = kwargs["conn"]
    cursor = kwargs["cursor"]

    # genera un libro nuevo y sale solo si libro es valido
    while True:

        # genera arbol nuevo si el arbol creado no tiene suficientes llaves validas
        arbol = ()
        while len(arbol) < 10:
            arbol, nombre_tabla = generador.main(
                kwargs["codigo_ggmk"], kwargs["formato"]
            )

        # crea tabla
        cursor.execute(
            f"CREATE TABLE '{nombre_tabla}' (GGMK, GMK, MK, SMK, K, Secuencia, Cilindro, MP, AsignadaProyecto)"
        )

        # carga arbol a tabla creada
        cursor.executemany(
            f"INSERT INTO '{nombre_tabla}' (GGMK, GMK, MK, SMK, K, Secuencia, Cilindro, MP, AsignadaProyecto) VALUES (?,?,?,?,?,?,?,?,?)",
            arbol,
        )

        # hace validaciones que solo se pueden con libro completo
        if not validaciones.valida_libro_completo(
            cursor=cursor, nombre_tabla=nombre_tabla
        ):
            cursor.execute(f"DROP TABLE '{nombre_tabla}'")
        else:
            break

    # calcula cantidad de SMK en libro que no sean 0
    cursor.executescript(
        f"""DROP TABLE IF EXISTS temp;
                CREATE TABLE temp (SMK);
                INSERT INTO temp SELECT SMK FROM '{nombre_tabla}' WHERE SMK <> 0;
                SELECT COUNT(DISTINCT SMK) FROM temp"""
    )
    cursor.execute("SELECT COUNT(DISTINCT SMK) FROM temp")
    _cuenta_smk = cursor.fetchone()
    cursor.execute("DROP TABLE temp")

    # calcula cantidad de GMK, MK y K en libro
    cursor.execute(
        f"""SELECT COUNT(DISTINCT GMK), COUNT(DISTINCT MK), COUNT(DISTINCT K) FROM '{nombre_tabla}'"""
    )
    _cuenta_gmk, _cuenta_mk, _cuenta_k = cursor.fetchone()

    # inserta todos los datos del nuevo libro en la tabla indice
    _record = (
        nombre_tabla,
        kwargs["codigo_ggmk"],
        kwargs["formato"],
        kwargs["nombre"],
        kwargs["notas"],
        dt.strftime(dt.now(), "%Y-%m-%d %H:%M:%S"),
        _cuenta_gmk,
        _cuenta_mk,
        _cuenta_smk[0] if _cuenta_smk else 0,
        _cuenta_k,
    )
    cursor.execute(f"""INSERT INTO 'libros' VALUES (?,?,?,?,?,?,?,?,?,?)""", _record)

    # graba base de datos
    conn.commit()

    # muestra las llaves en el GUI
    kwargs["window"].destroy()
    libros.visor.mostrar(
        cursor=cursor,
        nombre_tabla=nombre_tabla,
        main_window=kwargs["previous_window"],
    )


def ggmk_aleatoria(codigo_ggmk):

    _codigo = "123456"  # ggmk invalida
    while not validaciones.valida_codigo(_codigo):
        _codigo = "".join([str(random.randrange(0, 10)) for _ in range(6)])

    codigo_ggmk.set(value=_codigo)


def regresar(previous_window, window):
    # reactiva menu principal y cierra menu secundario
    previous_window.deiconify()
    window.destroy()
