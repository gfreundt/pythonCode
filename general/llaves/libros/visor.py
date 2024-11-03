from tkinter import END
import ttkbootstrap as ttkb
import openpyxl as pyxl
from fpdf import FPDF
from copy import deepcopy as copy


def mostrar(cursor, nombre_tabla, main_window):

    global detalle
    detalle = False

    # crear nueva ventana, dimensionar
    window = ttkb.Toplevel()
    window.geometry("1300x2000+10+10")

    # GUI - Top Frame: botones
    top_frame = ttkb.Frame(window)
    top_frame.pack(pady=10)

    # GUI - Bottom Frame: arbol
    bottom_frame = ttkb.Frame(window)
    bottom_frame.pack(pady=10)

    # definir y colocar botones de menu
    buttons = [
        ttkb.Button(
            top_frame,
            text="Detalle",
            command=lambda: menu_detalle(
                cursor=cursor,
                nombre_tabla=nombre_tabla,
                area_texto=area_texto,
            ),
        ),
        ttkb.Button(top_frame, text="Exportar XLS", command=menu_exportar_xls),
        ttkb.Button(top_frame, text="Exportar PDF", command=menu_exportar_pdf),
        ttkb.Button(top_frame, text="Guardar", command=menu_guardar),
        ttkb.Button(top_frame, text="Editar", command=menu_editar),
        ttkb.Button(
            top_frame,
            text="Regresar",
            command=lambda: menu_regresar(main_window=main_window, window=window),
        ),
    ]
    for x, button in enumerate(buttons):
        button.grid(row=0, column=x, padx=30, pady=20)

    # crear zona donde se muestra el texto del arbol
    area_texto = ttkb.Text(bottom_frame, height=78, width=130)
    area_texto.pack()

    # genera el texto del arbol al visor y mostrar
    menu_detalle(cursor=cursor, nombre_tabla=nombre_tabla, area_texto=area_texto)


def menu_detalle(**kwargs):

    global detalle

    arbol = genera_texto_arbol(
        detalle=detalle,
        cursor=kwargs["cursor"],
        nombre_libro=kwargs["nombre_tabla"],
    )
    muestra_arbol(arbol, area_texto=kwargs["area_texto"])
    detalle = not detalle


def menu_exportar_xls(cursor, nombre_tabla):
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
    cursor.execute(f"SELECT * FROM libros WHERE Codigo='{nombre_tabla}'")
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
    wb.save(f"{nombre_tabla}.xlsx")


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


def menu_editar(self):
    return


def menu_regresar(window, main_window):

    main_window.deiconify()
    window.destroy()
    return

    if not status_graba_db:
        proceso.cursor.execute(f"DROP TABLE '{proceso.nombre_tabla}'")
        proceso.conn.commit()


def genera_texto_arbol(detalle, cursor, nombre_libro):

    # extrae data de libro de base de datos
    cursor.execute(f"SELECT * FROM '{nombre_libro}'")
    data = cursor.fetchall()

    # variables en blanco para iniciar proceso
    previous = [0] * 10
    totales = {"gmk": 0, "mk": 0}

    # ingresar cabecera de texto
    output = f"GGMK <> Codigo:{data[0][0]}\n"

    # loopear todas las llaves y armar el arbol
    for line, (_, gmk, mk, _, k, sec, cil, mp) in enumerate(data):

        if gmk != previous[1]:
            output += "|\n"
            output += f"|{'-'*8} GM{sec[:4]} <> Codigo: {gmk}\n"
            totales["gmk"] += 1

        if mk != previous[2]:
            output += f"|{' '*9}|\n"
            output += f"|{' '*9}|{'-'*7} M{sec[:8]} <> Codigo:{mk}\n"
            output += f"|{' '*9}|{' '*8}|\n"
            totales["mk"] += 1

            if not detalle:
                cursor.execute(f"SELECT * FROM '{nombre_libro}' WHERE MK = '{mk}'")
                _unicas = len(cursor.fetchall())
                output += f"|{' '*9}|{' '*8}K-Unicas: {_unicas}\n"

        if detalle:
            output += f"|{' '*9}|{' '*8}|- {sec} <> Codigo:{k} - Cilindro ({mp} MP): {cil:<30} -\n"

        previous = copy(data[line])

    # agregar resumen al inicio del texto
    output = (
        f"""{'-'*50}\nLibro: {nombre_libro}\nValidaciones: OK\nTotal GMKs: {totales['gmk']:,}\nTotal MKs: {totales['mk']:,}\nTotal Ks: {len(data):,}\n{'-'*50}\n"""
        + output
    )

    return output


def muestra_arbol(arbol, area_texto):
    area_texto.delete("1.0", "end")
    area_texto.insert(END, arbol)
