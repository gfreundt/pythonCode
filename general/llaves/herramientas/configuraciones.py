import ttkbootstrap as ttkb


class Configuraciones:

    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def gui(self):

        # definir ventana
        self.window = ttkb.Toplevel()
        self.window.geometry("400x150")

        ttkb.Label(self.window, text="Disponible en Siguiente Version").pack(
            padx=10, pady=10
        )
        ttkb.Button(
            self.window, text="Regresar", command=self.regresar, bootstyle="danger"
        ).pack(padx=10, pady=10)

    def regresar(self):
        self.window.destroy()
