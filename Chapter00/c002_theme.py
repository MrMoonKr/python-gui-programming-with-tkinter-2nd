import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Tkinter Application ( 애플리케이션 )")
        self.minsize(640, 480)
        self.center_window(800, 600)

        self.style = ttk.Style(self)
        self._init_menubar()

    def _init_menubar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy")
        edit_menu.add_command(label="Paste")
        menubar.add_cascade(label="Edit", menu=edit_menu)

        theme_menu = tk.Menu(menubar, tearoff=0)
        self.theme_var = tk.StringVar(value=self.style.theme_use())
        for theme_name in self.style.theme_names():
            theme_menu.add_radiobutton(
                label=theme_name,
                value=theme_name,
                variable=self.theme_var,
                command=self.apply_theme,
            )
        menubar.add_cascade(label="Theme", menu=theme_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    def apply_theme(self):
        self.style.theme_use(self.theme_var.get())

    def show_about(self):
        messagebox.showinfo("About", "Tkinter Theme Demo")

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