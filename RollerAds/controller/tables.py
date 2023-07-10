from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ListProperty
from kivy.graphics import Rectangle, Color
from kivy.clock import mainthread


class TableColumnTitles(BoxLayout):
    def __init__(self, instance, column_data, **kwargs):
        super().__init__(**kwargs)
        self.instance = instance
        # background
        with self.canvas.before:
            self.shape_color = Color(rgba=(0.004, 0.5, 0.125, 1))
            self.shape = Rectangle(
                pos=self.pos,
                size=self.pos,
            )
            self.bind(size=self.update_shape)
        # create headers
        for c, col in enumerate(column_data):
            self.add_widget(
                Label(
                    text=f"[size=18][b]{col}",
                    markup=True,
                    pos_hint={"center_x": (c + 0.5) / 4, "center_y": 0.5},
                    size_hint=(self.instance.col_widths[c], 1),
                )
            )

    def update_shape(self, *_args):
        # maintain dimensions in case window is resized
        self.shape.size = self.size
        self.shape.pos = self.pos


class TableRow(ButtonBehavior, BoxLayout):
    bg_color = ListProperty([0.392, 0.629, 0.929, 1])

    def __init__(self, instance, row_num, **kwargs):
        super().__init__(**kwargs)
        # set widget attributes
        self.orientation = "horizontal"
        self.instance = instance
        self.row = row_num
        # print data into rows/columns
        for c, _ in enumerate(self.instance.column_data):
            self.add_widget(
                Label(
                    text=f"[size=16][color=000]{self.instance.row[c]}",
                    markup=True,
                    size_hint=(self.instance.col_widths[c], 1),
                    pos_hint={"center_x": (c + 0.5) / 4, "center_y": 0.5},
                )
            )
        self.draw()

    def draw(self, *_args):
        # background for each row
        with self.canvas.before:
            self.shape_color = (
                Color(rgba=(0.792, 0.914, 0.961, 1))
                if self.row % 2 == 0
                else Color(rgba=(0.95, 0.95, 0.95, 1))
            )
            self.shape = Rectangle(
                pos=self.pos,
                size=self.size,
            )
            self.bind(size=self.update_shape)

    def on_press(self, *_args):
        # skip if clicked row is same as selected row
        if self.row == self.instance.previous_row:
            return
        # set color of selected row
        self.bg_color = (0.392, 0.629, 0.9, 1)
        # set color of deselected row
        if self.instance.previous_row > -1:
            self.instance.row_sel.bg_color = (
                (0.792, 0.914, 0.961, 1)
                if self.instance.previous_row % 2 == 0
                else (0.95, 0.95, 0.95, 1)
            )
        # keep values of selected row for when its deselected
        self.instance.previous_row = self.row
        self.instance.row_sel = self
        self.instance.row_sel_num = self.row

    def update_shape(self, *_args):
        # maintain dimensions in case window is resized
        self.shape.size = [self.size[0], self.size[1] * 0.98]
        self.shape.pos = self.pos

    def on_bg_color(self, *_args):
        # triggered when background color variable value changes
        self.shape_color.rgba = self.bg_color


class Table(BoxLayout):
    column_data = ListProperty()
    row_data = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_row = -1
        self.row_sel_num = -1

        @mainthread
        def delayed():
            self.create_table()

        delayed()

    def create_table(self):
        # calculate column widths
        col = [
            max([len(self.row_data[i][j]) for i, _ in enumerate(self.row_data)])
            for j, _ in enumerate(self.row_data[0])
        ]
        self.col_widths = [i / sum(col) for i in col]

        # build Column Titles
        self.add_widget(TableColumnTitles(self, self.column_data))

        # build Rows and Row Data
        for r, self.row in enumerate(self.row_data):
            self.data_line = TableRow(self, r)
            self.add_widget(self.data_line)

    def update_row_data(self, **kwargs):
        self.row_data = kwargs["row_data"]
        self.clear_widgets()
        self.create_table()

    def update_single_row(self, **kwargs):
        print("**")


class KivyApp(App):
    def build(self):
        column_data = ["Name", "Age", "Gender", "Active", "Zip Code", "Country"]
        row_data = [
            ["Gabriel", "48", "Male", "Yes", "56789", "Peru"],
            ["Juan", "44", "Female", "Yes", "56789", "Peru"],
            ["Pedro", "12", "Male", "Yes", "56789", "Peru"],
            ["Pepe", "34", "Female", "No", "56789", "Peru"],
            ["Claudia", "23", "Female", "No", "56789", "Peru"],
            ["Rodrigo", "99", "Male", "yes", "56789", "Peru"],
            ["Max", "99", "Male", "yes", "56789", "Peru"],
            ["Juan", "44", "Female", "Yes", "56789", "Peru"],
        ]
        return Table(column_data=column_data, row_data=row_data)


if __name__ == "__main__":
    from kivy.core.window import Window

    # Basic Kivy parameters
    Window.size = (1200, 450)
    Window.top, Window.left = 50, 50
    KivyApp().run()
