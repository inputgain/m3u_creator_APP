import ctypes
import random
import re
import string
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    raise SystemExit(
        "Falta la dependencia 'tkinterdnd2'. Instala con: pip install -r requirements.txt"
    )


def assets_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).resolve().parent / "assets"


def natural_sort_key(value: str):
    parts = re.split(r"(\d+)", value.lower())
    key = []
    for part in parts:
        key.append(int(part) if part.isdigit() else part)
    return key


def parse_drop_files(data: str) -> list[Path]:
    paths = []
    token = ""
    in_brace = False
    for ch in data:
        if ch == "{":
            in_brace = True
            token = ""
            continue
        if ch == "}":
            in_brace = False
            if token:
                paths.append(Path(token))
            token = ""
            continue
        if ch == " " and not in_brace:
            if token:
                paths.append(Path(token))
                token = ""
            continue
        token += ch
    if token:
        paths.append(Path(token))
    return paths


def sort_natural_by_relative_path(paths: list[Path], base: Path) -> list[Path]:
    return sorted(paths, key=lambda p: natural_sort_key(p.relative_to(base).as_posix()))


def collect_mp3_from_inputs(inputs: list[Path]) -> list[Path]:
    collected: list[Path] = []
    for item in inputs:
        if not item.exists():
            continue
        if item.is_file() and item.suffix.lower() == ".mp3":
            collected.append(item.resolve())
            continue
        if item.is_dir():
            found = [p.resolve() for p in item.rglob("*.mp3") if p.is_file()]
            collected.extend(sort_natural_by_relative_path(found, item.resolve()))
    return collected


def to_relative_m3u_lines(model_paths: list[Path], m3u_dir: Path) -> list[str]:
    lines = []
    for path in model_paths:
        p = Path(path).resolve()
        try:
            rel = p.relative_to(m3u_dir.resolve())
        except ValueError:
            rel = Path(p.relative_to(Path(p.anchor)))
        lines.append(rel.as_posix())
    return lines


def write_m3u(lines: list[str], target_file: Path, confirm_overwrite: bool = True):
    if target_file.exists() and confirm_overwrite:
        overwrite = messagebox.askyesno(
            "Sobrescribir",
            f"{target_file.name} ya existe. Quieres reemplazarlo?",
        )
        if not overwrite:
            return False
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def find_usb_roots() -> list[Path]:
    removable = []
    for letter in string.ascii_uppercase:
        root = Path(f"{letter}:/")
        if not root.exists():
            continue
        drive_type = ctypes.windll.kernel32.GetDriveTypeW(str(root))
        if drive_type == 2:
            removable.append(root)
    return removable


class M3UCreatorApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("m3u Creator App")
        self.geometry("1040x680")
        png = assets_dir() / "app_icon.png"
        if png.exists():
            self._icon_img = tk.PhotoImage(file=str(png))
            self.iconphoto(True, self._icon_img)

        self.playlist_model: list[Path] = []
        self.original_order: list[Path] = []
        self.shuffle_mode = tk.BooleanVar(value=False)
        self.save_mode = tk.StringVar(value="manual")
        self.m3u_name = tk.StringVar(value="lista")
        self.usb_var = tk.StringVar(value="")
        self.count_text = tk.StringVar(value="Canciones: 0")

        self.drag_start_y = 0
        self.drag_candidate_index = None
        self.drag_source_indices: list[int] = []
        self.drag_target_index = None
        self.drag_active = False

        self._build_ui()

    def _build_ui(self):
        self.configure(bg="#eaf3ff")
        main = ttk.Frame(self, padding=12, style="Main.TFrame")
        main.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TFrame", background="#eaf3ff")
        style.configure("Card.TLabelframe", background="#f7fbff")
        style.configure("Card.TLabelframe.Label", background="#f7fbff", foreground="#1d3557")
        style.configure("Pista.TLabel", foreground="#355070", background="#f7fbff")
        style.configure("Total.TLabel", foreground="#1d3557", background="#eaf3ff", font=("Segoe UI", 10, "bold"))
        style.configure("Guardar.TButton", font=("Segoe UI", 11, "bold"), padding=(16, 8))

        style.configure(
            "Treeview",
            rowheight=24,
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="#102a43",
        )
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        # Reducimos el azul fuerte de seleccion, usando tono suave.
        style.map("Treeview", background=[("selected", "#dfefff")], foreground=[("selected", "#102a43")])

        actions = ttk.Frame(main, style="Main.TFrame")
        actions.pack(fill="x", pady=(0, 6))

        ttk.Button(actions, text="✖ Eliminar", command=self.remove_selected).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="▲ Subir", command=self.move_up).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="▼ Bajar", command=self.move_down).pack(side="left", padx=(0, 12))

        ttk.Checkbutton(
            actions,
            text="🔀 Orden aleatorio",
            variable=self.shuffle_mode,
            command=self.toggle_shuffle,
        ).pack(side="left")

        ttk.Label(actions, textvariable=self.count_text, style="Total.TLabel").pack(side="right")

        list_frame = ttk.LabelFrame(main, text="Vista preliminar (editable)", padding=8, style="Card.TLabelframe")
        list_frame.pack(fill="both", expand=True)

        tree_wrap = ttk.Frame(list_frame, style="Card.TLabelframe")
        tree_wrap.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_wrap,
            columns=("check", "n", "ruta"),
            show="headings",
            selectmode="extended",
        )
        self.tree.heading("check", text="Sel")
        self.tree.heading("n", text="#")
        self.tree.heading("ruta", text="Ruta")
        self.tree.column("check", width=52, anchor="center", stretch=False)
        self.tree.column("n", width=44, anchor="e", stretch=False)
        self.tree.column("ruta", width=760, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.drop_target_register(DND_FILES)
        self.tree.dnd_bind("<<Drop>>", self._on_drop)
        self.tree.dnd_bind("<<DropEnter>>", self._on_drop_enter)
        self.tree.dnd_bind("<<DropLeave>>", self._on_drop_leave)

        self.empty_label = ttk.Label(
            tree_wrap,
            text="Arrastra aqui archivos o carpetas con MP3",
            style="Pista.TLabel",
            justify="center",
            font=("Segoe UI", 12, "bold"),
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        self.insert_line = tk.Frame(self.tree, bg="#1b9aaa", height=2)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<B1-Motion>", self._on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_release)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Escape>", self._clear_selection_event)

        save_cfg = ttk.LabelFrame(main, text="Salida", padding=8, style="Card.TLabelframe")
        save_cfg.pack(fill="x", pady=(10, 0))

        mode_row = ttk.Frame(save_cfg)
        mode_row.pack(fill="x", pady=(0, 6))
        ttk.Radiobutton(
            mode_row,
            text="Ubicacion manual",
            variable=self.save_mode,
            value="manual",
            command=self._refresh_usb_state,
        ).pack(side="left")
        ttk.Radiobutton(
            mode_row,
            text="Raiz USB",
            variable=self.save_mode,
            value="usb",
            command=self._refresh_usb_state,
        ).pack(side="left", padx=(12, 0))

        usb_row = ttk.Frame(save_cfg)
        usb_row.pack(fill="x", pady=(0, 6))
        ttk.Label(usb_row, text="USB:").pack(side="left")
        self.usb_combo = ttk.Combobox(usb_row, textvariable=self.usb_var, state="readonly", width=18)
        self.usb_combo.pack(side="left", padx=(6, 6))
        ttk.Button(usb_row, text="Actualizar USB", command=self.refresh_usb_list).pack(side="left")

        name_row = ttk.Frame(save_cfg)
        name_row.pack(fill="x")
        ttk.Label(name_row, text="Nombre de la lista:").pack(side="left")
        ttk.Entry(name_row, textvariable=self.m3u_name, width=30).pack(side="left", padx=(6, 8))
        ttk.Label(name_row, text="(.m3u se añade automaticamente)").pack(side="left", padx=(0, 12))
        ttk.Button(name_row, text="💾 Generar M3U", style="Guardar.TButton", command=self.generate_m3u).pack(side="right")

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="🗑 Eliminar", command=self.remove_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="⬆ Subir", command=self.move_up)
        self.context_menu.add_command(label="⬇ Bajar", command=self.move_down)
        self.context_menu.add_command(label="⏫ Mover al inicio", command=self.move_selected_to_top)
        self.context_menu.add_command(label="⏬ Mover al final", command=self.move_selected_to_bottom)

        self.refresh_usb_list()
        self._refresh_usb_state()

    def _display_path(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(path.anchor)).replace("\\", "/")
        except Exception:
            return str(path).replace("\\", "/")

    def _set_empty_state(self, visible: bool):
        if visible:
            self.empty_label.lift()
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.empty_label.place_forget()

    def _selected_indices(self) -> list[int]:
        items = self.tree.selection()
        return sorted(int(i) for i in items)

    def _refresh_tree(self):
        selected_before = set(self._selected_indices())
        self.tree.delete(*self.tree.get_children())
        for i, path in enumerate(self.playlist_model):
            check = "✓" if i in selected_before else ""
            self.tree.insert("", "end", iid=str(i), values=(check, f"{i + 1:03d}", self._display_path(path)))

        for idx in selected_before:
            if idx < len(self.playlist_model):
                self.tree.selection_add(str(idx))

        self.count_text.set(f"Canciones: {len(self.playlist_model)}")
        self._hide_insert_preview()
        self._set_empty_state(visible=(len(self.playlist_model) == 0))
        self._update_selection_checks()

    def _update_selection_checks(self):
        selected = set(self._selected_indices())
        for iid in self.tree.get_children():
            idx = int(iid)
            values = list(self.tree.item(iid, "values"))
            values[0] = "✓" if idx in selected else ""
            self.tree.item(iid, values=values)

    def _on_tree_select(self, _event):
        self._update_selection_checks()

    def _set_drop_idle(self):
        self.tree.configure(style="Treeview")

    def _on_drop_enter(self, _event):
        self.tree.configure(style="Drop.Treeview")
        style = ttk.Style()
        style.configure("Drop.Treeview", background="#eef8ff", fieldbackground="#eef8ff")

    def _on_drop_leave(self, _event):
        self._set_drop_idle()

    def _on_drop(self, event):
        self._set_drop_idle()
        dropped = parse_drop_files(event.data)
        new_files = collect_mp3_from_inputs(dropped)
        if not new_files:
            messagebox.showinfo("Sin MP3", "No se encontraron archivos .mp3 en los elementos arrastrados.")
            return
        self.original_order.extend(new_files)
        if self.shuffle_mode.get():
            self.playlist_model.extend(new_files)
            random.shuffle(self.playlist_model)
        else:
            self.playlist_model.extend(new_files)
        self._refresh_tree()

    def remove_selected(self):
        selected = self._selected_indices()
        if not selected:
            return
        for idx in reversed(selected):
            removed = self.playlist_model.pop(idx)
            if removed in self.original_order:
                self.original_order.remove(removed)
        self._refresh_tree()

    def move_selected_to_top(self):
        selected = self._selected_indices()
        if not selected:
            return
        selected_set = set(selected)
        moved = [self.playlist_model[i] for i in selected]
        others = [item for i, item in enumerate(self.playlist_model) if i not in selected_set]
        self.playlist_model = moved + others
        self._refresh_tree()
        self.tree.selection_set([str(i) for i in range(len(moved))])
        self._update_selection_checks()

    def move_selected_to_bottom(self):
        selected = self._selected_indices()
        if not selected:
            return
        selected_set = set(selected)
        moved = [self.playlist_model[i] for i in selected]
        others = [item for i, item in enumerate(self.playlist_model) if i not in selected_set]
        start = len(others)
        self.playlist_model = others + moved
        self._refresh_tree()
        self.tree.selection_set([str(i) for i in range(start, start + len(moved))])
        self._update_selection_checks()

    def move_up(self):
        selected = self._selected_indices()
        if not selected or selected[0] == 0:
            return
        for idx in selected:
            self.playlist_model[idx - 1], self.playlist_model[idx] = self.playlist_model[idx], self.playlist_model[idx - 1]
        self._refresh_tree()
        self.tree.selection_set([str(i - 1) for i in selected])
        self._update_selection_checks()

    def move_down(self):
        selected = self._selected_indices()
        if not selected or selected[-1] == len(self.playlist_model) - 1:
            return
        for idx in reversed(selected):
            self.playlist_model[idx + 1], self.playlist_model[idx] = self.playlist_model[idx], self.playlist_model[idx + 1]
        self._refresh_tree()
        self.tree.selection_set([str(i + 1) for i in selected])
        self._update_selection_checks()

    def _on_drag_start(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            self.tree.selection_remove(self.tree.selection())
            self._update_selection_checks()
            return
        clicked_idx = int(row_id)
        selected = self._selected_indices()

        # Si pulsamos una fila ya seleccionada sin Ctrl/Shift, preservamos la multiseleccion
        # para poder arrastrar el bloque completo.
        if clicked_idx in selected and not (event.state & 0x0005):
            self.drag_start_y = event.y
            self.drag_candidate_index = clicked_idx
            self.drag_target_index = clicked_idx
            self.drag_active = False
            self.drag_source_indices = []
            return "break"

        self.drag_start_y = event.y
        self.drag_candidate_index = clicked_idx
        self.drag_target_index = self.drag_candidate_index
        self.drag_active = False
        self.drag_source_indices = []

    def _on_drag_motion(self, event):
        if self.drag_candidate_index is None:
            return

        if not self.drag_active:
            if abs(event.y - self.drag_start_y) < 5:
                return
            if event.state & 0x0005:
                return

            selected = self._selected_indices()
            if self.drag_candidate_index in selected and selected:
                self.drag_source_indices = selected
            else:
                self.drag_source_indices = [self.drag_candidate_index]
                self.tree.selection_set(str(self.drag_candidate_index))

            self.drag_active = True

        target = self._get_insert_index(event.y)
        self.drag_target_index = target
        self._show_insert_preview(target)

    def _on_drag_release(self, _event):
        if not self.drag_active or self.drag_target_index is None or not self.drag_source_indices:
            self._reset_drag_state()
            return

        final_index = self._move_selected_block(self.drag_source_indices, self.drag_target_index)
        moved_len = len(self.drag_source_indices)
        self._refresh_tree()
        self.tree.selection_set([str(i) for i in range(final_index, final_index + moved_len)])
        self._update_selection_checks()
        self._reset_drag_state()

    def _reset_drag_state(self):
        self.drag_candidate_index = None
        self.drag_target_index = None
        self.drag_active = False
        self.drag_source_indices = []
        self._hide_insert_preview()

    def _get_insert_index(self, y: int) -> int:
        size = len(self.playlist_model)
        if size == 0:
            return 0

        row_id = self.tree.identify_row(y)
        if not row_id:
            return size

        row_index = int(row_id)
        bbox = self.tree.bbox(row_id)
        if not bbox:
            return size

        row_top = bbox[1]
        row_height = bbox[3]
        if y < row_top + row_height / 2:
            return row_index
        return min(row_index + 1, size)

    def _show_insert_preview(self, index: int):
        size = len(self.playlist_model)
        if size == 0:
            self._hide_insert_preview()
            return

        if index <= 0:
            row_id = "0"
            bbox = self.tree.bbox(row_id)
            if not bbox:
                self._hide_insert_preview()
                return
            line_y = bbox[1]
        elif index >= size:
            row_id = str(size - 1)
            bbox = self.tree.bbox(row_id)
            if not bbox:
                self._hide_insert_preview()
                return
            line_y = bbox[1] + bbox[3]
        else:
            row_id = str(index)
            bbox = self.tree.bbox(row_id)
            if not bbox:
                self._hide_insert_preview()
                return
            line_y = bbox[1]

        self.insert_line.place(x=0, y=max(line_y - 1, 0), relwidth=1.0)

    def _hide_insert_preview(self):
        self.insert_line.place_forget()

    def _move_selected_block(self, selected_indices: list[int], target_index: int) -> int:
        selected_set = set(selected_indices)
        moving_items = [self.playlist_model[i] for i in selected_indices]
        remaining = [item for i, item in enumerate(self.playlist_model) if i not in selected_set]

        removed_before = sum(1 for i in selected_indices if i < target_index)
        insert_at = max(0, min(target_index - removed_before, len(remaining)))

        self.playlist_model = remaining[:insert_at] + moving_items + remaining[insert_at:]
        return insert_at

    def _show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return
        selected = set(self.tree.selection())
        if row_id not in selected:
            self.tree.selection_set(row_id)
        self._update_selection_checks()
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def toggle_shuffle(self):
        if self.shuffle_mode.get():
            self.playlist_model = list(self.playlist_model)
            random.shuffle(self.playlist_model)
        else:
            current = set(self.playlist_model)
            self.playlist_model = [p for p in self.original_order if p in current]
        self._refresh_tree()

    def refresh_usb_list(self):
        roots = find_usb_roots()
        values = [str(p) for p in roots]
        self.usb_combo["values"] = values
        if values and self.usb_var.get() not in values:
            self.usb_var.set(values[0])
        if not values:
            self.usb_var.set("")

    def _refresh_usb_state(self):
        state = "normal" if self.save_mode.get() == "usb" else "disabled"
        self.usb_combo.configure(state=state)

    def _clear_selection_event(self, _event):
        self.tree.selection_remove(self.tree.selection())
        self._update_selection_checks()

    def _resolve_output_file(self) -> Path | None:
        raw_name = self.m3u_name.get().strip()
        if not raw_name:
            messagebox.showerror("Nombre invalido", "Introduce un nombre para la lista.")
            return None
        filename = raw_name if raw_name.lower().endswith(".m3u") else f"{raw_name}.m3u"

        if self.save_mode.get() == "manual":
            selected = filedialog.asksaveasfilename(
                defaultextension=".m3u",
                filetypes=[("Listas M3U", "*.m3u")],
                initialfile=filename,
            )
            return Path(selected) if selected else None

        usb = self.usb_var.get().strip()
        if not usb:
            messagebox.showerror("Sin USB", "No hay USB seleccionado. Conecta uno o usa ubicacion manual.")
            return None
        return Path(usb) / filename

    def generate_m3u(self):
        if not self.playlist_model:
            messagebox.showerror("Lista vacia", "Agrega al menos un .mp3 antes de generar.")
            return
        target = self._resolve_output_file()
        if not target:
            return

        lines = to_relative_m3u_lines(self.playlist_model, target.parent)
        if write_m3u(lines, target, confirm_overwrite=True):
            messagebox.showinfo("Listo", f"Lista creada:\n{target}")


if __name__ == "__main__":
    app = M3UCreatorApp()
    app.mainloop()
