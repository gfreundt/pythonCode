from tkinter import IntVar, END
import ttkbootstrap as ttkb
from ttkbootstrap.tableview import Tableview
from datetime import datetime as dt

from proyectos.cargar2 import Cargar


class Nuevo:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def gui_pre_cargar(self):

        # abrir dialogo para elegir archivo
        cargar = Cargar(self)
        cargar.gui("libros")

    def gui_post_cargar(self):

        # capturar nombre de proyecto y libro que vienen del dialogo para elegir archivo
        self.nombre_libro = self.archivo_elegido[0]

        self.window = ttkb.Toplevel()
        self.window.geometry("1600x1100")
        self.text_area = ttkb.Text(self.window, height=100, width=80)
        self.text_area.place(x=10, y=60)

        self.data = []
        self.s1_valor = IntVar(self.window, value=1)

        self.nivel_boton = 0
        self.secuencia_gmk = -1

        self.b1 = ttkb.Button(
            self.window, text="Agrega GMK", command=lambda: self.menu_agrega_gmk()
        )
        self.b1.place(x=700, y=70)

        self.b2 = ttkb.Button(
            self.window, text="Agrega MK", command=self.menu_agrega_mk
        )
        self.b2.place(x=800, y=120)
        self.b2.config(state="disabled")

        self.b3 = ttkb.Button(
            self.window,
            text="Nivel Completo",
            command=lambda: self.menu_nivel_completo(),
        )
        self.b3.place(x=900, y=90)

        self.b4 = ttkb.Button(self.window, text="Deshacer", command=self.menu_deshacer)
        self.b4.place(x=900, y=170)

        self.s1 = ttkb.Spinbox(
            self.window, from_=1, to=99, textvariable=self.s1_valor, width=2
        )
        self.s1.place(x=800, y=170)
        self.s1.config(state="disabled")

        self.muestra_arbol()

    def menu_agrega_gmk(self):
        self.b1.config(state="disabled")
        self.b2.config(state="active")

        self.data.append([])
        self.nivel_boton = 1
        self.secuencia_gmk += 1

        self.muestra_arbol()

    def menu_agrega_mk(self):
        self.nivel_boton = 2
        self.b2.config(state="disabled")
        self.s1.config(state="normal")
        self.data[-1].append(0)

        self.muestra_arbol()

    def menu_agrega_k(self):
        self.data[self.secuencia_gmk].append(self.s1_valor.get())
        self.b4.config(state="disabled")
        self.s1.config(state="disabled")

        self.muestra_arbol()

    def menu_nivel_completo(self):
        if self.nivel_boton == 0:
            self.asigna_llaves()
            self.window.destroy()
            return
        elif self.nivel_boton == 1:
            self.nivel_boton = 0
            self.b1.config(state="active")
            self.b2.config(state="disabled")
        elif self.nivel_boton == 2:
            self.nivel_boton = 1
            self.data[-1][-1] = self.s1_valor.get()
            self.s1.config(state="disabled")
            self.b2.config(state="active")

        self.muestra_arbol()

    def menu_deshacer(self):
        return

    def asigna_llaves(self):

        proyecto_nombre = "nombre"
        proyecto_notas = "notas"

        # determina codigo secuencial del proyecto
        self.cursor.execute(
            f"SELECT COUNT(GGMK) FROM proyectos WHERE Libro_Origen = '{self.nombre_libro}'"
        )
        _secuencial = self.cursor.fetchall()
        nombre_proyecto = f"P{self.nombre_libro[1:]}-{int(_secuencial[0][0]) if _secuencial else 0:03d}"

        # copia estructura de tabla de libro a nuevo proyecto
        self.cursor.execute(f"DROP TABLE IF EXISTS '{nombre_proyecto}'")
        self.cursor.execute(
            f"""CREATE TABLE '{nombre_proyecto}'

            ('LibroOrigen' TEXT,
            'Secuencia' TEXT,
            'Jerarquia' TEXT,
            'CodigoLlave' TEXT,
            'Nombre' TEXT,
            'Copias' TEXT,
            'CodigoPuerta' TEXT,
            'TipoPuerta' TEXT,
            'TipoCerradura' TEXT,
            'Zona1' TEXT,
            'Zona2' TEXT,
            'Zona3' TEXT,
            'Zona4' TEXT,
            'ZonaCodigo' TEXT,
            'Notas' TEXT,
            'FabricadoLlaveCopias' NUMERIC,
            'FabricadoCilindro' NUMERIC )"""
        )

        # extrae del libro la GGMK
        self.cursor.execute(f"SELECT DISTINCT GGMK FROM '{self.nombre_libro}'")
        ggmk_codigo = self.cursor.fetchone()[0]
        self.cursor.execute(
            f"""INSERT INTO '{nombre_proyecto}' 
            
            (LibroOrigen, 
            Secuencia, 
            Jerarquia, 
            CodigoLlave, 
            Copias, 
            FabricadoLlaveCopias, 
            FabricadoCilindro)

            VALUES 

            ('{self.nombre_libro}','GGMK','GGMK',{ggmk_codigo},1,0,0)"""
        )

        # extrae del libro la cantidad de GMK necesarias para el proyecto
        self.cursor.execute(
            f"SELECT DISTINCT GMK FROM '{self.nombre_libro}' LIMIT {len(self.data)}"
        )
        required_gmks = [i[0] for i in self.cursor.fetchall()]

        # extrae del libro todas las MK necesarias para el proyecto
        total_mks = total_smks = total_ks = 0
        for g, gmk in enumerate(required_gmks):
            # genera secuencia de GMK e inserta
            self.cursor.execute(
                f"SELECT Secuencia, GMK FROM '{self.nombre_libro}' WHERE GMK='{gmk}'"
            )
            mk_secuencia = self.cursor.fetchone()
            self.cursor.execute(
                f"INSERT INTO '{nombre_proyecto}' (LibroOrigen, Secuencia, Jerarquia, CodigoLlave, Copias, FabricadoLlaveCopias, FabricadoCilindro) VALUES ('{self.nombre_libro}','GM{mk_secuencia[0][:4]}','GMK',{mk_secuencia[1]},1,0,0)"
            )

            self.cursor.execute(
                f"SELECT DISTINCT MK FROM '{self.nombre_libro}' WHERE GMK = '{gmk}' LIMIT {len(self.data[g])}"
            )
            required_mks = [i[0] for i in self.cursor.fetchall()]
            total_mks += len(required_mks)

            # llena la tabla del proyecto con las llaves necesarias
            for m, mk in enumerate(required_mks):
                # genera secuencia de MK e inserta
                self.cursor.execute(
                    f"SELECT Secuencia, MK FROM '{self.nombre_libro}' WHERE MK='{mk}'"
                )
                mk_secuencia = self.cursor.fetchone()
                self.cursor.execute(
                    f"INSERT INTO '{nombre_proyecto}' (LibroOrigen, Secuencia, Jerarquia, CodigoLlave, Copias, FabricadoLlaveCopias, FabricadoCilindro) VALUES ('{self.nombre_libro}','M{mk_secuencia[0][:8]}','MK',{mk_secuencia[1]},1,0,0)"
                )
                # inserta todas las k necesarias para esa mk
                cmd = f"""  INSERT INTO '{nombre_proyecto}' (LibroOrigen, Secuencia, Jerarquia, CodigoLlave, Copias, FabricadoLlaveCopias, FabricadoCilindro)
                                SELECT '{self.nombre_libro}', Secuencia, 'K', K, 1, 0, 0
                                FROM '{self.nombre_libro}' WHERE MK = '{mk}' LIMIT {self.data[g][m]}"""
                self.cursor.execute(cmd)

        # calcula cantidad de K en proyecto
        self.cursor.execute(
            f"SELECT COUNT (*) FROM '{nombre_proyecto}' WHERE Secuencia LIKE 'K-%'"
        )
        total_ks = self.cursor.fetchone()[0]

        # TODO: calcula cantidad de SMK en proyecto que no sean 0
        total_smks = 0

        # inserta todos los datos del nuevo proyecto en la tabla indice
        _record = (
            nombre_proyecto,
            self.nombre_libro,
            self.nombre_libro[2:8],
            proyecto_nombre,
            proyecto_notas,
            dt.strftime(dt.now(), "%Y-%m-%d %H:%M:%S"),
            len(required_gmks),
            total_mks,
            total_smks,
            total_ks,
        )

        self.cursor.execute(
            f"""INSERT INTO 'proyectos' VALUES ({(',?'*10)[1:]})""", _record
        )

        self.conn.commit()

    def muestra_arbol(self):
        self.text_area.delete("1.0", "end")
        self.text_area.insert(END, self.genera_texto_arbol())

    def genera_texto_arbol(self):
        totalx = 0
        total = 1

        output = f"GGMK\n"
        for p, gmk in enumerate(self.data, start=1):
            total += 1
            output += "|\n"
            output += f"|{'-'*9}GMK-{p:02d}\n"

            for q, mk in enumerate(gmk, start=1):
                total += 1
                output += f"{' ' if p==len(self.data) else '|'}{' '*9}|\n"
                output += f"|{' '*9}{' ' if p==len(self.data) else '|'}{'-'*9} MK-{p:02d}-{q:02d}\n"
                output += f"{' ' if p==len(self.data) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{' '*10}|\n"

                output += f"{' ' if p==len(self.data) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{' '*10}Unicas: {mk}\n"
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
