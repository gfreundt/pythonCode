from tkinter import IntVar, END, BooleanVar
import ttkbootstrap as ttkb
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime as dt

from proyectos.cargar import Cargar


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

        # definir ventana
        self.window = ttkb.Toplevel()
        self.window.geometry("1600x1100")

        # definir y colocar frames de ventana principal
        self.frame_left = ttkb.Frame(self.window)
        self.frame_right = ttkb.Frame(self.window)
        self.frame_bottom = ttkb.Frame(self.window)
        self.frame_left.grid(row=0, column=0)
        self.frame_right.grid(row=0, column=1)
        self.frame_bottom.grid(row=1, column=0)

        # crear zona de texto en frame izquierdo
        self.text_area = ttkb.Text(self.frame_left, height=40, width=80)
        self.text_area.pack()

        # crear resumen de avance, opciones en frame derecho
        self.llaves_aleatorias = BooleanVar(value=False)
        self.o1 = ttkb.Checkbutton(
            self.frame_right,
            text="Codigos de Llaves Aleatorios",
            variable=self.llaves_aleatorias,
            bootstyle="primary",
        )
        self.no_reutilizar_llaves = BooleanVar(value=False)
        self.o2 = ttkb.Checkbutton(
            self.frame_right,
            text="No Usar Llaves de Otro Proyecto",
            variable=self.no_reutilizar_llaves,
            bootstyle="primary",
        )
        ttkb.Label(self.frame_right, text="Resumen:").pack(anchor="nw", pady=5, padx=15)
        self.t1 = ttkb.Label(self.frame_right, text="")
        self.t1.pack(anchor="nw", pady=0, padx=15)
        self.t2 = ttkb.Label(self.frame_right, text="")
        self.t2.pack(anchor="nw", pady=20, padx=15)
        ttkb.Label(self.frame_right, text="Opciones:").pack(
            anchor="nw", pady=5, padx=15
        )
        self.o1.pack(anchor="nw", padx=15, pady=5)
        self.o2.pack(anchor="nw", padx=15, pady=10)

        # crear botones y spinbox para agregar llaves y estructura al arbol
        self.data = []
        self.s1_valor = IntVar(self.window, value=1)

        self.nivel_boton = 0
        self.secuencia_gmk = -1

        self.b1 = ttkb.Button(
            self.frame_bottom, text="Agrega GMK", command=lambda: self.menu_agrega_gmk()
        )
        self.b1.grid(row=0, column=0, padx=20, pady=20)

        self.b2 = ttkb.Button(
            self.frame_bottom, text="Agrega MK", command=self.menu_agrega_mk
        )
        self.b2.grid(row=0, column=1, padx=20, pady=20)
        self.b2.config(state="disabled")

        ttkb.Label(self.frame_bottom, text="K :").grid(row=0, column=2)

        self.s1 = ttkb.Spinbox(
            self.frame_bottom, from_=1, to=99, textvariable=self.s1_valor, width=2
        )
        self.s1.grid(row=0, column=3, padx=20, pady=20)
        self.s1.config(state="disabled")

        self.b3 = ttkb.Button(
            self.frame_bottom,
            text="Nivel Completo",
            command=lambda: self.menu_nivel_completo(),
        )
        self.b3.grid(row=0, column=4, padx=20, pady=20)

        self.b4 = ttkb.Button(
            self.frame_bottom,
            text="Deshacer",
            bootstyle="warning",
            command=self.menu_deshacer,
        )
        self.b4.grid(row=0, column=5, padx=20, pady=20)
        self.b4.config(state="disabled")

        # llenar area de texto con datos de arbol actualizado
        self.muestra_arbol()

    def menu_agrega_gmk(self):
        self.b1.config(state="disabled")
        self.b2.config(state="active")
        self.b3.config(bootstyle="primary", text="Nivel Completo")

        self.data.append([])
        self.nivel_boton = 1
        self.secuencia_gmk += 1

        self.menu_agrega_mk()
        self.b4.config(state="active")

        # llenar area de texto con datos de arbol actualizado
        self.muestra_arbol()

    def menu_agrega_mk(self):
        self.nivel_boton = 2
        self.b2.config(state="disabled")
        self.s1.config(state="normal")
        self.data[-1].append(0)
        self.b4.config(state="active")

        # llenar area de texto con datos de arbol actualizado
        self.muestra_arbol()

    def menu_agrega_k(self):
        self.data[self.secuencia_gmk].append(self.s1_valor.get())
        self.b4.config(state="disabled")
        self.s1.config(state="disabled")
        self.b4.config(state="active")
        # llenar area de texto con datos de arbol actualizado
        self.muestra_arbol()

    def menu_nivel_completo(self):
        if self.nivel_boton == 0:
            # solamente si hay llaves elegidas, asignar llaves y cerrar
            if self.data:
                self.asigna_llaves()
            self.window.destroy()
            return
        elif self.nivel_boton == 1:
            self.nivel_boton = 0
            self.b1.config(state="active")
            self.b2.config(state="disabled")
            self.b3.config(bootstyle="success", text="Finalizar")
        elif self.nivel_boton == 2:
            self.nivel_boton = 1
            self.data[-1][-1] = self.s1_valor.get()
            self.s1.config(state="disabled")
            self.b2.config(state="active")

        # llenar area de texto con datos de arbol actualizado
        self.muestra_arbol()

    def menu_deshacer(self):

        # no ejecutar deshacer si solo hay GGMK y nada mas
        if not self.data:
            return

        # eliminar ultimo grupo de llaves insertada
        self.data[-1].pop()

        # si eliminacion deja lista de MK en blanco, eliminar lista en blanco
        if not self.data[-1]:
            self.data.pop()
            self.b1.config(state="active")
            self.b2.config(state="disabled")
            self.nivel_boton = 1
            self.b3.config(bootstyle="success", text="Finalizar")
        else:
            self.b1.config(state="disabled")
            self.b2.config(state="active")
            self.nivel_boton = 0
            self.b3.config(bootstyle="primary", text="Nivel Completo")

        # si no hay llaves elegidas, bloquear boton deshacer
        if not self.data:
            self.b4.config(state="disabled")

        # llenar area de texto con datos de arbol actualizado
        self.muestra_arbol()

    def asigna_llaves(self):
        # controla si hay problemas en estructura de libro con lo solicitado por el proyecto
        _alerta_minimo_llaves = ""

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
            'Zona5' TEXT,
            'Notas' TEXT,
            'FabricadoLlaveCopias' NUMERIC,
            'FabricadoCilindro' NUMERIC)"""
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

        # activa alerta si no se cumple el minimo de GMKs solicitada por estructura de usuario
        if len(required_gmks) < len(self.data):
            _alerta_minimo_llaves += "> Faltan GMKs.\n"

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

            # activa alerta si no se cumple el minimo de MKs solicitada por estructura de usuario
            if len(required_mks) < len(self.data[g]):
                _alerta_minimo_llaves += f"> Faltan MKs en GMK-{g+1:02d}.\n"

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
                # genera secuencia de Ks
                cmd = f"""  SELECT '{self.nombre_libro}', Secuencia, 'K', K, 1, 0, 0
                            FROM '{self.nombre_libro}' WHERE MK = '{mk}' 
                            {'ORDER BY RANDOM()' if self.llaves_aleatorias.get() else ''} 
                            LIMIT {self.data[g][m]}"""
                self.cursor.execute(cmd)
                k_secuencia = self.cursor.fetchall()

                # activa alerta si no se cumple el minimo de Ks solicitada por estructura de usuario
                if len(k_secuencia) < self.data[g][m]:
                    _alerta_minimo_llaves += f"> Faltan Ks en MK-{g+1:02d}-{m+1:03d}.\n"

                # inserta todas las k seleccionadas en proyecto
                self.cursor.executemany(
                    f"""  INSERT INTO '{nombre_proyecto}'
                          (LibroOrigen, Secuencia, Jerarquia, CodigoLlave, Copias, FabricadoLlaveCopias, FabricadoCilindro) 
                          VALUES (?,?,?,?,?,?,?)""",
                    k_secuencia,
                )

        # si la estructura del libro no da para la solicitud del proyecto, mensaje de error, no se graba y regresa a menu anterior
        if _alerta_minimo_llaves:
            self.cursor.execute(f"DROP TABLE '{nombre_proyecto}'")
            Messagebox.show_warning(
                parent=self.window,
                title="Estructura de Libro Invalida",
                message=f"""El libro {self.nombre_libro} no tiene la estructura necesaria para este proyecto.\n
                {_alerta_minimo_llaves}
                Elegir un libro con formato diferente o cambiar estructura del proyecto.""",
            )
            return

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

        # crea entradas en tabla de zonas para proyecto recien creado
        self.cursor.execute("SELECT * FROM 'Zonas'")

        # calcula siguiente ID, si no hay empieza de =1
        next_recordID = self.cursor.fetchall()
        next_recordID = -1 if not next_recordID else next_recordID[-1][0]

        # inserta 'Zona#' como nombre de categoria para las 5 zonas
        for i in range(1, 6):
            self.cursor.execute(
                f"""INSERT INTO 'Zonas' VALUES (?,?,?,?)""",
                (next_recordID + i, nombre_proyecto, i, f"Zona{i}"),
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

        self.t1.config(text=f"Total Llaves: {total + totalx}")
        self.t2.config(text=f"Total Puertas: {totalx}")

        return output

    def aplica_formato(data):
        new_data = [list(i) for i in data]

        # elimina cero
        for i, m in enumerate(data):
            for j, n in enumerate(m):
                if n == 0:
                    new_data[i][j] = ""

        return new_data
