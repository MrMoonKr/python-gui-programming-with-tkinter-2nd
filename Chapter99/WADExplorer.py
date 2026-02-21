import os
import struct
import threading
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ---------------------------
# WAD format (from wadf.h / wadlib.c)
# ---------------------------
# wadf_header: 8 * uint32
# wadf_index_header: 4 * uint32
# wadf_index_record:
#   uint32 id
#   uint32 data_offset
#   uint32 data_size
#   uint32 name_offset
#   uint64 modified_time
#   uint32 type
#   uint32 null1
#
# Record name: read 256 bytes at name_offset (wadlib.c: WadRecordResolveName)
# ---------------------------

WADF_HEADER_STRUCT = struct.Struct("<8I")          # 32 bytes
WADF_INDEX_HEADER_STRUCT = struct.Struct("<4I")    # 16 bytes
WADF_INDEX_RECORD_STRUCT = struct.Struct("<4IQ2I") # 32 bytes

MAGIC_ACCEPT = {b"WADF", b"FDAW"}  # be tolerant

NAME_FIELD_SIZE = 256


def _safe_decode_cstr_256(b: bytes) -> str:
    # Trim at first NUL; decode as latin-1/utf-8 tolerant
    raw = b.split(b"\x00", 1)[0]
    if not raw:
        return ""
    try:
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return raw.decode("latin-1", errors="replace")


def _format_unix_like_time(sec: int) -> str:
    # defiance-tools stores a 64-bit modified_time; exact epoch is not documented here.
    # We'll display as integer + best-effort UTC datetime if it looks like Unix epoch.
    # If it doesn't, you still see the raw number.
    if sec <= 0:
        return "0"
    try:
        # heuristic: if within [2000..2100] unix epoch
        dt = datetime.datetime.utcfromtimestamp(sec)
        if 2000 <= dt.year <= 2100:
            return f"{sec} ({dt.isoformat()}Z)"
    except Exception:
        pass
    return str(sec)


class WadRecord:
    __slots__ = ("wad_path", "id", "type", "name_offset", "data_offset", "data_size", "modified_time", "name")

    def __init__(self, wad_path: str, rid: int, rtype: int, name_offset: int,
                 data_offset: int, data_size: int, modified_time: int):
        self.wad_path = wad_path
        self.id = rid
        self.type = rtype
        self.name_offset = name_offset
        self.data_offset = data_offset
        self.data_size = data_size
        self.modified_time = modified_time
        self.name = None  # lazy-loaded like WadRecordResolveName

    def ensure_name_loaded(self) -> None:
        if self.name is not None:
            return
        with open(self.wad_path, "rb") as f:
            f.seek(self.name_offset, os.SEEK_SET)
            b = f.read(NAME_FIELD_SIZE)
        self.name = _safe_decode_cstr_256(b)


class WadFile:
    def __init__(self, path: str):
        self.path = path
        self.records: list[WadRecord] = []

    def load_index(self) -> None:
        with open(self.path, "rb") as f:
            head = f.read(WADF_HEADER_STRUCT.size)
            if len(head) != WADF_HEADER_STRUCT.size:
                raise ValueError("File too small (no header)")
            magic_u32, unk1, total_records, *_ = WADF_HEADER_STRUCT.unpack(head)

            # Interpret magic both ways (u32 -> bytes)
            magic_bytes = struct.pack("<I", magic_u32)
            if magic_bytes not in MAGIC_ACCEPT:
                # Some environments might pack differently; also try big-endian view:
                magic_be = struct.pack(">I", magic_u32)
                if magic_be not in MAGIC_ACCEPT:
                    raise ValueError(f"Bad magic: {magic_bytes!r} / {magic_be!r}")

            total_read = 0

            # wadlib.c reads index headers until total_records_read == total_records
            while total_read < total_records:
                ih_raw = f.read(WADF_INDEX_HEADER_STRUCT.size)
                if len(ih_raw) != WADF_INDEX_HEADER_STRUCT.size:
                    raise ValueError("Unexpected EOF in index header")
                num_records, next_header_offset, ih_unk1, ih_unk2 = WADF_INDEX_HEADER_STRUCT.unpack(ih_raw)

                for _ in range(num_records):
                    ir_raw = f.read(WADF_INDEX_RECORD_STRUCT.size)
                    if len(ir_raw) != WADF_INDEX_RECORD_STRUCT.size:
                        raise ValueError("Unexpected EOF in index record")
                    rid, data_offset, data_size, name_offset, modified_time, rtype, null1 = WADF_INDEX_RECORD_STRUCT.unpack(ir_raw)

                    self.records.append(
                        WadRecord(
                            wad_path=self.path,
                            rid=rid,
                            rtype=rtype,
                            name_offset=name_offset,
                            data_offset=data_offset,
                            data_size=data_size,
                            modified_time=modified_time,
                        )
                    )
                    total_read += 1

                if next_header_offset != 0:
                    f.seek(next_header_offset, os.SEEK_SET)


class WadBrowserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WAD Browser (Tkinter) - defiance-tools wadlib.h reference")
        self.geometry("1200x750")

        self.wad_files: list[WadFile] = []
        self.current_wad: WadFile | None = None
        self.filtered_records: list[WadRecord] = []

        self._build_ui()

    def _build_ui(self):
        # Top toolbar
        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)

        btn_open_dir = ttk.Button(top, text="Open WAD Folder...", command=self.open_folder)
        btn_open_dir.pack(side=tk.LEFT)

        btn_open_wad = ttk.Button(top, text="Open WAD File...", command=self.open_wad_file)
        btn_open_wad.pack(side=tk.LEFT, padx=(6, 0))

        ttk.Label(top, text="  Filter: ").pack(side=tk.LEFT)

        self.var_filter = tk.StringVar()
        ent = ttk.Entry(top, textvariable=self.var_filter, width=60)
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ent.bind("<KeyRelease>", lambda e: self.apply_filter())

        btn_clear = ttk.Button(top, text="Clear", command=self._clear_filter)
        btn_clear.pack(side=tk.LEFT, padx=(6, 0))

        btn_extract = ttk.Button(top, text="Extract Selected (Raw)...", command=self.extract_selected)
        btn_extract.pack(side=tk.LEFT, padx=(12, 0))

        # Main split
        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Left: WAD list
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        ttk.Label(left, text="WAD Files").pack(side=tk.TOP, anchor="w")

        self.tree_wads = ttk.Treeview(left, columns=("path", "records"), show="headings", height=20)
        self.tree_wads.heading("path", text="Path")
        self.tree_wads.heading("records", text="#Records")
        self.tree_wads.column("path", width=520, anchor="w")
        self.tree_wads.column("records", width=80, anchor="e")
        self.tree_wads.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        yscroll_wads = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree_wads.yview)
        self.tree_wads.configure(yscrollcommand=yscroll_wads.set)
        yscroll_wads.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_wads.bind("<<TreeviewSelect>>", self.on_select_wad)

        # Right: Records
        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        ttk.Label(right, text="Records").pack(side=tk.TOP, anchor="w")

        cols = ("id", "type", "size", "mtime", "name")
        self.tree_rec = ttk.Treeview(right, columns=cols, show="headings")
        self.tree_rec.heading("id", text="ID")
        self.tree_rec.heading("type", text="Type")
        self.tree_rec.heading("size", text="Size")
        self.tree_rec.heading("mtime", text="ModifiedTime")
        self.tree_rec.heading("name", text="Name")

        self.tree_rec.column("id", width=120, anchor="e")
        self.tree_rec.column("type", width=120, anchor="e")
        self.tree_rec.column("size", width=120, anchor="e")
        self.tree_rec.column("mtime", width=220, anchor="w")
        self.tree_rec.column("name", width=420, anchor="w")

        self.tree_rec.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        yscroll_rec = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.tree_rec.yview)
        self.tree_rec.configure(yscrollcommand=yscroll_rec.set)
        yscroll_rec.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_rec.bind("<Double-1>", lambda e: self._double_click_record())

        # Status bar
        self.var_status = tk.StringVar(value="Ready.")
        status = ttk.Label(self, textvariable=self.var_status, relief=tk.SUNKEN, anchor="w")
        status.pack(side=tk.BOTTOM, fill=tk.X)

    def _set_status(self, s: str):
        self.var_status.set(s)
        self.update_idletasks()

    def _clear_filter(self):
        self.var_filter.set("")
        self.apply_filter()

    def open_wad_file(self):
        wad_path = filedialog.askopenfilename(
            title="Select a .wad file",
            filetypes=[("WAD files", "*.wad"), ("All files", "*.*")]
        )
        if not wad_path:
            return

        self._set_status(f"Loading WAD file: {wad_path}")
        self._clear_all()
        self._load_wad_paths([wad_path])

    def open_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing .wad files")
        if not folder:
            return

        self._set_status(f"Scanning folder: {folder}")
        self._clear_all()
        try:
            wad_paths = sorted(
                os.path.join(folder, fn) for fn in os.listdir(folder)
                if fn.lower().endswith(".wad") and os.path.isfile(os.path.join(folder, fn))
            )
            if not wad_paths:
                messagebox.showinfo("WAD Browser", "No .wad files found in that folder.")
                self._set_status("No .wad files found.")
                return
            self._load_wad_paths(wad_paths)
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to load WADs:\n{ex}")
            self._set_status("Load failed.")

    def _load_wad_paths(self, wad_paths: list[str]):
        def worker():
            try:
                wad_files: list[WadFile] = []
                for i, p in enumerate(wad_paths, 1):
                    wf = WadFile(p)
                    wf.load_index()
                    wad_files.append(wf)
                    self.after(0, lambda i=i, n=len(wad_paths), p=p: self._set_status(f"Loaded {i}/{n}: {os.path.basename(p)}"))

                self.after(0, lambda: self._apply_loaded_wads(wad_files))
            except Exception as ex:
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to load WADs:\n{ex}"))
                self.after(0, lambda: self._set_status("Load failed."))

        threading.Thread(target=worker, daemon=True).start()

    def _apply_loaded_wads(self, wad_files: list[WadFile]):
        self.wad_files = wad_files
        for wf in wad_files:
            self.tree_wads.insert("", "end", values=(wf.path, len(wf.records)))
        self._set_status(f"Loaded {len(wad_files)} WAD file(s). Select one to browse records.")

    def _clear_all(self):
        self.wad_files = []
        self.current_wad = None
        self.filtered_records = []
        for t in (self.tree_wads, self.tree_rec):
            for item in t.get_children():
                t.delete(item)

    def on_select_wad(self, _evt=None):
        sel = self.tree_wads.selection()
        if not sel:
            return
        idx = self.tree_wads.index(sel[0])
        if idx < 0 or idx >= len(self.wad_files):
            return
        self.current_wad = self.wad_files[idx]
        self.apply_filter()

    def _parse_filter(self, s: str):
        s = (s or "").strip()
        if not s:
            return None

        # Support:
        # - "id:1234" or "id:0x1234"
        # - "type:0x..." / "type:..."
        # - plain text => substring match on name (lazy)
        terms = []
        for part in s.split():
            if ":" in part:
                k, v = part.split(":", 1)
                terms.append((k.lower(), v))
            else:
                terms.append(("name", part))
        return terms

    def apply_filter(self):
        self.tree_rec.delete(*self.tree_rec.get_children())

        if not self.current_wad:
            self._set_status("No WAD selected.")
            return

        terms = self._parse_filter(self.var_filter.get())
        recs = self.current_wad.records

        if not terms:
            self.filtered_records = recs
        else:
            out = []
            for r in recs:
                ok = True
                for k, v in terms:
                    if k == "id":
                        target = int(v, 16) if v.lower().startswith("0x") else int(v, 10)
                        if r.id != target:
                            ok = False
                            break
                    elif k == "type":
                        target = int(v, 16) if v.lower().startswith("0x") else int(v, 10)
                        if r.type != target:
                            ok = False
                            break
                    elif k == "name":
                        # lazy load only if needed
                        r.ensure_name_loaded()
                        if v.lower() not in (r.name or "").lower():
                            ok = False
                            break
                    else:
                        # unknown key => treat as name token
                        r.ensure_name_loaded()
                        if v.lower() not in (r.name or "").lower():
                            ok = False
                            break
                if ok:
                    out.append(r)
            self.filtered_records = out

        # Populate list (don’t force-name-load unless already loaded by filter)
        for r in self.filtered_records[:200000]:  # guard against insane UI spam
            r.ensure_name_loaded()
            name = r.name or ""
            self.tree_rec.insert(
                "", "end",
                values=(
                    f"0x{r.id:08X}",
                    f"0x{r.type:08X}",
                    r.data_size,
                    _format_unix_like_time(int(r.modified_time)),
                    name
                )
            )

        self._set_status(
            f"WAD: {os.path.basename(self.current_wad.path)} | records: {len(self.current_wad.records)} | shown: {len(self.filtered_records)}"
        )

    def _get_selected_record(self) -> WadRecord | None:
        if not self.current_wad:
            return None
        sel = self.tree_rec.selection()
        if not sel:
            return None
        idx = self.tree_rec.index(sel[0])
        if idx < 0 or idx >= len(self.filtered_records):
            return None
        return self.filtered_records[idx]

    def _double_click_record(self):
        r = self._get_selected_record()
        if not r:
            return
        # load name on demand and refresh that row
        r.ensure_name_loaded()
        item = self.tree_rec.selection()[0]
        vals = list(self.tree_rec.item(item, "values"))
        vals[4] = r.name or ""
        self.tree_rec.item(item, values=vals)

    def extract_selected(self):
        r = self._get_selected_record()
        if not r:
            messagebox.showinfo("Extract", "Select a record first.")
            return

        out_dir = filedialog.askdirectory(title="Select output folder")
        if not out_dir:
            return

        # Determine output filename
        r.ensure_name_loaded()
        base = r.name.strip() if r.name else f"id_{r.id:08X}"
        # sanitize
        base = "".join(c if c not in r'<>:"/\|?*' else "_" for c in base)
        out_path = os.path.join(out_dir, f"{base}.bin")

        try:
            with open(r.wad_path, "rb") as f:
                f.seek(r.data_offset, os.SEEK_SET)
                blob = f.read(r.data_size)

            with open(out_path, "wb") as o:
                o.write(blob)

            self._set_status(f"Extracted: {out_path}")
            messagebox.showinfo("Extract", f"Done:\n{out_path}")
        except Exception as ex:
            messagebox.showerror("Extract", f"Failed:\n{ex}")


if __name__ == "__main__":
    app = WadBrowserApp()
    app.mainloop()
