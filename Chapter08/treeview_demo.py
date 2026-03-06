import tkinter as tk
from pathlib import Path
from tkinter import ttk


# Legacy code
# # Set up root window
# root = tk.Tk()
#
# # Create list of paths
# paths = Path('.').glob('**/*')
#
#
# # Create and configure treeview
# tv = ttk.Treeview(
#   root, columns=['size', 'modified'], selectmode='none'
# )
# tv.heading('#0', text='Name')
# tv.heading('size', text='Size', anchor='center')
# tv.heading('modified', text='Modified', anchor='e')
# tv.column('#0', stretch=True)
# tv.column('size', width=200)
#
# tv.pack(expand=True, fill='both')
#
# # Populate Treeview
# for path in paths:
#   meta = path.stat()
#   parent = str(path.parent)
#   if parent == '.':
#     parent = ''
#   tv.insert(
#     parent,
#     'end',
#     iid=str(path),
#     text=str(path.name),
#     values=[meta.st_size, meta.st_mtime]
#   )
#
# def sort(tv, col, parent='', reverse=False):
#   """Sort the given column of the treeview"""
#
#   # build a sorting list
#   sort_index = list()
#   for iid in tv.get_children(parent):
#     sort_value = tv.set(iid, col) if col != '#0' else iid
#     sort_index.append((sort_value, iid))
#
#   # sort the list
#   sort_index.sort(reverse=reverse)
#
#   # move each node according to its index in the sort list
#   for index, (_, iid) in enumerate(sort_index):
#     tv.move(iid, parent, index)
#
#     # sort each child node
#     sort(tv, col, parent=iid, reverse=reverse)
#
#   # If this is the top level, reset the headings for reverse sort
#   if parent == '':
#     tv.heading(
#       col,
#       command=lambda col=col: sort(tv, col, reverse=not reverse)
#     )
#
# for cid in ['#0', 'size', 'modified']:
#   tv.heading(cid, command=lambda col=cid: sort(tv, col))
#
#
# status = tk.StringVar()
# tk.Label(root, textvariable=status).pack(side=tk.BOTTOM)
#
# def show_directory_stats(*_):
#   clicked_path = Path(tv.focus())
#   num_children = len(list(clicked_path.iterdir()))
#   status.set(
#     f'Directory: {clicked_path.name}, {num_children} children'
#   )
#
#
# tv.bind('<<TreeviewOpen>>', show_directory_stats)
# tv.bind('<<TreeviewClose>>', lambda _: status.set(''))
#
# root.mainloop()
#

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Treeview Demo")
        self.minsize(640, 480)
        self.center_window(900, 600)

        self.style = ttk.Style(self)
        self.root_path = Path(".")
        self.status_var = tk.StringVar()
        self.theme_var = tk.StringVar(value=self.style.theme_use())
        self.treeview: ttk.Treeview = None

        self._build_menu()
        self._build_body()
        self._build_statusbar()
        self._populate_treeview()
        self._bind_events()

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

        self._build_treeview(container)

    def _build_treeview(self, parent):
        self.treeview = ttk.Treeview( parent,
            columns=("size", "modified"),
            selectmode="browse",
        )
        self.treeview.heading("#0",
            text="Name",
            command=lambda: self._sort_treeview("#0"),
        )
        self.treeview.heading("size",
            text="Size",
            anchor="center",
            command=lambda: self._sort_treeview("size"),
        )
        self.treeview.heading("modified",
            text="Modified",
            anchor="e",
            command=lambda: self._sort_treeview("modified"),
        )
        self.treeview.column("#0", stretch=True)
        self.treeview.column("size", width=200)

        self.treeview.pack(fill=tk.BOTH, expand=True)

    def _build_statusbar(self):
        statusbar = ttk.Label(self, textvariable=self.status_var)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _add_menu_button(self, parent, text, menu):
        button = ttk.Menubutton(parent, text=text, direction="below")
        button.pack(side=tk.LEFT, padx=(0, 4))
        button["menu"] = menu

    def _populate_treeview(self):
        for path in self.root_path.glob("**/*"):
            meta = path.stat()
            parent = str(path.parent)
            if parent == ".":
                parent = ""

            self.treeview.insert(
                parent,
                tk.END,
                iid=str(path),
                text=path.name,
                values=(meta.st_size, meta.st_mtime),
            )

    def _bind_events(self):
        self.treeview.bind("<<TreeviewOpen>>", self._show_directory_stats)
        self.treeview.bind("<<TreeviewClose>>", self._clear_status)
        self.treeview.bind("<<TreeviewSelect>>", self._show_selected_item)

    def _sort_treeview(self, column, parent="", reverse=False):
        sort_index = []
        for item_id in self.treeview.get_children(parent):
            sort_value = (
                self.treeview.set(item_id, column)
                if column != "#0"
                else item_id
            )
            sort_index.append((sort_value, item_id))

        sort_index.sort(reverse=reverse)

        for index, (_, item_id) in enumerate(sort_index):
            self.treeview.move(item_id, parent, index)
            self._sort_treeview(column, parent=item_id, reverse=reverse)

        if parent == "":
            self.treeview.heading(
                column,
                command=lambda: self._sort_treeview(
                    column,
                    reverse=not reverse,
                ),
            )

    def _show_directory_stats(self, *_):
        clicked_path = Path(self.treeview.focus())
        if not clicked_path.exists() or not clicked_path.is_dir():
            self.status_var.set("")
            return

        num_children = len(list(clicked_path.iterdir()))
        self.status_var.set(
            f"Directory: {clicked_path.name}, {num_children} children"
        )

    def _clear_status(self, *_):
        self.status_var.set("")

    def _show_selected_item(self, *_):
        item_id = self.treeview.focus()
        if not item_id:
            self.status_var.set("")
            return

        selected_path = Path(item_id)
        if selected_path.is_dir():
            num_children = len(list(selected_path.iterdir()))
            self.status_var.set(
                f"Directory: {selected_path.name}, {num_children} children"
            )
            return

        self.status_var.set(f"File: {selected_path.name}")

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
