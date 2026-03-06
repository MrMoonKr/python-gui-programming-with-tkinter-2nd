import tkinter as tk
from tkinter import ttk


# Legacy code
# berries = [
#     {'number': '1', 'parent': '',  'value': 'Raspberry'},
#     {'number': '4', 'parent': '1', 'value': 'Red Raspberry'},
#     {'number': '5', 'parent': '1', 'value': 'Blackberry'},
#     {'number': '2', 'parent': '', 'value': 'Banana'},
#     {'number': '3', 'parent': '', 'value': 'Strawberry'}
# ]
#
# root = tk.Tk()
#
# tv = ttk.Treeview(root, columns=['value'])
# tv.heading('#0', text='Node')
# tv.heading('value', text='Value')
# tv.grid(sticky='news')
#
# for berry in berries:
#     tv.insert(
#         berry['parent'],
#         'end',
#         iid=berry['number'],
#         text=berry['number'],
#         values=[berry['value']]
#     )
#
# root.mainloop()
#

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Hierarchy Example")
        self.minsize(480, 320)
        self.center_window(640, 400)

        self.style = ttk.Style(self)
        self.berries = [
            {"number": "1", "parent": "", "value": "Raspberry"},
            {"number": "4", "parent": "1", "value": "Red Raspberry"},
            {"number": "5", "parent": "1", "value": "Blackberry"},
            {"number": "2", "parent": "", "value": "Banana"},
            {"number": "3", "parent": "", "value": "Strawberry"},
        ]
        self.theme_var = tk.StringVar(value=self.style.theme_use())
        self.treeview: ttk.Treeview = None

        self._build_menu()
        self._build_body()
        self._populate_treeview()

    def _build_menu(self):
        menu_bar = ttk.Frame(self, padding=(8, 6))
        menu_bar.pack(side=tk.TOP, fill=tk.X)

        theme_menu = tk.Menu(self, tearoff=0)
        for theme_name in self.style.theme_names():
            theme_menu.add_radiobutton(
                label=theme_name,
                value=theme_name,
                variable=self.theme_var,
                command=self.apply_theme,
            )
        self._add_menu_button(menu_bar, "Theme", theme_menu)

    def _build_body(self):
        container = ttk.Frame(self, padding=6)
        container.pack(fill=tk.BOTH, expand=True)

        self._build_treeview(container)

    def _build_treeview(self, parent):
        self.treeview = ttk.Treeview(parent, columns=("value",))
        self.treeview.heading("#0", text="Node")
        self.treeview.heading("value", text="Value")
        self.treeview.column("#0", stretch=True)
        self.treeview.column("value", stretch=True)
        self.treeview.pack(fill=tk.BOTH, expand=True)

    def _populate_treeview(self):
        for berry in self.berries:
            self.treeview.insert(
                berry["parent"],
                tk.END,
                iid=berry["number"],
                text=berry["number"],
                values=(berry["value"],),
            )

    def _add_menu_button(self, parent, text, menu):
        button = ttk.Menubutton(parent, text=text, direction="below")
        button.pack(side=tk.LEFT, padx=(0, 4))
        button["menu"] = menu

    def apply_theme(self):
        self.style.theme_use(self.theme_var.get())

    def center_window(self, width: int, height: int):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = int((screen_w - width) / 2)
        y = int((screen_h - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
