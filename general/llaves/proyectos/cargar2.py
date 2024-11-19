import ttkbootstrap as ttkb
from ttkbootstrap.tableview import Tableview


class Cargar:

    def __init__(self, previous):

        self.previous = previous
        self.cursor = previous.cursor
        self.conn = previous.conn

    def gui(self, formato):

        self.window = ttkb.Toplevel()
        self.window.geometry("1400x1300")

        # estructura de datos para proyectos
        col_data = [
            "Codigo",
            "Libro Origen",
            "GGMK",
            "Nombre",
            "Notas",
            "Creacion",
            "GMKs",
            "MKs",
            "SMKs",
            "Ks",
        ]

        # cambiar dos campos en caso estructura de datos sea para libros
        if formato == "libros":
            col_data[1] = "GGMK"
            col_data[2] = "Formato"

        # extrae y limpia datos
        self.cursor.execute(f"SELECT * FROM '{formato}'")
        row_data = self.aplica_formato(self.cursor.fetchall())

        self.dt_view = Tableview(
            self.window,
            coldata=col_data,
            rowdata=row_data,
            autofit=True,
            autoalign=True,
            height=min(42, len(row_data)),
        )

        self.dt_view.pack(padx=20, pady=10)

        # crea y coloca botones
        ttkb.Button(
            self.window,
            text="Seleccionar",
            command=self.seleccionar,
        ).pack(pady=20)

        ttkb.Button(
            self.window,
            text="Regresar",
            command=self.regresar,
        ).pack(pady=20)

    def aplica_formato(self, data):
        new_data = [list(i) for i in data]

        # elimina cero
        for i, m in enumerate(data):
            for j, n in enumerate(m):
                if n == 0:
                    new_data[i][j] = ""

        return new_data

    def seleccionar(self):
        self.previous.archivo_elegido = self.dt_view.get_rows(selected=True)[0].values
        self.window.destroy()
        self.previous.gui_post_cargar()

    def regresar(self):
        self.window.destroy()
