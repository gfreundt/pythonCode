from random import randrange, shuffle
from copy import deepcopy as copy
from tkinter import Tk, Label, Text, END, font, PhotoImage, Button
from pprint import pprint
from datetime import datetime as dt
import openpyxl as pyxl
from visor import Visor


class Libro:

    def __init__(self, conn):

        self.conn = conn
        self.cursor = self.conn.cursor()

        self.detalle = False
        self.status_graba_db = False

        self.vista = Visor(configuracion="libro", proceso=self)

    def menu_detalle(self):
        self.detalle = not self.detalle
        arbol = self.genera_texto_arbol(detalle=self.detalle)
        self.muestra_arbol(arbol)

    def menu_rehacer(self):
        self.text_area.delete("1.0", "end")
        self.text_area.insert(END, "Procesando...\n")
        self.crea_libro()

    def menu_exportar(self):
        wb = pyxl.Workbook()
        ws = wb.active

        arbol = self.genera_texto_arbol(detalle=True)
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

        wb.save("export.xlsx")

    def menu_guardar(self):
        self.conn.commit()
        self.status_graba_db = True

    def menu_regresar(self):
        if not self.status_graba_db:
            self.cursor.execute(f"DROP TABLE '{self.nombre_tabla}'")
            self.conn.commit()
        self.window.destroy()

    def crea_libro(self, **kwargs):

        # en primera solicitud de libro nuevo, recibe toda esta informacion (no en rehacer libro)
        if kwargs:
            self.formato = kwargs["formato"]
            self.codigo_ggmk = kwargs["codigo_ggmk"]
            self.libro_nombre = kwargs["libro_nombre"]
            self.libro_notas = kwargs["libro_notas"]

        self.ggmk = {
            "codigo": copy(self.codigo_ggmk),
            "nombre": "Llave GGMK",
            "libro": self.libro_nombre,
            "notas": self.libro_notas,
            "fecha": dt.strftime(dt.now(), "%Y-%m-%d"),
            "subkeys": [],
        }

        self.llaves_usadas = []
        self.todas_maestras = []

        self.genera_mp_pos()

        # crea nueva tabla
        self.cursor.execute(
            f"CREATE TABLE '{self.nombre_tabla}' (GGMK, GMK, MK, SMK, K, Secuencia, Cilindro, MP, V_Unica, V_GGMK, V_GMK, V_MK, V_SMK, V_Cruzada)"
        )

        c1 = 0
        while True:
            x1 = self.siguiente_codigo(
                tipo="gmk",
                codigo_base=(
                    self.ggmk["codigo"]
                    if not self.ggmk["subkeys"]
                    else self.ggmk["subkeys"][-1]["codigo"]
                ),
            )
            if x1 == -1:
                break
            self.ggmk["subkeys"].append(
                {
                    "codigo": copy(x1),
                    "secuencia": f"GMK-{c1+1:02d}",
                    "nombre": f"Llave {c1+1:02d}",
                    "subkeys": [],
                }
            )
            self.llaves_usadas.append(copy(x1))
            self.todas_maestras.append(copy(x1))

            c2 = 0
            while True:
                x2 = self.siguiente_codigo(
                    tipo="mk",
                    codigo_base=(
                        x1
                        if not self.ggmk["subkeys"][c1]["subkeys"]
                        else self.ggmk["subkeys"][c1]["subkeys"][-1]["codigo"]
                    ),
                )
                if x2 == -1:
                    break
                self.ggmk["subkeys"][c1]["subkeys"].append(
                    {
                        "codigo": copy(x2),
                        "secuencia": f"MK-{c1+1:02d}-{c2+1:02d}",
                        "nombre": f"Llave {c1+1:02d}-{c2+1:02d}",
                        "subkeys": [],
                    }
                )
                self.llaves_usadas.append(copy(x2))
                self.todas_maestras.append(copy(x2))

                c3 = 0
                while True:
                    x3 = self.siguiente_codigo(
                        tipo="k",
                        codigo_base=(
                            x2
                            if not self.ggmk["subkeys"][c1]["subkeys"][c2]["subkeys"]
                            else self.ggmk["subkeys"][c1]["subkeys"][c2]["subkeys"][-1][
                                "codigo"
                            ]
                        ),
                    )
                    if x3 == -1:
                        break
                    self.ggmk["subkeys"][c1]["subkeys"][c2]["subkeys"].append(
                        {
                            "codigo": copy(x3),
                            "cilindro": crea_cilindro(
                                ggmk=self.codigo_ggmk, key=copy(x3)
                            ),
                            "secuencia": f"K-{c1+1:02d}-{c2+1:02d}-{c3+1:03d}",
                            "nombre": f"Llave {c1+1:02d}-{c2+1:02d}-{c3+1:03d}",
                        }
                    )
                    self.llaves_usadas.append(copy(x3))

                    _record = (
                        self.ggmk["codigo"],
                        x1,
                        x2,
                        0,
                        x3,
                        f"K-{c1+1:02d}-{c2+1:02d}-{c3+1:03d}",
                        crea_cilindro(ggmk=self.codigo_ggmk, key=x3),
                    )
                    self.cursor.execute(
                        f"INSERT INTO '{self.nombre_tabla}' (GGMK, GMK, MK, SMK, K, Secuencia, Cilindro) VALUES (?,?,?,?,?,?,?)",
                        _record,
                    )

                    c3 += 1
                c2 += 1
            c1 += 1

        self.valida_libro_completo()
        self.muestra_arbol()

    def siguiente_codigo(self, tipo, codigo_base):

        while True:

            codigo_nuevo = [i for i in codigo_base]
            pos = self.mp_pos[tipo]

            if len(pos) == 1:

                codigo_nuevo[pos[0]] = str((int(codigo_nuevo[pos[0]]) + 2) % 10)
                codigo_nuevo = "".join(codigo_nuevo)

                if codigo_nuevo in self.llaves_usadas:
                    return -1

                if valida_codigo(codigo_nuevo):
                    return codigo_nuevo

                return -1

            elif len(pos) == 2:

                for a in range(0, 9, 2):
                    codigo_nuevo[pos[0]] = str((int(codigo_nuevo[pos[0]]) + a) % 10)
                    for b in range(0, 9, 2):
                        codigo_nuevo[pos[1]] = str((int(codigo_nuevo[pos[1]]) + b) % 10)
                        cn = "".join(codigo_nuevo)
                        if cn not in self.llaves_usadas and valida_codigo(cn):
                            return cn
                return -1

            elif len(pos) == 3:

                for a in range(0, 9, 2):
                    codigo_nuevo[pos[0]] = str((int(codigo_nuevo[pos[0]]) + a) % 10)
                    for b in range(0, 9, 2):
                        codigo_nuevo[pos[1]] = str((int(codigo_nuevo[pos[1]]) + b) % 10)
                        for c in range(0, 9, 2):
                            codigo_nuevo[pos[2]] = str(
                                (int(codigo_nuevo[pos[2]]) + c) % 10
                            )
                            cn = "".join(codigo_nuevo)
                            if cn not in self.llaves_usadas and valida_codigo(cn):
                                return cn
                return -1

            elif len(pos) == 4:

                for a in range(0, 9, 2):
                    codigo_nuevo[pos[0]] = str((int(codigo_nuevo[pos[0]]) + a) % 10)
                    for b in range(0, 9, 2):
                        codigo_nuevo[pos[1]] = str((int(codigo_nuevo[pos[1]]) + b) % 10)
                        for c in range(0, 9, 2):
                            codigo_nuevo[pos[2]] = str(
                                (int(codigo_nuevo[pos[2]]) + c) % 10
                            )
                            for d in range(0, 9, 2):
                                codigo_nuevo[pos[3]] = str(
                                    (int(codigo_nuevo[pos[3]]) + d) % 10
                                )
                                cn = "".join(codigo_nuevo)
                                if cn not in self.llaves_usadas and valida_codigo(cn):
                                    return cn
                return -1

    def valida_libro_completo(self):

        # extraer toda las filas de la tabla
        self.cursor.execute(f"SELECT * FROM '{self.nombre_tabla}'")
        table_data = self.cursor.fetchall()

        # extrae todos los codigos de las master keys en la tabla
        self.cursor.execute(
            f"SELECT * FROM (SELECT GGMK FROM '{self.nombre_tabla}' UNION SELECT GMK FROM '{self.nombre_tabla}' UNION SELECT MK FROM '{self.nombre_tabla}' UNION SELECT SMK FROM '{self.nombre_tabla}' WHERE GGMK IS NOT 0)"
        )
        todas_maestras = [i[0] for i in self.cursor.fetchall()]

        # extraer todos los codigos de las llaves de la tabla
        self.cursor.execute(f"SELECT K FROM '{self.nombre_tabla}'")
        llaves_usadas = [i[0] for i in self.cursor.fetchall()]

        # iterar todas las llaves y realizar validaciones
        for row_num, row in enumerate(table_data, start=1):
            t = (
                row[6].count(":"),
                valida_llave_es_unica(llave=row[4], llaves_usadas=llaves_usadas),
                valida_llave_abre_cilindro(llave=row[0], cilindro=row[6]),
                valida_llave_abre_cilindro(llave=row[1], cilindro=row[6]),
                valida_llave_abre_cilindro(llave=row[2], cilindro=row[6]),
                valida_llave_no_cruzada(
                    cilindro=row[6],
                    mis_maestras=[i for i in row[:5] if i != 0],
                    todas_maestras=todas_maestras,
                ),
            )

            self.cursor.execute(
                f"UPDATE '{self.nombre_tabla}' SET MP={t[0]}, V_Unica={t[1]}, V_GGMK={t[1]}, V_GMK={t[1]}, V_MK={t[1]}, V_SMK={t[1]}, V_Cruzada={t[1]} WHERE rowid={row_num}"
            )

    def genera_mp_pos(self):
        _pines = list(range(0, 6))
        shuffle(_pines)

        s = "!"
        k = 0
        self.mp_pos = {}

        for pin_size, dic_key in zip(
            self.formato.split("-")[1:], ["gmk", "mk", "smk", "k"]
        ):
            p = int(pin_size)
            if p > 0:
                _m = [_pines[i] for i in range(k, k + p)]
                _n = f"{''.join(str(_pines[i]+1) for i in range(k, k + p))}!"
            else:
                _m = []
                _n = "0!"

            self.mp_pos[dic_key] = _m
            s += _n
            k += p

        self.nombre_tabla = f"L-{self.codigo_ggmk}-{s}"

    def carga_libro(self, nombre_tabla):

        # extraer toda las filas de la tabla
        self.cursor.execute(f"SELECT * FROM '{nombre_tabla}'")
        libro_data = self.cursor.fetchall()

        # extrae todos los codigos de las master keys en la tabla
        self.cursor.execute(
            f"SELECT * FROM (SELECT GGMK FROM '{nombre_tabla}' UNION SELECT GMK FROM '{nombre_tabla}' UNION SELECT MK FROM '{nombre_tabla}' UNION SELECT SMK FROM '{nombre_tabla}' WHERE GGMK IS NOT 0)"
        )
        todas_maestras = [i[0] for i in self.cursor.fetchall()]

        # extraer todos los codigos de las llaves de la tabla
        self.cursor.execute(f"SELECT K FROM '{self.nombre_tabla}'")
        llaves_usadas = [i[0] for i in self.cursor.fetchall()]

        # eliminar botones de Rehacer y Guardar del menu
        self.buttons[1].destroy()
        self.buttons[3].destroy()

        arbol = self.genera_texto_arbol(detalle=False)
        self.muestra_arbol(arbol)

    def muestra_arbol(self):
        self.vista.mostrar(self.ggmk)

    def valida_llave_es_unica(self, llave):
        if self.llaves_usadas.count(llave) == 1:
            return 1
        return 0

    def valida_llave_no_cruzada(self, cilindro, mis_maestras):
        for maestra in self.todas_maestras:
            if maestra in mis_maestras:
                continue
            if valida_llave_abre_cilindro(maestra, cilindro):
                return 0

        return 1


def crea_cilindro(ggmk, key):
    ggmk = (int(i) for i in ggmk)
    key = (int(i) for i in key)

    cilindro = []
    for g, k in zip(ggmk, key):
        if g == k:
            cilindro.append(f"[{g}]")
        else:
            cilindro.append(f"[{min(g,k)}:{abs(g-k)}]")

    return "".join(cilindro)


def valida_codigo(codigo):

    # string to tuple
    codigo = tuple(int(i) for i in codigo)

    # no puede haber 8 o 9 de diferencia entre pines
    for position in range(len(codigo) - 1):
        c = codigo[position]
        n = codigo[position + 1]
        if abs(n - c) >= 8:
            return False

    # no puede haber una secuencia [par-impar-par-impar-par-impar] o [impar-par-impar-par-impar-par]
    test = [int(i) % 2 for i in codigo]
    if test == [0, 1, 0, 1, 0, 1] or test == [1, 0, 1, 0, 1, 0]:
        return False

    # no pueden haber tres pines seguidos iguales
    for pos in range(4):
        if codigo[pos : pos + 3].count(codigo[pos]) == 3:
            return False

    return True


def valida_llave_es_unica(llave, llaves_usadas):
    if llaves_usadas.count(llave) == 1:
        return 1
    return 0


def valida_llave_abre_cilindro(llave, cilindro):

    opciones = []
    for pos in cilindro.split("]")[:-1]:
        if ":" in pos:
            opciones.append((pos[1], int(pos[1]) + int(pos[3])))
        else:
            opciones.append((pos[1],))

    cilindros = []
    for a in opciones[0]:
        for b in opciones[1]:
            for c in opciones[2]:
                for d in opciones[3]:
                    for e in opciones[4]:
                        for f in opciones[5]:
                            cilindros.append(f"{a}{b}{c}{d}{e}{f}")

    if llave in cilindros:
        return 1

    return 0


def valida_llave_no_cruzada(cilindro, mis_maestras, todas_maestras):
    for maestra in todas_maestras:
        if maestra in mis_maestras:
            continue
        if valida_llave_abre_cilindro(maestra, cilindro):
            return 0

    return 1
