from tkinter import END, StringVar
import ttkbootstrap as ttkb
import openpyxl as pyxl
from fpdf import FPDF
from copy import deepcopy as copy

import proyectos.editar


def mostrar(cursor, nombre_proyecto, nombre_libro, main_window):

    global detalle
    detalle = False

    # crear nueva ventana, dimensionar
    window = ttkb.Toplevel()
    window.geometry("1900x1800+10+10")

    # GUI - Top Frame: botones
    frames = {
        "top": ttkb.Frame(window),
        "mid": ttkb.Frame(window),
        "bottom": ttkb.Frame(window),
    }
    frames["top"].pack(pady=10)

    # GUI - Mid Frame: arbol
    frames["mid"].pack(pady=10)

    # GUI - Bottom Frame: editar
    frames["bottom"].pack(pady=10)

    # definir y colocar botones de menu
    buttons = [
        ttkb.Button(
            frames["top"],
            text="Detalle",
            command=lambda: menu_detalle(
                cursor=cursor,
                nombre_proyecto=nombre_proyecto,
                nombre_libro=nombre_libro,
                area_texto=area_texto,
            ),
        ),
        ttkb.Button(frames["top"], text="Exportar XLS", command=menu_exportar_xls),
        ttkb.Button(frames["top"], text="Exportar PDF", command=menu_exportar_pdf),
        ttkb.Button(
            frames["top"],
            text="Editar",
            command=lambda: menu_editar(
                frames,
                cursor,
                nombre_proyecto,
                nombre_libro,
                area_texto,
            ),
        ),
        ttkb.Button(
            frames["top"],
            text="Regresar",
            command=lambda: menu_regresar(main_window=main_window, window=window),
            bootstyle="warning",
        ),
        ttkb.Button(
            frames["top"], text="Guardar", command=menu_guardar, bootstyle="success"
        ),
    ]
    for x, button in enumerate(buttons):
        button.grid(row=0, column=x, padx=30, pady=20)

    # crear zona donde se muestra el texto del arbol
    area_texto = ttkb.Text(frames["mid"], height=38, width=250)
    area_texto.pack()

    # genera el texto del arbol al visor y mostrar
    menu_detalle(
        cursor=cursor,
        nombre_proyecto=nombre_proyecto,
        area_texto=area_texto,
        nombre_libro=nombre_libro,
    )


def menu_detalle(**kwargs):

    global detalle

    arbol = genera_texto_arbol(
        detalle=detalle,
        cursor=kwargs["cursor"],
        nombre_proyecto=kwargs["nombre_proyecto"],
        nombre_libro=kwargs["nombre_libro"],
    )

    muestra_arbol(arbol, area_texto=kwargs["area_texto"])
    detalle = not detalle


def menu_exportar_xls(cursor, nombre_proyecto):
    wb = pyxl.Workbook()
    ws = wb.active

    # crear hoja "Estructura"
    ws.title = "Estructura"
    titulos = [
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
    cursor.execute(f"SELECT * FROM libros WHERE Codigo='{nombre_proyecto}'")
    data = cursor.fetchone()
    for i, (a, b) in enumerate(zip(titulos, data), start=1):
        ws[f"A{i}"] = str(a)
        ws[f"B{i}"] = str(b)

    # crear hoja "Resumen"
    wb.create_sheet("Resumen")
    ws = wb["Resumen"]
    arbol = genera_texto_arbol(detalle=False)
    fila = 0
    for linea in arbol.split("\n"):
        fila += 1
        if "GGMK" in linea:
            ws[f"A{fila}"] = linea
        elif "GMK-" in linea:
            ws[f"B{fila}"] = linea
        elif "MK-" in linea:
            ws[f"C{fila}"] = linea
        elif "K-" in linea:
            ws[f"D{fila}"] = linea
        else:
            fila -= 1

    # crear hoja "Detalle"
    wb.create_sheet("Detalle")
    ws = wb["Detalle"]
    arbol = genera_texto_arbol(detalle=True)
    fila = 0
    for linea in arbol.split("\n"):
        fila += 1
        if "GGMK" in linea:
            ws[f"A{fila}"] = linea
        elif "GMK-" in linea:
            ws[f"B{fila}"] = linea
        elif "MK-" in linea:
            ws[f"C{fila}"] = linea
        elif "K-" in linea:
            ws[f"D{fila}"] = linea
        else:
            fila -= 1

    # crear plantilla para carga de proyectos
    wb.create_sheet("PlantillaProyecto")

    # guardar hoja
    wb.save(f"{nombre_proyecto}.xlsx")


def menu_exportar_pdf(self):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    arbol = genera_texto_arbol(detalle=True)
    for linea in arbol.split("\n"):
        pdf.cell(200, 10, txt=linea, ln=1, align="L")
    pdf.output("mygfg.pdf")

    return


def menu_guardar(conn):
    conn.commit()
    status_graba_db = True


def menu_editar(frames, cursor, nombre_proyecto, nombre_libro, area_texto):

    arbol = genera_texto_arbol(
        detalle=True,
        cursor=cursor,
        nombre_proyecto=nombre_proyecto,
        nombre_libro=nombre_libro,
    )
    muestra_arbol(arbol, area_texto=area_texto)
    proyectos.editar.gui(frames, cursor, nombre_proyecto)


def menu_regresar(window, main_window):

    main_window.deiconify()
    window.destroy()
    return

    if not status_graba_db:
        proceso.cursor.execute(f"DROP TABLE '{proceso.nombre_tabla}'")
        proceso.conn.commit()


def genera_texto_arbol(detalle, cursor, nombre_proyecto, nombre_libro):

    totales = {"gmk": 0, "mk": 0}

    cursor.execute(
        f"SELECT * FROM '{nombre_proyecto}' AS T1 JOIN '{nombre_libro}' AS T2 ON T1.Secuencia = T2.Secuencia"
    )
    data = cursor.fetchall()

    previous = [0] * 25
    output = f"GGMK <> Codigo:{data[0][0]}\n"

    for line, d in enumerate(data):

        sec = d[1]
        nombre = d[2] if d[2] else ""
        cop = d[3]
        cod_puerta = d[4] if d[4] else ""
        tip_puerta = d[5] if d[5] else ""
        tip_cerr = d[6] if d[6] else ""
        zona = " - ".join([i if i else "" for i in d[7:12]])
        gmk = d[14]
        mk = d[15]
        smk = d[16]
        k = d[17]
        cil = d[19]
        mp = d[20]

        if gmk != previous[14]:
            output += "|\n"
            output += f"|{'-'*8} GM{sec} <> Codigo: {gmk}\n"
            totales["gmk"] += 1

        if mk != previous[15]:
            output += f"|{' '*9}|\n"
            output += f"|{' '*9}|{'-'*7} M{sec} <> Codigo:{mk}\n"
            output += f"|{' '*9}|{' '*8}|\n"
            totales["mk"] += 1

            if not detalle:
                cursor.execute(
                    f"SELECT * FROM '{nombre_proyecto}' AS T1 JOIN '{nombre_libro}' AS T2 ON T1.Secuencia = T2.Secuencia WHERE MK = '{mk}'"
                )
                _unicas = len(cursor.fetchall())
                output += f"|{' '*9}|{' '*8}K-Unicas: {_unicas}\n"

        if detalle:
            output += f"|{' '*9}|{' '*8}|- {sec} <> Codigo:{k} [{nombre if nombre else '(sin nombre)'}] - Cilindro ({mp} MP): {cil:<30}- Copias: {cop} - Zona: {zona} - Puerta: {tip_puerta} - {cod_puerta} - Cerradura: {tip_cerr}\n"

        previous = copy(data[line])

    # agregar resumen al inicio del texto
    cursor.execute(f"SELECT * FROM 'proyectos' WHERE Codigo = '{nombre_proyecto}'")
    d = cursor.fetchone()

    output = (
        f"""{'-'*50}\nProyecto: {nombre_proyecto}\nNombre: {d[3]}\nFecha de Creacion: {d[5]}\nTotal GMKs: {int(d[6]):,}\nTotal MKs: {int(d[7]):,}\nTotal Ks: {int(d[9]):,}\n{'-'*50}\n"""
        + output
    )

    return output


def muestra_arbol(arbol, area_texto):
    area_texto.delete("1.0", "end")
    area_texto.insert(END, arbol)
