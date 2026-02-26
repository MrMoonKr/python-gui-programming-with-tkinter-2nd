import tkinter as tk
from tkinter import ttk


class PAKExplorer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RPF Explorer (Tkinter Mock)")
        self.geometry("1100x700")
        self.minsize(900, 500)

        # ---- status text variable
        self.status_var = tk.StringVar(value="Ready.")

        # ---- layout: menu, toolbar, main, status
        self._build_menu()
        self._build_toolbar()
        self._build_main_panes()
        self._build_statusbar()

        # demo data
        self._populate_demo_tree()
        self._populate_demo_list(root_name="(no selection)")

        # bindings
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.listview.bind("<Double-1>", self._on_list_double_click)
        self.bind("<F5>", lambda e: self._set_status("Refresh (F5)"))

    # -----------------------------
    # UI builders
    # -----------------------------
    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open...", command=lambda: self._set_status("File > Open..."))
        file_menu.add_command(label="Close", command=lambda: self._set_status("File > Close"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Copy", command=lambda: self._set_status("Edit > Copy"))
        edit_menu.add_command(label="Paste", command=lambda: self._set_status("Edit > Paste"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=lambda: self._set_status("Edit > Find..."))

        view_menu = tk.Menu(menubar, tearoff=False)
        self.show_toolbar_var = tk.BooleanVar(value=True)
        self.show_status_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Toolbar", variable=self.show_toolbar_var, command=self._toggle_toolbar)
        view_menu.add_checkbutton(label="Status Bar", variable=self.show_status_var, command=self._toggle_statusbar)
        view_menu.add_separator()
        view_menu.add_command(label="Refresh (F5)", command=lambda: self._set_status("View > Refresh"))

        tools_menu = tk.Menu(menubar, tearoff=False)
        tools_menu.add_command(label="Scan", command=lambda: self._set_status("Tools > Scan"))
        tools_menu.add_command(label="Export selected", command=lambda: self._set_status("Tools > Export selected"))

        options_menu = tk.Menu(menubar, tearoff=False)
        options_menu.add_command(label="Settings...", command=lambda: self._set_status("Options > Settings..."))
        self.edit_mode_var = tk.BooleanVar(value=False)
        options_menu.add_checkbutton(
            label="Edit mode",
            variable=self.edit_mode_var,
            command=lambda: self._set_status(f"Options > Edit mode = {self.edit_mode_var.get()}")
        )

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        menubar.add_cascade(label="View", menu=view_menu)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        menubar.add_cascade(label="Options", menu=options_menu)

        self.config(menu=menubar)

    def _build_toolbar(self):
        self.toolbar = ttk.Frame(self, padding=(6, 4))
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # left tool buttons
        ttk.Button(self.toolbar, text="Open", command=lambda: self._set_status("Toolbar: Open")).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(self.toolbar, text="Back", command=lambda: self._set_status("Toolbar: Back")).pack(side=tk.LEFT, padx=4)
        ttk.Button(self.toolbar, text="Up", command=lambda: self._set_status("Toolbar: Up")).pack(side=tk.LEFT, padx=4)
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Button(self.toolbar, text="Refresh", command=lambda: self._set_status("Toolbar: Refresh")).pack(side=tk.LEFT, padx=4)

        # edit mode checkbox (like the screenshot top-right)
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Checkbutton(
            self.toolbar,
            text="Edit mode",
            variable=self.edit_mode_var,
            command=lambda: self._set_status(f"Toolbar: Edit mode = {self.edit_mode_var.get()}")
        ).pack(side=tk.LEFT, padx=4)

        # spacer
        ttk.Label(self.toolbar, text=" ").pack(side=tk.LEFT, expand=True)

        # right-side search box
        ttk.Label(self.toolbar, text="Search:").pack(side=tk.LEFT, padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.toolbar, textvariable=self.search_var, width=28)
        self.search_entry.pack(side=tk.LEFT)
        ttk.Button(self.toolbar, text="Go", command=self._on_search).pack(side=tk.LEFT, padx=6)

    def _build_main_panes(self):
        # main container
        self.main = ttk.Frame(self)
        self.main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # horizontal paned window: left tree / right list
        self.paned = ttk.Panedwindow(self.main, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # left: tree frame + scrollbar
        self.left_frame = ttk.Frame(self.paned, padding=4)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(self.left_frame, show="tree")
        self.tree_scroll = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scroll.grid(row=0, column=1, sticky="ns")

        # right: list frame (Treeview with columns) + scrollbars
        self.right_frame = ttk.Frame(self.paned, padding=4)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        columns = ("name", "type", "size", "attributes")
        self.listview = ttk.Treeview(
            self.right_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.listview.heading("name", text="Name")
        self.listview.heading("type", text="Type")
        self.listview.heading("size", text="Size")
        self.listview.heading("attributes", text="Attributes")

        # column widths (feel free to tweak)
        self.listview.column("name", width=420, anchor="w")
        self.listview.column("type", width=140, anchor="w")
        self.listview.column("size", width=90, anchor="e")
        self.listview.column("attributes", width=160, anchor="w")

        self.list_scroll_y = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.listview.yview)
        self.list_scroll_x = ttk.Scrollbar(self.right_frame, orient=tk.HORIZONTAL, command=self.listview.xview)
        self.listview.configure(yscrollcommand=self.list_scroll_y.set, xscrollcommand=self.list_scroll_x.set)

        self.listview.grid(row=0, column=0, sticky="nsew")
        self.list_scroll_y.grid(row=0, column=1, sticky="ns")
        self.list_scroll_x.grid(row=1, column=0, sticky="ew")

        # add panes with initial relative sizes
        self.paned.add(self.left_frame, weight=1)   # left narrower
        self.paned.add(self.right_frame, weight=3)  # right wider

    def _build_statusbar(self):
        self.statusbar = ttk.Frame(self, padding=(6, 3))
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(self.statusbar, textvariable=self.status_var, anchor="w")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # optional right status items (like a small indicator area)
        self.right_status = ttk.Label(self.statusbar, text="OK", width=8, anchor="e")
        self.right_status.pack(side=tk.RIGHT)

    # -----------------------------
    # Demo population
    # -----------------------------
    def _populate_demo_tree(self):
        self.tree.delete(*self.tree.get_children())

        root = self.tree.insert("", "end", text="update", open=True)
        x64 = self.tree.insert(root, "end", text="x64", open=True)
        dlcpacks = self.tree.insert(x64, "end", text="dlcpacks", open=True)
        mpjan = self.tree.insert(dlcpacks, "end", text="mpjanuary2016", open=True)
        self.tree.insert(mpjan, "end", text="dlc.rpf", open=True)
        self.tree.insert(mpjan, "end", text="dlc2.rpf", open=False)

        common = self.tree.insert("", "end", text="common.rpf", open=False)
        self.tree.insert(common, "end", text="data", open=False)
        self.tree.insert(common, "end", text="textures", open=False)

    def _populate_demo_list(self, root_name: str):
        self.listview.delete(*self.listview.get_children())

        # header-ish row simulation: not needed, but good for status
        self._set_status(f"Listing: {root_name}")

        demo_rows = [
            ("vehicles.meta", "XML", "12 KB", "R"),
            ("handling.meta", "XML", "8 KB", "R"),
            ("carcols.meta", "XML", "21 KB", "R"),
            ("carvariations.meta", "XML", "15 KB", "R"),
            ("stream/", "Folder", "", ""),
        ]

        for name, typ, size, attr in demo_rows:
            self.listview.insert("", "end", values=(name, typ, size, attr))

    # -----------------------------
    # Callbacks
    # -----------------------------
    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        node = sel[0]
        path = self._tree_item_path(node)
        self._populate_demo_list(root_name=path)

    def _on_list_double_click(self, _event):
        sel = self.listview.selection()
        if not sel:
            return
        values = self.listview.item(sel[0], "values")
        self._set_status(f"Open item: {values[0]}")

    def _on_search(self):
        q = self.search_var.get().strip()
        if not q:
            self._set_status("Search: (empty)")
            return
        self._set_status(f"Search: {q}")

    def _toggle_toolbar(self):
        if self.show_toolbar_var.get():
            self.toolbar.pack(side=tk.TOP, fill=tk.X)
            self._set_status("View: Toolbar shown")
        else:
            self.toolbar.pack_forget()
            self._set_status("View: Toolbar hidden")

    def _toggle_statusbar(self):
        if self.show_status_var.get():
            self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
            self._set_status("View: Status bar shown")
        else:
            self.statusbar.pack_forget()
            # statusbar hidden, so no need to set status

    # -----------------------------
    # Helpers
    # -----------------------------
    def _tree_item_path(self, item_id: str) -> str:
        # Build a visual "path" from tree node up to root
        parts = []
        cur = item_id
        while cur:
            parts.append(self.tree.item(cur, "text"))
            cur = self.tree.parent(cur)
            if cur == "":
                break
        return "\\".join(reversed(parts))


if __name__ == "__main__":
    app = PAKExplorer()
    app.mainloop()
