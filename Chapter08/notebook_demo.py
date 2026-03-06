import tkinter as tk
from tkinter import ttk


# Legacy code
# root = tk.Tk()
#
# # create notebook
# notebook = ttk.Notebook(root)
# notebook.grid()
#
#
# # Create some large widgets
# banana_facts = [
#     'Banana trees are of the genus Musa.',
#     'Bananas are technically berries.',
#     'All bananas contain small amounts of radioactive potassium.'
#     'Bananas are used in paper and textile manufacturing.'
# ]
#
# plantain_facts = [
#     'Plantains are also of genus Musa.',
#     'Plantains are starchier and less sweet than bananas',
#     'Plantains are called "Cooking Bananas" since they are'
#     ' rarely eaten raw.'
# ]
#
# b_label = ttk.Label(notebook, text='\n\n'.join(banana_facts))
# p_label = ttk.Label(notebook, text='\n\n'.join(plantain_facts))
#
# # Add the widgets to the notebook
# notebook.add(b_label, text='Bananas', padding=20)
# notebook.add(p_label, text='Plantains', padding=20)
#
# # we could also use insert:
# # notebook.insert(1, p_label, text='Plantains', padding=20)
#
# # Set up underline
# notebook.tab(0, underline=0)
# notebook.tab(1, underline=0)
#
# # enable keyboard controls for the tab
# notebook.enable_traversal()
#
# # Select the first tab
# #notebook.select(0)
#
# # or by widgets
# notebook.select(p_label)
#
# root.mainloop()
#

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Notebook Demo")
        self.minsize(640, 480)
        self.center_window(800, 600)

        self.style = ttk.Style(self)
        self.theme_var = tk.StringVar(value=self.style.theme_use())
        self.notebook: ttk.Notebook = None

        self.banana_facts = [
            "Banana trees are of the genus Musa.",
            "Bananas are technically berries.",
            "All bananas contain small amounts of radioactive potassium.",
            "Bananas are used in paper and textile manufacturing.",
        ]
        self.plantain_facts = [
            "Plantains are also of genus Musa.",
            "Plantains are starchier and less sweet than bananas.",
            'Plantains are called "Cooking Bananas" since they are',
            "rarely eaten raw.",
        ]

        self._build_menu()
        self._build_body()

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
        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        self._build_notebook(container)

    def _build_notebook(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        banana_tab = self._create_fact_tab(
            self.notebook,
            self.banana_facts,
        )
        plantain_tab = self._create_fact_tab(
            self.notebook,
            self.plantain_facts,
        )

        self.notebook.add(banana_tab, text="Bananas", padding=20)
        self.notebook.add(plantain_tab, text="Plantains", padding=20)

        self.notebook.tab(0, underline=0)
        self.notebook.tab(1, underline=0)
        self.notebook.enable_traversal()
        self.notebook.select(plantain_tab)

    def _create_fact_tab(self, parent, facts):
        frame = ttk.Frame(parent, padding=16)
        label = ttk.Label(frame, text="\n\n".join(facts), justify=tk.LEFT)
        label.pack(anchor=tk.W, fill=tk.BOTH, expand=True)
        return frame

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
