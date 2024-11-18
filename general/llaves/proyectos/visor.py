from tkinter import END, StringVar
import ttkbootstrap as ttkb
import openpyxl as pyxl
from fpdf import FPDF
from copy import deepcopy as copy

from proyectos.cargar2 import Cargar
from proyectos.editar import Editar


def mostrar(cursor, nombre_proyecto, nombre_libro, main_window, conn):

    editar = Editar(cursor=cursor, conn=conn, nombre_proyecto=nombre_proyecto)

    global detalle
    detalle = False

    # crear nueva ventana, dimensionar
    window = ttkb.Toplevel()
    window.geometry(f"2000x{int(int(window.winfo_screenheight())*.92)}+10+10")

    # definir Frames
    frames = {
        "top": ttkb.Frame(window),
        "mid": ttkb.Frame(window),
        "bottom": ttkb.Frame(window, height=100),
    }

    # GUI - Top Frame: botones
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
            frames["top"], text="Editar", command=lambda: menu_editar(frames["bottom"])
        ),
        ttkb.Button(
            frames["top"],
            text="Regresar",
            command=lambda: menu_regresar(main_window=main_window, window=window),
            bootstyle="warning",
        ),
        ttkb.Button(
            frames["top"],
            text="Refrescar",
            command=lambda: menu_refrescar(
                cursor=cursor,
                nombre_proyecto=nombre_proyecto,
                nombre_libro=nombre_libro,
                area_texto=area_texto,
            ),
            bootstyle="success",
        ),
    ]
    for x, button in enumerate(buttons):
        button.grid(row=0, column=x, padx=30, pady=20)

    # crear zona donde se muestra el texto del arbol
    area_texto = ttkb.Text(frames["mid"], height=63, width=250)
    area_texto.pack()

    # genera el texto del arbol al visor y mostrar
    menu_detalle(
        cursor=cursor,
        nombre_proyecto=nombre_proyecto,
        area_texto=area_texto,
        nombre_libro=nombre_libro,
    )

    editar.gui(frame=frames["bottom"])


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


def menu_refrescar(**kwargs):

    arbol = genera_texto_arbol(
        detalle=detalle,
        cursor=kwargs["cursor"],
        nombre_proyecto=kwargs["nombre_proyecto"],
        nombre_libro=kwargs["nombre_libro"],
    )

    muestra_arbol(arbol, area_texto=kwargs["area_texto"])


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


def menu_exportar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    arbol = genera_texto_arbol(detalle=True)
    for linea in arbol.split("\n"):
        pdf.cell(200, 10, txt=linea, ln=1, align="L")
    pdf.output("mygfg.pdf")


def menu_editar(frame):

    for widget in frame.winfo_children():
        widget.config(state="normal")


def menu_regresar(window, main_window):

    main_window.deiconify()
    window.destroy()


def genera_texto_arbol(detalle, cursor, nombre_proyecto, nombre_libro):

    totales = {"gmk": 0, "mk": 0}

    cursor.execute(
        f"""SELECT  Secuencia, Jerarquia, CodigoLlave, Nombre, Copias, CodigoPuerta, TipoPuerta,
                    TipoCerradura, Zona1, Zona2, Zona3, Zona4, ZonaCodigo
                    FROM '{nombre_proyecto}'"""
    )

    data = [[j if j else "" for j in i] for i in cursor.fetchall()]
    output = ""

    for (
        sec,
        jer,
        cod,
        nom,
        cop,
        codp,
        tipp,
        tipc,
        zon1,
        zon2,
        zon3,
        zon4,
        zonc,
    ) in data:

        if jer == "GGMK":
            output += f"{sec} | Codigo:{cod} | Nombre: {nom} | Copias: {cop} |\n"

        if jer == "GMK":
            output += "|\n"
            output += f"|{'-'*8} {sec} | Codigo:{cod} | Nombre: {nom} | Copias: {cop} | Zona: {zon1} {zon2} {zon3} {zon4} {zonc} |\n"
            totales["gmk"] += 1

        if jer == "MK":
            output += f"|{' '*9}|\n"
            output += f"|{' '*9}|{'-'*7} {sec} | Codigo:{cod} | Nombre: {nom} | Copias: {cop} | Zona: {zon1} {zon2} {zon3} {zon4} {zonc} |\n"
            output += f"|{' '*9}|{' '*10}|\n"
            totales["mk"] += 1

            if not detalle:
                cursor.execute(
                    f"SELECT * FROM '{nombre_proyecto}' AS T1 JOIN '{nombre_libro}' AS T2 ON T1.Secuencia = T2.Secuencia WHERE MK = '{cod}'"
                )
                _unicas = len(cursor.fetchall())
                output += f"|{' '*9}|{' '*10}|- K-Únicas: {_unicas}\n"

        if jer == "K" and detalle:
            output += f"""|{' '*9}|{' '*10}|- {sec} | Codigo:{cod} | Nombre: {nom} | Copias: {cop} | Zona: {zon1} {zon2} {zon3} {zon4} {zonc} | Puerta: {codp} - {tipp} | Cerradura: {tipc} |\n"""

    # agregar resumen al inicio del texto
    cursor.execute(f"SELECT * FROM 'proyectos' WHERE Codigo = '{nombre_proyecto}'")
    d = cursor.fetchone()

    output = (
        f"""{'-'*50}\nProyecto: {nombre_proyecto}\nNombre: {d[3]}\nFecha de Creacion: {d[5]}\nTotal GMKs: {int(d[6]):,}\nTotal MKs: {int(d[7]):,}\nTotal Ks: {int(d[9]):,}\n{'-'*50}\n\n"""
        + output
    )

    return output


def muestra_arbol(arbol, area_texto):
    area_texto.delete("1.0", "end")
    area_texto.insert(END, arbol)
