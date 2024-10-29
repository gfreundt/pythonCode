from tkinter import IntVar, END
import ttkbootstrap as ttkb
from ttkbootstrap.tableview import Tableview
import visor

class Arbol:
      def __init__(self):
            pass

def gui(cursor, previous_window):

    # previous_window.withdraw()

    window = ttkb.Toplevel()
    window.geometry("1400x1300")

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
        command=lambda: seleccion(
            window, dt, cursor=cursor, previous_window=previous_window
        ),
    ).pack(pady=20)
    ttkb.Button(window, text="Regresar", command=lambda: regresar(window)).pack(pady=20)

def arma_arbol( tabla):
        
        arbol = {}

        proyecto_nombre = ""
        proyecto_notas = ""

        window = ttkb.Toplevel()
        window.geometry("1000x1300")
        text_area = ttkb.Text(window, height=100, width=80)
        text_area.place(x=10, y=60)
        ggmk = None

        nombre_tabla = tabla
        arbol.data = []
        arbol.s1_valor = IntVar(window, value=1)

        vertical = 50
        nivel_boton = 0
        secuencia_gmk = -1

        arbol.b1 = ttkb.Button(
            window, text="Agrega GMK", command=lambda: menu_agrega_gmk(arbol)
        )
        arbol.b1.place(x=700, y=70)

        arbol.b2 = ttkb.Button(
            window, text="Agrega MK", command=menu_agrega_mk
        )
        arbol.b2.place(x=730, y=100)
        arbol.b2.config(state="disabled")

        arbol.b3 = ttkb.Button(
            window, text="Nivel Completo", command=menu_nivel_completo
        )
        arbol.b3.place(x=860, y=85)

        arbol.b4 = ttkb.Button(window, text="Deshacer", command=menu_deshacer)
        arbol.b4.place(x=860, y=135)

        arbol.s1 = ttkb.Spinbox(
            window, from_=1, to=8, textvariable=arbol.s1_valor, width=2
        )
        arbol.s1.place(x=760, y=130)
        arbol.s1.config(state="disabled")

        muestra_arbol()

def menu_agrega_gmk(arbol):
        arbol.b1.config(state="disabled")
        arbol.b2.config(state="active")

        arbol.data.append([])
        arbol.nivel_boton = 1
        arbol.secuencia_gmk += 1

        muestra_arbol()

def menu_agrega_mk(arbol):
        arbol.nivel_boton = 2
        arbol.b2.config(state="disabled")
        arbol.s1.config(state="normal")
        arbol.data[-1].append(0)

        muestra_arbol()

def menu_agrega_k(arbol):
        arbol.data[arbol.secuencia_gmk].append(arbol.s1_valor.get())
        arbol.b4.config(state="disabled")
        arbol.s1.config(state="disabled")

        muestra_arbol()

def menu_nivel_completo(self):
        if nivel_boton == 0:
            ggmk = asigna_llaves()
            window.destroy()
            vista = Visor(configuracion="proyecto", proceso=self)
            vista.mostrar()
            return
        elif nivel_boton == 1:
            nivel_boton = 0
            boton1.config(state="active")
            boton2.config(state="disabled")
        elif nivel_boton == 2:
            nivel_boton = 1
            arbol[-1][-1] = spinbox_valor.get()
            cantidad_llaves.config(state="disabled")
            boton2.config(state="active")

        muestra_arbol()

def menu_deshacer():
        return

def asigna_llaves(self):

        # determina codigo secuencial del proyecto
        cursor.execute(
            f"SELECT COUNT(GGMK) FROM proyectos WHERE Libro_Origen = '{nombre_tabla}'"
        )
        _secuencial = cursor.fetchall()
        nombre_proyecto = f"P{nombre_tabla[1:]}-{int(_secuencial[0][0]) if _secuencial else 0:03d}"

        print(nombre_proyecto)

        # copia estructura de tabla de libro a nuevo proyecto
        cursor.execute(f"DROP TABLE IF EXISTS '{nombre_proyecto}'")
        cursor.execute(
            f"CREATE TABLE '{nombre_proyecto}' (GGMK, GMK, MK, SMK, K, Secuencia, Cilindro, MP, TipoPuerta, Cerradura, Copias, Zona1, Zona2, Zona3, Zona4, ZonaCodigo, Notas)"
        )

        # extrae del libro la cantidad de GMK necesarias para el proyecto
        cursor.execute(
            f"SELECT DISTINCT GMK FROM '{nombre_tabla}' LIMIT {len(arbol)}"
        )
        required_gmks = [i[0] for i in cursor.fetchall()]

        # extrae del libro todas las MK necesarias para el proyecto
        for g, gmk in enumerate(required_gmks):
            cursor.execute(
                f"SELECT DISTINCT MK FROM '{nombre_tabla}' WHERE GMK = '{gmk}' LIMIT {len(arbol[g])}"
            )
            required_mks = [i[0] for i in cursor.fetchall()]

            # llena la tabla del proyecto con las llaves necesarias
            for m, mk in enumerate(required_mks):
                cmd = f"""  INSERT INTO '{nombre_proyecto}' (GGMK, GMK, MK, SMK, K, Secuencia, Cilindro, MP, Copias)
                            SELECT GGMK, GMK, MK, SMK, K, Secuencia, Cilindro, MP, 1
                            FROM '{nombre_tabla}' WHERE MK = '{mk}' LIMIT {arbol[g][m]}"""
                cursor.execute(cmd)

        # calcula cantidad de SMK en libro que no sean 0
        cursor.executescript(
            f"""DROP TABLE IF EXISTS temp;
                CREATE TABLE temp (SMK);
                INSERT INTO temp SELECT SMK FROM '{nombre_proyecto}' WHERE SMK <> 0;
                SELECT COUNT(DISTINCT SMK) FROM temp"""
        )
        cursor.execute("SELECT COUNT(DISTINCT SMK) FROM temp")
        _cuenta_smk = cursor.fetchone()
        cursor.execute("DROP TABLE temp")

        # calcula cantidad de GMK, MK y K en libro
        cursor.execute(
            f"""SELECT GGMK, COUNT(DISTINCT GMK), COUNT(DISTINCT MK), COUNT(DISTINCT K) FROM '{nombre_proyecto}'"""
        )
        _codigo_ggmk, _cuenta_gmk, _cuenta_mk, _cuenta_k = cursor.fetchone()

        # inserta todos los datos del nuevo libro en la tabla indice
        _record = (
            nombre_proyecto,
            nombre_tabla,
            _codigo_ggmk,
            proyecto_nombre,
            proyecto_notas,
            dt.strftime(dt.now(), "%Y-%m-%d %H:%M:%S"),
            _cuenta_gmk,
            _cuenta_mk,
            _cuenta_smk[0] if _cuenta_smk else 0,
            _cuenta_k,
            "Zona1",
            "Zona2",
            "Zona3",
            "Zona4",
            "Modelo",
            1,
        )
        cursor.execute(
            f"""INSERT INTO 'proyectos' VALUES ({(',?'*16)[1:]})""", _record
        )

        conn.commit()

def muestra_arbol(self):
        text_area.delete("1.0", "end")
        text_area.insert(END, genera_texto_arbol())

def cargar_proyecto(self, tabla):
        nombre_tabla = tabla
        nombre_proyecto = copy(nombre_tabla)
        vista = Visor(configuracion="proyecto", proceso=self)
        vista.mostrar()

def listado(self):
        window = Tk()
        window.geometry("1600x1300")

        cursor.execute("SELECT * FROM proyectos")

        data = [
            (
                "Codigo",
                "Libro_Origen",
                "GGMK",
                "Nombre",
                "Notas",
                "Fecha",
                "Total_GMK",
                "Total_MK",
                "Total_SMK",
                "Total_K",
                "Zona1",
                "Zona2",
                "Zona3",
                "Zona4",
                "Modelo_Puerta",
                "Copias",
            )
        ] + cursor.fetchall()

        for r, row in enumerate(data):
            for c, col in enumerate(row):
                e = Entry(window, font=("calibre", 10, "normal"))
                e.grid(row=r, column=c, padx=5, pady=2)
                e.insert(END, col if col else "")

        Button(window, text="Regresar", command=listado_regreso).place(
            x=1500, y=100
        )

def listado_regreso(self):
    window.destroy()

def genera_texto_arbol(self):
        totalx = 0
        total = 1

        output = f"GGMK\n"
        for p, gmk in enumerate(arbol, start=1):
            total += 1
            output += "|\n"
            output += f"|{'-'*9}GMK-{p:02d}\n"

            for q, mk in enumerate(gmk, start=1):
                total += 1
                output += f"{' ' if p==len(arbol) else '|'}{' '*9}|\n"
                output += f"|{' '*9}{' ' if p==len(arbol) else '|'}{'-'*9} MK-{p:02d}-{q:02d}\n"
                output += f"{' ' if p==len(arbol) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{' '*10}|\n"

                output += f"{' ' if p==len(arbol) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{' '*10}Unicas: {mk}\n"
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

def regresar(window):
    window.destroy()


def seleccion(window, dt, cursor, previous_window):

    selected = dt.get_rows(selected=True)
    window.destroy()
    visor.mostrar(
        cursor=cursor,
        config="libro",
        nombre_tabla=selected[0].values[0],
        main_window=previous_window,
    )