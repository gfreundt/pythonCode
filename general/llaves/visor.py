from copy import deepcopy as copy
from tkinter import Tk, Text, END, Button
from pprint import pprint
from datetime import datetime as dt
import json
import uuid
import openpyxl as pyxl


class Visor:

    def __init__(self, configuracion):
        self.configuracion = configuracion
        self.fecha = dt.strftime(dt.now(), "%Y-%m-%d")
        self.file_name = f"L{str(uuid.uuid4())[-10:]}.json"
        self.detalle = False

    def mostrar(self, ggmk):
        self.ggmk = ggmk

        # crear nueva ventana, dimensionar
        self.window = Tk()
        self.window.geometry("1000x1300")

        # definir y colocar botones de menu
        self.buttons = [
            Button(self.window, text="Detalle", command=self.menu_detalle),
            Button(self.window, text="Exportar XLS", command=self.menu_exportar_xls),
            Button(self.window, text="Exportar PDF", command=self.menu_exportar_pdf),
            Button(self.window, text="Guardar", command=self.menu_guardar),
            Button(self.window, text="Regresar", command=self.arbol_regresar),
        ]
        for x, button in enumerate(self.buttons, start=1):
            button.place(x=x * 75, y=20)

        # crear zona donde se muestra el texto del arbol
        self.text_area = Text(self.window, height=100, width=130)
        self.text_area.place(x=10, y=60)

        # genera el texto del arbol al visor y mostrar
        arbol = self.genera_texto_arbol(detalle=self.detalle)
        self.muestra_arbol(arbol)

    def menu_detalle(self):
        self.detalle = not self.detalle
        arbol = self.genera_texto_arbol(detalle=self.detalle)
        self.muestra_arbol(arbol)

    def menu_rehacer(self):
        self.crea_libro(codigo_ggmk=copy(self.ggmk["codigo"]))
        self.detalle = False
        arbol = self.genera_texto_arbol(detalle=self.detalle)
        self.muestra_arbol(arbol)

    def menu_exportar_xls(self):
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

    def menu_exportar_pdf(self):
        return

    def menu_guardar(self):
        with open(self.file_name, "w") as outfile:
            json_object = json.dumps(self.ggmk, indent=4)
            outfile.write(json_object)

    def arbol_regresar(self):
        self.window.destroy()

    def genera_texto_arbol(self, detalle):
        totalx = 0
        total = 1

        output = f"GGMK | Codigo:{self.ggmk['codigo']}\n"
        for p, gmk in enumerate(self.ggmk["subkeys"], start=1):
            total += 1
            output += "|\n"
            output += f"|{'-'*9}GMK-{p:02d} <> Codigo:{gmk['codigo']}\n"

            for q, mk in enumerate(gmk["subkeys"], start=1):
                total += 1
                output += f"{' ' if p==len(self.ggmk['subkeys']) else '|'}{' '*9}|\n"
                output += f"{' ' if p==len(self.ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys'])+1 else '|'}{'-'*9} MK-{p:02d}-{q:02d} <> Codigo:{mk['codigo']}\n"
                output += f"{' ' if p==len(self.ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}|\n"

                if not detalle:
                    output += f"{' ' if p==len(self.ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}Unicas: {len(mk['subkeys'])}\n"
                    totalx += len(mk["subkeys"])
                else:
                    for r, key in enumerate(mk["subkeys"], start=1):
                        totalx += 1
                        output += f"{' ' if p==len(self.ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}{' ' if r==len(mk['subkeys'])+1 else '|'}{'-'*9}{key['secuencia']} <> Codigo:{key['codigo']} - Cilindro:{key['cilindro']:<30} {key['cilindro'].count(':')} MP) \n"

        output += f"\nTotal Llaves: {total+totalx:,}\n"
        output += f"Total Puertas: {totalx:,}\n"

        return output

    def muestra_arbol(self, arbol):
        self.text_area.delete("1.0", "end")
        self.text_area.insert(END, arbol)


