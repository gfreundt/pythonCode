from tkinter import IntVar, END
import ttkbootstrap as ttkb
from ttkbootstrap.tableview import Tableview
from datetime import datetime as dt


class Arbol:
    def __init__(self):
        pass


def gui(cursor, previous_window, conn):

    global arbol
    arbol = Arbol()

    # previous_window.withdraw()

    window = ttkb.Toplevel()
    window.geometry("1800x1300")

    cursor.execute("SELECT * FROM libros")

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

    row_data = aplica_formato(cursor.fetchall())

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
        command=lambda: seleccion(window, dt, cursor=cursor, conn=conn),
    ).pack(pady=20)
    ttkb.Button(window, text="Regresar", command=lambda: regresar(window)).pack(pady=20)


def seleccion(window, dt, cursor, conn):

    selected = dt.get_rows(selected=True)
    window.destroy()
    arma_arbol(nombre_libro=selected[0].values[0], cursor=cursor, conn=conn)


def regresar(window):
    window.destroy()


def arma_arbol(nombre_libro, cursor, conn):

    window = ttkb.Toplevel()
    window.geometry("1600x1300")
    arbol.text_area = ttkb.Text(window, height=100, width=80)
    arbol.text_area.place(x=10, y=60)

    arbol.data = []
    arbol.s1_valor = IntVar(window, value=1)

    arbol.nivel_boton = 0
    arbol.secuencia_gmk = -1

    arbol.b1 = ttkb.Button(window, text="Agrega GMK", command=lambda: menu_agrega_gmk())
    arbol.b1.place(x=700, y=70)

    arbol.b2 = ttkb.Button(window, text="Agrega MK", command=menu_agrega_mk)
    arbol.b2.place(x=800, y=120)
    arbol.b2.config(state="disabled")

    arbol.b3 = ttkb.Button(
        window,
        text="Nivel Completo",
        command=lambda: menu_nivel_completo(window, cursor, nombre_libro, conn),
    )
    arbol.b3.place(x=900, y=90)

    arbol.b4 = ttkb.Button(window, text="Deshacer", command=menu_deshacer)
    arbol.b4.place(x=900, y=170)

    arbol.s1 = ttkb.Spinbox(window, from_=1, textvariable=arbol.s1_valor, width=2)
    arbol.s1.place(x=800, y=170)
    arbol.s1.config(state="disabled")

    muestra_arbol()


def menu_agrega_gmk():
    arbol.b1.config(state="disabled")
    arbol.b2.config(state="active")

    arbol.data.append([])
    arbol.nivel_boton = 1
    arbol.secuencia_gmk += 1

    muestra_arbol()


def menu_agrega_mk():
    arbol.nivel_boton = 2
    arbol.b2.config(state="disabled")
    arbol.s1.config(state="normal")
    arbol.data[-1].append(0)

    muestra_arbol()


def menu_agrega_k():
    arbol.data[arbol.secuencia_gmk].append(arbol.s1_valor.get())
    arbol.b4.config(state="disabled")
    arbol.s1.config(state="disabled")

    muestra_arbol()


def menu_nivel_completo(window, cursor, nombre_libro, conn):
    if arbol.nivel_boton == 0:
        asigna_llaves(cursor, nombre_libro, conn)
        window.destroy()
        return
    elif arbol.nivel_boton == 1:
        arbol.nivel_boton = 0
        arbol.b1.config(state="active")
        arbol.b2.config(state="disabled")
    elif arbol.nivel_boton == 2:
        arbol.nivel_boton = 1
        arbol.data[-1][-1] = arbol.s1_valor.get()
        arbol.s1.config(state="disabled")
        arbol.b2.config(state="active")

    muestra_arbol()


def menu_deshacer():
    return


def asigna_llaves(cursor, nombre_libro, conn):

    proyecto_nombre = "nombre"
    proyecto_notas = "notas"

    # determina codigo secuencial del proyecto
    cursor.execute(
        f"SELECT COUNT(GGMK) FROM proyectos WHERE Libro_Origen = '{nombre_libro}'"
    )
    _secuencial = cursor.fetchall()
    nombre_proyecto = (
        f"P{nombre_libro[1:]}-{int(_secuencial[0][0]) if _secuencial else 0:03d}"
    )

    # copia estructura de tabla de libro a nuevo proyecto
    cursor.execute(f"DROP TABLE IF EXISTS '{nombre_proyecto}'")
    cursor.execute(
        f"CREATE TABLE '{nombre_proyecto}' (LibroOrigen, Secuencia, Jerarquia, Nombre, Copias, CodigoPuerta, TipoPuerta, TipoCerradura, Zona1, Zona2, Zona3, Zona4, ZonaCodigo, Notas, FabricadoLlaveCopias, FabricadoCilindro)"
    )

    # extrae del libro la GGMK
    cursor.execute(f"SELECT DISTINCT GGMK FROM '{nombre_libro}'")
    required_gmks = [i[0] for i in cursor.fetchone()]
    cursor.execute(
        f"INSERT INTO '{nombre_proyecto}' (LibroOrigen, Secuencia, Jerarquia, Copias, FabricadoLlaveCopias, FabricadoCilindro) VALUES ('{nombre_libro}','GGMK','GGMK',1,0,0)"
    )

    # extrae del libro la cantidad de GMK necesarias para el proyecto
    cursor.execute(f"SELECT DISTINCT GMK FROM '{nombre_libro}' LIMIT {len(arbol.data)}")
    required_gmks = [i[0] for i in cursor.fetchall()]

    # extrae del libro todas las MK necesarias para el proyecto
    total_mks = total_smks = total_ks = 0
    for g, gmk in enumerate(required_gmks):
        # genera secuencia de GMK e inserta
        cursor.execute(f"SELECT Secuencia FROM '{nombre_libro}' WHERE GMK='{gmk}'")
        mk_secuencia = cursor.fetchone()
        cursor.execute(
            f"INSERT INTO '{nombre_proyecto}' (LibroOrigen, Secuencia, Jerarquia, Copias, FabricadoLlaveCopias, FabricadoCilindro) VALUES ('{nombre_libro}','GM{mk_secuencia[0][:4]}','GMK',1,0,0)"
        )

        cursor.execute(
            f"SELECT DISTINCT MK FROM '{nombre_libro}' WHERE GMK = '{gmk}' LIMIT {len(arbol.data[g])}"
        )
        required_mks = [i[0] for i in cursor.fetchall()]
        total_mks += len(required_mks)

        # llena la tabla del proyecto con las llaves necesarias
        for m, mk in enumerate(required_mks):
            # genera secuencia de MK e inserta
            cursor.execute(f"SELECT Secuencia FROM '{nombre_libro}' WHERE MK='{mk}'")
            mk_secuencia = cursor.fetchone()
            cursor.execute(
                f"INSERT INTO '{nombre_proyecto}' (LibroOrigen, Secuencia, Jerarquia, Copias, FabricadoLlaveCopias, FabricadoCilindro) VALUES ('{nombre_libro}','M{mk_secuencia[0][:8]}','MK', 1,0,0)"
            )
            # inserta todas las k necesarias para esa mk
            cmd = f"""  INSERT INTO '{nombre_proyecto}' (LibroOrigen, Secuencia, Jerarquia, Copias, FabricadoLlaveCopias, FabricadoCilindro)
                            SELECT '{nombre_libro}', Secuencia, 'K', 1, 0, 0
                            FROM '{nombre_libro}' WHERE MK = '{mk}' LIMIT {arbol.data[g][m]}"""
            cursor.execute(cmd)

    # calcula cantidad de K en proyecto
    cursor.execute(
        f"SELECT COUNT (*) FROM '{nombre_proyecto}' WHERE Secuencia LIKE 'K-%'"
    )
    total_ks = cursor.fetchone()[0]

    # TODO: calcula cantidad de SMK en proyecto que no sean 0
    total_smks = 0

    # inserta todos los datos del nuevo proyecto en la tabla indice
    _record = (
        nombre_proyecto,
        nombre_libro,
        nombre_libro[2:8],
        proyecto_nombre,
        proyecto_notas,
        dt.strftime(dt.now(), "%Y-%m-%d %H:%M:%S"),
        len(required_gmks),
        total_mks,
        total_smks,
        total_ks,
    )

    cursor.execute(f"""INSERT INTO 'proyectos' VALUES ({(',?'*10)[1:]})""", _record)

    conn.commit()


def muestra_arbol():
    arbol.text_area.delete("1.0", "end")
    arbol.text_area.insert(END, genera_texto_arbol())


def genera_texto_arbol():
    totalx = 0
    total = 1

    output = f"GGMK\n"
    for p, gmk in enumerate(arbol.data, start=1):
        total += 1
        output += "|\n"
        output += f"|{'-'*9}GMK-{p:02d}\n"

        for q, mk in enumerate(gmk, start=1):
            total += 1
            output += f"{' ' if p==len(arbol.data) else '|'}{' '*9}|\n"
            output += f"|{' '*9}{' ' if p==len(arbol.data) else '|'}{'-'*9} MK-{p:02d}-{q:02d}\n"
            output += f"{' ' if p==len(arbol.data) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{' '*10}|\n"

            output += f"{' ' if p==len(arbol.data) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{' '*10}Unicas: {mk}\n"
            totalx += mk

    output += f"\nTotal Llaves: {total+totalx:,}\n"
    output += f"Total Puertas: {totalx:,}\n"

    return output


def aplica_formato(data):
    new_data = [list(i) for i in data]

    # elimina cero
    for i, m in enumerate(data):
        for j, n in enumerate(m):
            if n == 0:
                new_data[i][j] = ""

    return new_data
