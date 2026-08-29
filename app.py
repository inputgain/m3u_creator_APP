import ctypes
import random
import re
import shutil
import string
import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    raise SystemExit(
        "Falta la dependencia 'tkinterdnd2'. Instala con: pip install -r requirements.txt"
    )

__version__ = "1.5.2"

LANG = {
    "es": {
        "window_title": "m3u Creator App",
        "btn_new": "\U0001f195 Nuevo",
        "btn_open": "\U0001f4c2 Abrir M3U",
        "btn_del": "\u2716 Eliminar",
        "btn_up": "\u25b2 Subir",
        "btn_down": "\u25bc Bajar",
        "btn_fix": "\U0001f527 Corregir caracteres",
        "tip_new": "Crear una nueva lista vacia",
        "tip_open": "Abrir una lista M3U existente",
        "tip_del": "Eliminar las canciones seleccionadas",
        "tip_up": "Subir la seleccion en la lista",
        "tip_down": "Bajar la seleccion en la lista",
        "tip_fix": "Corregir caracteres NO ASCII en nombres de archivo y carpetas",
        "shuffle": "\U0001f500 Orden aleatorio",
        "col_sel": "Sel",
        "col_num": "#",
        "col_path": "Ruta",
        "empty_state": "Arrastra aqui los archivos o carpetas con MP3",
        "warn_suffix": "\u26a0 caracter NO ASCII",
        "frame_list": "Vista preliminar (editable)",
        "frame_save": "Salida",
        "mode_manual": "Ubicacion manual",
        "mode_usb": "Raiz USB",
        "lbl_usb": "USB:",
        "btn_refresh": "Actualizar USB",
        "tip_refresh": "Buscar dispositivos USB conectados",
        "lbl_name": "Nombre de la lista:",
        "lbl_hint": "(.m3u se anade automaticamente)",
        "btn_gen": "\U0001f4be Generar M3U",
        "tip_gen": "Guardar la lista como archivo .m3u",
        "ctx_del": "\U0001f5d1 Eliminar",
        "ctx_up": "\u2b06 Subir",
        "ctx_down": "\u2b07 Bajar",
        "ctx_top": "\u23ee Mover al inicio",
        "ctx_bottom": "\u23ed Mover al final",
        "ctx_fix": "\U0001f527 Corregir nombre",
        "dlg_title": "Corregir caracteres NO ASCII",
        "dlg_header": "\U0001f527  Corregir caracteres NO ASCII  \u2014  {count} archivo{s} encontrado{s}",
        "dlg_auto": "Aplicar correccion automatica (\u00e1\u2192a, \u00e9\u2192e, \u00f1\u2192n, ...)",
        "btn_cancel": "Cancelar",
        "tip_cancel": "Cerrar sin aplicar cambios",
        "btn_rename": "Renombrar",
        "tip_rename": "Aplicar los cambios de nombre en disco",
        "lbl_orig": "Ubicacion original:",
        "lbl_new": "Nuevo nombre:",
        "lbl_noascii": "NO ASCII: {chars}",
        "count_fmt": "Canciones: {count}",
        "file_filter_m3u": "Listas M3U",
        "file_filter_all": "Todos los archivos",
        "mb_overwrite_title": "Sobrescribir",
        "mb_overwrite_msg": "{name} ya existe. Quieres reemplazarlo?",
        "mb_missing_title": "Archivos faltantes",
        "mb_missing_msg": "Se encontraron archivos que no existen:\n\n{list}\nDesea mantenerlos en la playlist?",
        "mb_missing_more": " ... y {n} mas\n",
        "mb_write_error_title": "Error al guardar",
        "mb_write_error_msg": "No se pudo guardar la lista:\n{error}",
        "mb_empty_title": "Vacia",
        "mb_empty_msg": "El archivo M3U esta vacio o no contiene pistas validas.",
        "mb_newlist_title": "Nueva lista",
        "mb_newlist_msg": "Se borraran todas las entradas. Continuar?",
        "mb_noproblems_title": "Sin problemas",
        "mb_noproblems_msg": "No hay archivos con caracteres NO ASCII.",
        "mb_confirm_title": "Confirmar renombrado",
        "mb_confirm_msg": "Se renombraran {count} archivos/carpetas en disco.\n\nContinuar?",
        "mb_errors_title": "Errores al renombrar",
        "mb_errors_msg": "No se pudieron renombrar algunos archivos:\n\n{errors}",
        "mb_noname_title": "Nombre invalido",
        "mb_noname_msg": "Introduce un nombre para la lista.",
        "mb_nousb_title": "Sin USB",
        "mb_nousb_msg": "No hay USB seleccionado. Conecta uno o usa ubicacion manual.",
        "mb_emptylist_title": "Lista vacia",
        "mb_emptylist_msg": "Agrega al menos un .mp3 antes de generar.",
        "mb_already_exists": "Ya existe: {name}",
        "mb_folder_error": "Error carpeta {name}:\n  {error}",
        "mb_done_title": "Listo",
        "mb_done_msg": "Lista creada:\n{target}",
        "about_title": "Acerca de",
        "about_desc": "Creador de listas de reproduccion M3U",
        "about_made_by": "Hecho por inputgain",
        "about_license": "Licencia MIT",
        "btn_close": "Cerrar",
        "lang_btn": "EN",
        "tip_lang": "Cambiar idioma",
        "default_name": "lista",
    },
    "en": {
        "window_title": "m3u Creator App",
        "btn_new": "\U0001f195 New",
        "btn_open": "\U0001f4c2 Open M3U",
        "btn_del": "\u2716 Delete",
        "btn_up": "\u25b2 Move Up",
        "btn_down": "\u25bc Move Down",
        "btn_fix": "\U0001f527 Fix characters",
        "tip_new": "Create a new empty playlist",
        "tip_open": "Open an existing M3U playlist",
        "tip_del": "Delete selected songs",
        "tip_up": "Move selection up in the list",
        "tip_down": "Move selection down in the list",
        "tip_fix": "Fix non-ASCII characters in file and folder names",
        "shuffle": "\U0001f500 Shuffle order",
        "col_sel": "Sel",
        "col_num": "#",
        "col_path": "Path",
        "empty_state": "Drag and drop MP3 files or folders here",
        "warn_suffix": "\u26a0 non-ASCII character",
        "frame_list": "Preview (editable)",
        "frame_save": "Output",
        "mode_manual": "Manual location",
        "mode_usb": "USB root",
        "lbl_usb": "USB:",
        "btn_refresh": "Refresh USB",
        "tip_refresh": "Search for connected USB devices",
        "lbl_name": "Playlist name:",
        "lbl_hint": "(.m3u is added automatically)",
        "btn_gen": "\U0001f4be Generate M3U",
        "tip_gen": "Save playlist as .m3u file",
        "ctx_del": "\U0001f5d1 Delete",
        "ctx_up": "\u2b06 Move Up",
        "ctx_down": "\u2b07 Move Down",
        "ctx_top": "\u23ee Move to top",
        "ctx_bottom": "\u23ed Move to bottom",
        "ctx_fix": "\U0001f527 Fix name",
        "dlg_title": "Fix non-ASCII characters",
        "dlg_header": "\U0001f527  Fix non-ASCII characters  \u2014  {count} file{s} found",
        "dlg_auto": "Apply auto-fix (\u00e1\u2192a, \u00e9\u2192e, \u00f1\u2192n, ...)",
        "btn_cancel": "Cancel",
        "tip_cancel": "Close without applying changes",
        "btn_rename": "Rename",
        "tip_rename": "Apply name changes on disk",
        "lbl_orig": "Original location:",
        "lbl_new": "New name:",
        "lbl_noascii": "NO ASCII: {chars}",
        "count_fmt": "Songs: {count}",
        "file_filter_m3u": "M3U Playlists",
        "file_filter_all": "All files",
        "mb_overwrite_title": "Overwrite",
        "mb_overwrite_msg": "{name} already exists. Do you want to replace it?",
        "mb_missing_title": "Missing files",
        "mb_missing_msg": "The following files were not found:\n\n{list}\nKeep them in the playlist?",
        "mb_missing_more": " ... and {n} more\n",
        "mb_write_error_title": "Save error",
        "mb_write_error_msg": "Could not save the playlist:\n{error}",
        "mb_empty_title": "Empty",
        "mb_empty_msg": "The M3U file is empty or contains no valid tracks.",
        "mb_newlist_title": "New playlist",
        "mb_newlist_msg": "All entries will be deleted. Continue?",
        "mb_noproblems_title": "No issues",
        "mb_noproblems_msg": "No files with non-ASCII characters found.",
        "mb_confirm_title": "Confirm rename",
        "mb_confirm_msg": "Will rename {count} files/folders on disk.\n\nContinue?",
        "mb_errors_title": "Rename errors",
        "mb_errors_msg": "Some files could not be renamed:\n\n{errors}",
        "mb_noname_title": "Invalid name",
        "mb_noname_msg": "Enter a name for the playlist.",
        "mb_nousb_title": "No USB",
        "mb_nousb_msg": "No USB selected. Connect one or use manual location.",
        "mb_emptylist_title": "Empty playlist",
        "mb_emptylist_msg": "Add at least one .mp3 before generating.",
        "mb_already_exists": "Already exists: {name}",
        "mb_folder_error": "Folder error {name}:\n  {error}",
        "mb_done_title": "Done",
        "mb_done_msg": "Playlist created:\n{target}",
        "about_title": "About",
        "about_desc": "M3U playlist creator",
        "about_made_by": "Made by inputgain",
        "about_license": "MIT License",
        "btn_close": "Close",
        "lang_btn": "ES",
        "tip_lang": "Switch language",
        "default_name": "playlist",
    },
}


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
            found = [
                p.resolve() for p in item.rglob("*")
                if p.is_file() and p.suffix.lower() == ".mp3"
            ]
            collected.extend(sort_natural_by_relative_path(found, item.resolve()))
    return collected


def to_relative_m3u_lines(model_paths: list[Path], m3u_dir: Path) -> list[str]:
    lines = []
    base = m3u_dir.resolve()
    for path in model_paths:
        p = Path(path).resolve()
        try:
            rel = p.relative_to(base)
        except ValueError:
            lines.append(p.as_posix())
            continue
        lines.append(rel.as_posix())
    return lines


def write_m3u(lines: list[str], target_file: Path, confirm_overwrite: bool = True, lang: str = "es"):
    t = LANG[lang]
    if target_file.exists() and confirm_overwrite:
        overwrite = messagebox.askyesno(
            t["mb_overwrite_title"],
            t["mb_overwrite_msg"].format(name=target_file.name),
        )
        if not overwrite:
            return False
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as e:
        messagebox.showerror(t["mb_write_error_title"], t["mb_write_error_msg"].format(error=e))
        return False
    return True


def parse_m3u_file(m3u_path: Path) -> tuple[list[Path], list[Path]]:
    """Parse an M3U file and return (all_paths_in_file_order, missing_paths)."""
    try:
        text = m3u_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        text = m3u_path.read_text(encoding="latin-1")
    m3u_dir = m3u_path.resolve().parent
    all_paths = []
    missing = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        resolved = (m3u_dir / line).resolve()
        all_paths.append(resolved)
        if not resolved.exists():
            missing.append(resolved)
    return all_paths, missing


def find_usb_roots() -> list[Path]:
    removable = []
    if sys.platform == "win32":
        for letter in string.ascii_uppercase:
            root = Path(f"{letter}:/")
            if not root.exists():
                continue
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(str(root))
            if drive_type == 2:
                removable.append(root)
    elif sys.platform == "darwin":
        volumes = Path("/Volumes")
        if volumes.is_dir():
            for entry in volumes.iterdir():
                if entry.is_dir():
                    removable.append(entry)
    else:
        import os
        user = os.environ.get("USER", "")
        for base in [Path(f"/media/{user}"), Path(f"/run/media/{user}"), Path("/mnt")]:
            if base.is_dir():
                for entry in base.iterdir():
                    if entry.is_dir():
                        removable.append(entry)
    return removable


CHAR_MAP = {
    "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
    "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
    "ñ": "n", "Ñ": "N",
    "ü": "u", "Ü": "U",
    "¿": "", "¡": "",
}


class ToolTip:
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event=None):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("Segoe UI", 9), padx=6, pady=4)
        label.pack()

    def _hide(self, _event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


@dataclass
class _FixEntry:
    idx: int
    orig_path: Path
    orig_str: str
    entry: tk.Entry
    preview_lbl: tk.Label
    preview_var: tk.StringVar


class M3UCreatorApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.lang = tk.StringVar(value="es")
        self.lang.trace_add("write", lambda *_: self._change_language())

        t = LANG[self.lang.get()]
        self.title(t["window_title"])
        self.geometry("1040x680")
        png = assets_dir() / "app_icon.png"
        if png.exists():
            self._icon_img = tk.PhotoImage(file=str(png))
            self.iconphoto(True, self._icon_img)

        self.playlist_model: list[Path] = []
        self.original_order: list[Path] = []
        self.shuffle_mode = tk.BooleanVar(value=False)
        self.save_mode = tk.StringVar(value="manual")
        self.m3u_name = tk.StringVar(value=t["default_name"])
        self.usb_var = tk.StringVar(value="")
        self.count_text = tk.StringVar(value=t["count_fmt"].format(count=0))
        self.source_m3u: Path | None = None

        self.drag_start_y = 0
        self.drag_candidate_index = None
        self.drag_source_indices: list[int] = []
        self.drag_target_index = None
        self.drag_active = False

        self._build_ui()

    def _build_ui(self):
        t = LANG[self.lang.get()]
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
        style.map("TCombobox", fieldbackground=[("disabled", "#d9d9d9")], foreground=[("disabled", "#888888")])

        style.configure(
            "Treeview",
            rowheight=24,
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="#102a43",
        )
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#dfefff")], foreground=[("selected", "#102a43")])

        actions = ttk.Frame(main, style="Main.TFrame")
        actions.pack(fill="x", pady=(0, 6))

        btn_new = ttk.Button(actions, text=t["btn_new"], command=self.new_playlist)
        btn_new.pack(side="left", padx=(0, 6))
        ToolTip(btn_new, t["tip_new"])

        btn_open = ttk.Button(actions, text=t["btn_open"], command=self.load_m3u)
        btn_open.pack(side="left", padx=(0, 12))
        ToolTip(btn_open, t["tip_open"])

        btn_del = ttk.Button(actions, text=t["btn_del"], command=self.remove_selected)
        btn_del.pack(side="left", padx=(0, 6))
        ToolTip(btn_del, t["tip_del"])

        btn_up = ttk.Button(actions, text=t["btn_up"], command=self.move_up)
        btn_up.pack(side="left", padx=(0, 6))
        ToolTip(btn_up, t["tip_up"])

        btn_down = ttk.Button(actions, text=t["btn_down"], command=self.move_down)
        btn_down.pack(side="left", padx=(0, 12))
        ToolTip(btn_down, t["tip_down"])

        self.fix_chars_btn = ttk.Button(actions, text=t["btn_fix"], command=self._open_fix_dialog, state="disabled")
        self.fix_chars_btn.pack(side="left", padx=(0, 12))
        ToolTip(self.fix_chars_btn, t["tip_fix"])

        ttk.Checkbutton(
            actions,
            text=t["shuffle"],
            variable=self.shuffle_mode,
            command=self.toggle_shuffle,
        ).pack(side="left")

        ttk.Label(actions, textvariable=self.count_text, style="Total.TLabel").pack(side="right")

        btn_about = ttk.Button(actions, text="\u2139\ufe0f", command=self._show_about, width=3)
        btn_about.pack(side="right", padx=(0, 6))
        ToolTip(btn_about, t["about_title"])

        btn_lang = ttk.Button(actions, text=t["lang_btn"], command=self._toggle_language, width=3)
        btn_lang.pack(side="right", padx=(0, 6))
        ToolTip(btn_lang, t["tip_lang"])

        list_frame = ttk.LabelFrame(main, text=t["frame_list"], padding=8, style="Card.TLabelframe")
        list_frame.pack(fill="both", expand=True)

        tree_wrap = ttk.Frame(list_frame, style="Card.TLabelframe")
        tree_wrap.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_wrap,
            columns=("check", "n", "ruta"),
            show="headings",
            selectmode="extended",
        )
        self.tree.heading("check", text=t["col_sel"])
        self.tree.heading("n", text=t["col_num"])
        self.tree.heading("ruta", text=t["col_path"])
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
            text=t["empty_state"],
            style="Pista.TLabel",
            justify="center",
            font=("Segoe UI", 26, "bold"),
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        self.insert_line = tk.Frame(self.tree, bg="#1b9aaa", height=2)

        self.tree.tag_configure('warn', foreground='#cc0000')

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<B1-Motion>", self._on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_release)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Escape>", self._clear_selection_event)

        save_cfg = ttk.LabelFrame(main, text=t["frame_save"], padding=8, style="Card.TLabelframe")
        save_cfg.pack(fill="x", pady=(10, 0))

        mode_row = ttk.Frame(save_cfg)
        mode_row.pack(fill="x", pady=(0, 6))
        ttk.Radiobutton(
            mode_row,
            text=t["mode_manual"],
            variable=self.save_mode,
            value="manual",
            command=self._refresh_usb_state,
        ).pack(side="left")
        ttk.Radiobutton(
            mode_row,
            text=t["mode_usb"],
            variable=self.save_mode,
            value="usb",
            command=self._refresh_usb_state,
        ).pack(side="left", padx=(12, 0))

        usb_row = ttk.Frame(save_cfg)
        usb_row.pack(fill="x", pady=(0, 6))
        ttk.Label(usb_row, text=t["lbl_usb"]).pack(side="left")
        self.usb_combo = ttk.Combobox(usb_row, textvariable=self.usb_var, state="readonly", width=18)
        self.usb_combo.pack(side="left", padx=(6, 6))
        self.refresh_usb_btn = ttk.Button(usb_row, text=t["btn_refresh"], command=self.refresh_usb_list)
        self.refresh_usb_btn.pack(side="left")
        ToolTip(self.refresh_usb_btn, t["tip_refresh"])

        name_row = ttk.Frame(save_cfg)
        name_row.pack(fill="x")
        ttk.Label(name_row, text=t["lbl_name"]).pack(side="left")
        ttk.Entry(name_row, textvariable=self.m3u_name, width=30).pack(side="left", padx=(6, 8))
        ttk.Label(name_row, text=t["lbl_hint"]).pack(side="left", padx=(0, 12))
        btn_gen = ttk.Button(name_row, text=t["btn_gen"], style="Guardar.TButton", command=self.generate_m3u)
        btn_gen.pack(side="right")
        ToolTip(btn_gen, t["tip_gen"])

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label=t["ctx_del"], command=self.remove_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label=t["ctx_up"], command=self.move_up)
        self.context_menu.add_command(label=t["ctx_down"], command=self.move_down)
        self.context_menu.add_command(label=t["ctx_top"], command=self.move_selected_to_top)
        self.context_menu.add_command(label=t["ctx_bottom"], command=self.move_selected_to_bottom)
        self.context_menu.add_separator()
        self.context_menu.add_command(label=t["ctx_fix"], command=self._fix_single_from_context)

        self.refresh_usb_list()
        self._refresh_usb_state()

    def _toggle_language(self):
        current = self.lang.get()
        self.lang.set("en" if current == "es" else "es")

    def _change_language(self):
        selected = [i for i in self._selected_indices() if i < len(self.playlist_model)]
        for w in self.winfo_children():
            w.destroy()
        self._build_ui()
        self._refresh_tree()
        if selected:
            self.tree.selection_set([str(i) for i in selected])
            self._update_selection_checks()

    def _show_about(self):
        t = LANG[self.lang.get()]
        dlg = tk.Toplevel(self)
        dlg.title(t["about_title"])
        dlg.geometry("380x290")
        dlg.resizable(False, False)
        dlg.configure(bg="#eaf3ff")
        dlg.transient(self)
        dlg.grab_set()

        title_frame = tk.Frame(dlg, bg="#eaf3ff")
        title_frame.pack(pady=(20, 4))

        if hasattr(self, "_icon_img"):
            about_icon = self._icon_img.subsample(21, 21)
            icon_label = tk.Label(title_frame, image=about_icon, bg="#eaf3ff")
            icon_label.image = about_icon
            icon_label.pack(side="left", padx=(0, 8))

        ttk.Label(title_frame, text="m3u Creator App", font=("Segoe UI", 16, "bold"),
                  background="#eaf3ff", foreground="#1d3557").pack(side="left")
        ttk.Label(dlg, text=f"v{__version__}", font=("Segoe UI", 11),
                  background="#eaf3ff", foreground="#555555").pack()
        ttk.Label(dlg, text=t["about_desc"], font=("Segoe UI", 10),
                  background="#eaf3ff", foreground="#333333").pack(pady=(8, 16))

        link = tk.Label(dlg, text=t["about_made_by"], font=("Segoe UI", 10, "underline"),
                        fg="#1b9aaa", bg="#eaf3ff", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda _: self._open_github())

        ttk.Label(dlg, text=t["about_license"], font=("Segoe UI", 9),
                  background="#eaf3ff", foreground="#888888").pack(pady=(4, 0))

        info = f"Python {sys.version.split()[0]} | Tkinter"
        ttk.Label(dlg, text=info, font=("Segoe UI", 8),
                  background="#eaf3ff", foreground="#888888").pack(pady=(16, 0))

        ttk.Button(dlg, text=t["btn_close"], command=dlg.destroy).pack(pady=(16, 10))

    @staticmethod
    def _open_github():
        import webbrowser
        webbrowser.open("https://github.com/inputgain")

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

    @staticmethod
    def _find_non_ascii_chars(text: str) -> list[str]:
        chars = set()
        for ch in text:
            if ord(ch) > 127:
                chars.add(ch)
        return sorted(chars, key=ord)

    def _refresh_tree(self):
        t = LANG[self.lang.get()]
        selected_before = set(self._selected_indices())
        self.tree.delete(*self.tree.get_children())
        for i, path in enumerate(self.playlist_model):
            check = "\u2713" if i in selected_before else ""
            display = self._display_path(path)
            warn_chars = self._find_non_ascii_chars(display)
            if warn_chars:
                chars_str = " | ".join(warn_chars)
                display += f"  ]- {t['warn_suffix']}: {chars_str}"
                self.tree.insert("", "end", iid=str(i), values=(check, f"{i + 1:03d}", display), tags=('warn',))
            else:
                self.tree.insert("", "end", iid=str(i), values=(check, f"{i + 1:03d}", display))

        for idx in selected_before:
            if idx < len(self.playlist_model):
                self.tree.selection_add(str(idx))

        self.count_text.set(t["count_fmt"].format(count=len(self.playlist_model)))
        self._hide_insert_preview()
        self._set_empty_state(visible=(len(self.playlist_model) == 0))
        self._update_selection_checks()
        has_warns = self._has_warn_rows()
        self.fix_chars_btn.configure(state="normal" if has_warns else "disabled")

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
        m3u_files = [p for p in dropped if p.suffix.lower() == ".m3u"]
        if m3u_files:
            self._load_m3u_from_path(m3u_files[0])
        other = [p for p in dropped if p.suffix.lower() != ".m3u"]
        if other:
            new_files = collect_mp3_from_inputs(other)
            seen = set(self.playlist_model)
            unique_files = []
            for p in new_files:
                if p not in seen:
                    seen.add(p)
                    unique_files.append(p)
            if unique_files:
                self.original_order.extend(unique_files)
                if self.shuffle_mode.get():
                    self.playlist_model.extend(unique_files)
                    random.shuffle(self.playlist_model)
                else:
                    self.playlist_model.extend(unique_files)
                self._refresh_tree()

    def _show_missing_files_dialog(self, missing: list[Path]) -> bool:
        """Show dialog for missing files. Returns True to keep them, False to remove."""
        if not missing:
            return True
        t = LANG[self.lang.get()]
        msg = ""
        for p in missing[:15]:
            msg += f"  - {p}\n"
        n = len(missing) - 15
        if n > 0:
            msg += t["mb_missing_more"].format(n=n)
        full_msg = t["mb_missing_msg"].format(list=msg)
        return messagebox.askyesno(t["mb_missing_title"], full_msg, icon="warning")

    def _load_m3u_from_path(self, m3u_path: Path):
        all_paths, missing = parse_m3u_file(m3u_path)
        if not all_paths:
            t = LANG[self.lang.get()]
            messagebox.showinfo(t["mb_empty_title"], t["mb_empty_msg"])
            return
        if missing:
            keep = self._show_missing_files_dialog(missing)
            if not keep:
                missing_set = set(missing)
                all_paths = [p for p in all_paths if p not in missing_set]
        self.playlist_model = all_paths
        self.original_order = list(all_paths)
        self.source_m3u = m3u_path
        self.m3u_name.set(m3u_path.stem)
        self._refresh_tree()

    def load_m3u(self):
        t = LANG[self.lang.get()]
        path = filedialog.askopenfilename(
            filetypes=[(t["file_filter_m3u"], "*.m3u"), (t["file_filter_all"], "*.*")],
        )
        if not path:
            return
        self._load_m3u_from_path(Path(path))

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

        has_ascii_issues = False
        for idx in self._selected_indices():
            path = self.playlist_model[idx]
            if self._find_non_ascii_chars(self._display_path(path)):
                has_ascii_issues = True
                break
        self.context_menu.entryconfigure(LANG[self.lang.get()]["ctx_fix"],
                                         state="normal" if has_ascii_issues else "disabled")

        self.context_menu.tk_popup(event.x_root, event.y_root)

    def new_playlist(self):
        if self.playlist_model:
            ok = messagebox.askyesno(LANG[self.lang.get()]["mb_newlist_title"],
                                     LANG[self.lang.get()]["mb_newlist_msg"])
            if not ok:
                return
        self.playlist_model = []
        self.original_order = []
        self.source_m3u = None
        self.m3u_name.set(LANG[self.lang.get()]["default_name"])
        self._refresh_tree()

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
        self.refresh_usb_btn.configure(state=state)

    def _clear_selection_event(self, _event):
        self.tree.selection_remove(self.tree.selection())
        self._update_selection_checks()

    def _has_warn_rows(self) -> bool:
        for path in self.playlist_model:
            if self._find_non_ascii_chars(self._display_path(path)):
                return True
        return False

    def _get_warn_indices(self) -> list[int]:
        return [
            i for i, path in enumerate(self.playlist_model)
            if self._find_non_ascii_chars(self._display_path(path))
        ]

    def _fix_single_from_context(self):
        selected = self._selected_indices()
        if not selected:
            return
        self._open_fix_dialog(indices=[selected[0]])

    @staticmethod
    def _auto_fix_name(name: str) -> str:
        result = name
        for bad, good in CHAR_MAP.items():
            result = result.replace(bad, good)
        return result

    @staticmethod
    def _auto_fix_path(full_path: str) -> str:
        normalized = full_path.replace("\\", "/")
        parts = normalized.split("/")
        return "/".join(
            M3UCreatorApp._auto_fix_name(p) if i > 0 else p
            for i, p in enumerate(parts)
        )

    def _open_fix_dialog(self, indices: list[int] | None = None):
        t = LANG[self.lang.get()]
        if indices is None:
            indices = self._get_warn_indices()
        if not indices:
            messagebox.showinfo(t["mb_noproblems_title"], t["mb_noproblems_msg"])
            return

        dlg = tk.Toplevel(self)
        dlg.title(t["dlg_title"])
        dlg.geometry("820x580")
        dlg.minsize(640, 400)
        dlg.resizable(True, True)
        dlg.configure(bg="#eaf3ff")
        dlg.transient(self)
        dlg.grab_set()

        # ── Header ──
        header = tk.Frame(dlg, bg="#1d3557", height=48)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        count = len(indices)
        s = "" if count == 1 else "s"
        tk.Label(
            header,
            text=t["dlg_header"].format(count=count, s=s),
            font=("Segoe UI", 12, "bold"),
            bg="#1d3557",
            fg="#ffffff",
        ).pack(side="left", padx=16, pady=10)

        # ── Bottom panel (fixed) ──
        auto_var = tk.BooleanVar(value=True)
        bottom_frame = tk.Frame(dlg, bg="#eaf3ff")
        bottom_frame.pack(side="bottom", fill="x")

        check_frame = tk.Frame(bottom_frame, bg="#eaf3ff")
        check_frame.pack(fill="x", padx=18, pady=(8, 0))
        ttk.Checkbutton(
            check_frame,
            text=t["dlg_auto"],
            variable=auto_var,
        ).pack(side="left")

        btn_frame = tk.Frame(bottom_frame, bg="#eaf3ff")
        btn_frame.pack(fill="x", padx=18, pady=12)
        btn_cancel = ttk.Button(btn_frame, text=t["btn_cancel"], command=dlg.destroy)
        btn_cancel.pack(side="right")
        ToolTip(btn_cancel, t["tip_cancel"])
        rename_btn = ttk.Button(btn_frame, text=t["btn_rename"])
        ToolTip(rename_btn, t["tip_rename"])
        rename_btn.pack(side="right", padx=(8, 0))

        # ── Scrollable middle ──
        middle = tk.Frame(dlg, bg="#eaf3ff")
        middle.pack(side="top", fill="both", expand=True)

        canvas = tk.Canvas(middle, bg="#eaf3ff", highlightthickness=0)
        vsb = ttk.Scrollbar(middle, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#eaf3ff")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        inner_win = canvas.create_window((0, 0), window=scroll_frame, anchor="nw", tags="inner")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(14, 0), pady=10)

        # ── File cards ──
        fix_entries: list[_FixEntry] = []

        for i, idx in enumerate(indices):
            path = self.playlist_model[idx]
            abs_display = str(path.resolve()).replace("\\", "/")
            warn_chars = self._find_non_ascii_chars(abs_display)
            chars_str = " | ".join(warn_chars) if warn_chars else ""

            # Card
            card = tk.Frame(scroll_frame, bg="#ffffff", highlightbackground="#c8d4e0",
                            highlightthickness=1, bd=0)
            card.pack(fill="x", pady=(0 if i == 0 else 8, 0), padx=6)

            # Top row: badge + icon + warn badge
            top = tk.Frame(card, bg="#ffffff")
            top.pack(fill="x", padx=14, pady=(12, 4))

            tk.Label(top, text=f"#{idx + 1:03d}", font=("Consolas", 10, "bold"),
                     bg="#e2e8f0", fg="#1d3557", padx=6, pady=1).pack(side="left")
            tk.Label(top, text="  ⚠", font=("Segoe UI", 10),
                     bg="#ffffff", fg="#cc0000").pack(side="left")

            if chars_str:
                tk.Label(top, text=t["lbl_noascii"].format(chars=chars_str), font=("Segoe UI", 8),
                         bg="#fff0f0", fg="#cc0000", padx=4, pady=1).pack(side="right")

            # Entry area
            entry_frame = tk.Frame(card, bg="#ffffff")
            entry_frame.pack(fill="x", padx=14, pady=(0, 10))

            # Original path (read-only label)
            tk.Label(entry_frame, text=t["lbl_orig"], font=("Segoe UI", 9),
                     bg="#ffffff", fg="#333333").pack(anchor="w")
            tk.Label(entry_frame, text=abs_display, font=("Consolas", 9),
                     bg="#ffffff", fg="#cc0000", anchor="w", wraplength=740,
                     justify="left").pack(anchor="w", pady=(0, 6))

            # Editable entry
            tk.Label(entry_frame, text=t["lbl_new"], font=("Segoe UI", 9),
                     bg="#ffffff", fg="#333333").pack(anchor="w")

            name_entry = tk.Entry(entry_frame, font=("Consolas", 10), bg="#f8fafe",
                                  fg="#102a43", insertbackground="#102a43",
                                  highlightthickness=1, highlightbackground="#b0c4de",
                                  highlightcolor="#1b9aaa", bd=1, relief="flat")
            name_entry.pack(fill="x", pady=(2, 0), ipady=3)
            name_entry.insert(0, abs_display)
            name_entry.select_range(0, "end")
            name_entry.xview("end")

            # Preview label
            preview_var = tk.StringVar(value="")
            preview_lbl = tk.Label(entry_frame, textvariable=preview_var,
                                   font=("Segoe UI", 9), bg="#ffffff", fg="#2d8a4e", anchor="w")

            # Key release: update preview
            def _make_update(ent, pv, pl, orig_disp):
                def _update(_event=None):
                    val = ent.get().strip()
                    if val and val != orig_disp:
                        pl.pack(anchor="w", pady=(3, 0))
                        pv.set(f"→ {val}")
                    else:
                        pl.pack_forget()
                        pv.set("")
                return _update

            name_entry.bind("<KeyRelease>", _make_update(name_entry, preview_var, preview_lbl, abs_display))

            fix_entries.append(_FixEntry(idx, path, abs_display, name_entry, preview_lbl, preview_var))

        # ── Scrollbar: only show if needed ──
        def _check_scroll():
            canvas.update_idletasks()
            content_h = scroll_frame.winfo_reqheight()
            visible_h = canvas.winfo_height()
            if content_h > visible_h and visible_h > 1:
                vsb.pack(side="right", fill="y", pady=10, padx=(0, 14))
                canvas.configure(yscrollcommand=vsb.set)
            else:
                vsb.pack_forget()
                canvas.configure(yscrollcommand="")

        def _on_canvas_cfg(event):
            canvas.itemconfig("inner", width=event.width)
            _check_scroll()
        canvas.bind("<Configure>", _on_canvas_cfg)

        def _on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<MouseWheel>", _on_mouse_wheel)
        scroll_frame.bind("<MouseWheel>", _on_mouse_wheel)
        for child in scroll_frame.winfo_children():
            child.bind("<MouseWheel>", _on_mouse_wheel)
            for sub in child.winfo_children():
                sub.bind("<MouseWheel>", _on_mouse_wheel)

        # ── Auto-fix ──
        def apply_auto_fix():
            for fe in fix_entries:
                fixed = self._auto_fix_path(fe.orig_str)
                fe.entry.delete(0, "end")
                fe.entry.insert(0, fixed)
                if fixed != fe.orig_str:
                    fe.preview_lbl.configure(text=f"→ {fixed}")
                    fe.preview_lbl.pack(anchor="w", pady=(3, 0))
                else:
                    fe.preview_lbl.pack_forget()

        def restore_original():
            for fe in fix_entries:
                fe.entry.delete(0, "end")
                fe.entry.insert(0, fe.orig_str)
                fe.preview_lbl.pack_forget()

        def toggle_auto_fix():
            if auto_var.get():
                apply_auto_fix()
            else:
                restore_original()

        auto_var.trace_add("write", lambda *_: toggle_auto_fix())

        # ── Rename ──
        def on_apply():
            # print("\n" + "=" * 60)
            # print("ON_APPLY START")
            # print(f"fix_entries: {len(fix_entries)}")
            # for fe in fix_entries:
            #     print(f"  [{fe.idx}] {fe.orig_path}")
            #     print(f"       -> {fe.entry.get().strip()}")
            # print("=" * 60)

            if len(fix_entries) > 1:
                t = LANG[self.lang.get()]
                ok = messagebox.askyesno(
                    t["mb_confirm_title"],
                    t["mb_confirm_msg"].format(count=len(fix_entries)),
                    parent=dlg,
                )
                if not ok:
                    return

            errors = []
            renamed_count = 0

            orig_paths = {fe.idx: fe.orig_path for fe in fix_entries}
            dir_moves: list[tuple[Path, Path]] = []
            seen_dirs: set[tuple[Path, Path]] = set()

            for fe in fix_entries:
                new_str = fe.entry.get().strip()
                if not new_str or new_str == fe.orig_str:
                    continue
                new_path = Path(new_str)
                if not new_path.is_absolute():
                    new_path = Path(fe.orig_path.anchor) / new_str
                if fe.orig_path.resolve() == new_path.resolve():
                    continue

                old_p = fe.orig_path.resolve().parts
                new_p = new_path.resolve().parts
                common = 0
                for a, b in zip(old_p, new_p):
                    if a == b:
                        common += 1
                    else:
                        break
                for j in range(len(old_p) - 1, common, -1):
                    od = Path(*old_p[:j])
                    nd = Path(*new_p[:j])
                    if od != nd and (od, nd) not in seen_dirs:
                        seen_dirs.add((od, nd))
                        dir_moves.append((od, nd))

            # print(f"\nPhase 1: {len(dir_moves)} dir moves")
            # for od, nd in dir_moves:
            #     print(f"  {od} -> {nd}")

            dir_done: dict[Path, Path] = {}

            def remap_through(path: Path) -> Path:
                for _ in range(len(dir_done)):
                    for od, nd in dir_done.items():
                        try:
                            rel = path.relative_to(od)
                        except ValueError:
                            continue
                        new = nd / rel
                        if new == path:
                            continue
                        path = new
                        break
                    else:
                        break
                return path

            for od, nd in sorted(dir_moves, key=lambda kv: len(kv[0].parts)):
                actual_od = remap_through(od)
                if actual_od == nd:
                    continue
                if nd.exists():
                    if actual_od.exists():
                        errors.append(LANG[self.lang.get()]["mb_already_exists"].format(name=nd))
                    continue
                if actual_od.exists():
                    try:
                        shutil.move(str(actual_od), str(nd))
                    except OSError as e:
                        errors.append(LANG[self.lang.get()]["mb_folder_error"].format(name=od.name, error=e))
                        continue
                dir_done[actual_od] = nd

            # print(f"\nPhase 3: {len(fix_entries)} entries")
            for fe in fix_entries:
                new_str = fe.entry.get().strip()
                if not new_str or new_str == fe.orig_str:
                    continue
                new_path = Path(new_str)
                if not new_path.is_absolute():
                    new_path = Path(fe.orig_path.anchor) / new_str
                if fe.orig_path.resolve() == new_path.resolve():
                    continue

                current_path = remap_through(fe.orig_path)

                if current_path.resolve() == new_path.resolve():
                    # print(f"  [{fe.idx}] SKIP (same): {current_path.name}")
                    self.playlist_model[fe.idx] = new_path.resolve()
                    if fe.orig_path in self.original_order:
                        self.original_order[self.original_order.index(fe.orig_path)] = new_path.resolve()
                    fe.orig_path = new_path
                    fe.orig_str = str(new_path).replace("\\", "/")
                    fe.entry.delete(0, "end")
                    fe.entry.insert(0, fe.orig_str)
                    fe.preview_var.set("")
                    fe.preview_lbl.pack_forget()
                    renamed_count += 1
                    continue

                try:
                    if current_path.name != new_path.name:
                        dst = current_path.parent / new_path.name
                        if dst.exists():
                            errors.append(f"{fe.orig_str}:\n  {LANG[self.lang.get()]['mb_already_exists'].format(name=dst.name)}")
                            continue
                        shutil.move(str(current_path), str(dst))
                        # print(f"  [{fe.idx}] RENAMED: {current_path.name} -> {dst.name}")
                    # else:
                    #     print(f"  [{fe.idx}] OK: {current_path.name}")
                    self.playlist_model[fe.idx] = new_path.resolve()
                    if fe.orig_path in self.original_order:
                        self.original_order[self.original_order.index(fe.orig_path)] = new_path.resolve()
                    fe.orig_path = new_path
                    fe.orig_str = str(new_path).replace("\\", "/")
                    fe.entry.delete(0, "end")
                    fe.entry.insert(0, fe.orig_str)
                    fe.preview_var.set("")
                    fe.preview_lbl.pack_forget()
                    renamed_count += 1
                except OSError as e:
                    errors.append(f"{fe.orig_str}:\n  {e}")

            if dir_done:
                for i, p in enumerate(self.playlist_model):
                    self.playlist_model[i] = remap_through(p)

            old_dirs = set()
            for idx, p in orig_paths.items():
                rp = p.resolve()
                while rp.parent != rp:
                    old_dirs.add(rp)
                    rp = rp.parent
            for od in sorted(old_dirs, key=lambda p: len(p.parts), reverse=True):
                if od.exists():
                    try:
                        if not any(od.iterdir()):
                            od.rmdir()
                            # print(f"CLEANUP: removed {od}")
                    except OSError:
                        pass

            # print(f"\nRESULT: renamed={renamed_count} errors={len(errors)}")
            # for e in errors:
            #     print(f"  ERR: {e}")

            if errors:
                t = LANG[self.lang.get()]
                messagebox.showwarning(
                    t["mb_errors_title"],
                    t["mb_errors_msg"].format(errors="\n".join(errors)),
                    parent=dlg,
                )
            if renamed_count > 0:
                self._refresh_tree()
            dlg.destroy()

        rename_btn.configure(command=on_apply)

        if auto_var.get():
            apply_auto_fix()

    def _resolve_output_file(self) -> Path | None:
        t = LANG[self.lang.get()]
        raw_name = self.m3u_name.get().strip()
        if not raw_name:
            messagebox.showerror(t["mb_noname_title"], t["mb_noname_msg"])
            return None
        filename = raw_name if raw_name.lower().endswith(".m3u") else f"{raw_name}.m3u"

        if self.save_mode.get() == "manual":
            initial = filename
            if self.source_m3u and self.source_m3u.exists():
                initial = str(self.source_m3u)
            selected = filedialog.asksaveasfilename(
                defaultextension=".m3u",
                filetypes=[(t["file_filter_m3u"], "*.m3u")],
                initialfile=initial,
            )
            return Path(selected) if selected else None

        usb = self.usb_var.get().strip()
        if not usb:
            messagebox.showerror(t["mb_nousb_title"], t["mb_nousb_msg"])
            return None
        return Path(usb) / filename

    def generate_m3u(self):
        t = LANG[self.lang.get()]
        if not self.playlist_model:
            messagebox.showerror(t["mb_emptylist_title"], t["mb_emptylist_msg"])
            return
        target = self._resolve_output_file()
        if not target:
            return

        lines = to_relative_m3u_lines(self.playlist_model, target.parent)
        confirm_overwrite = self.save_mode.get() != "manual"
        if write_m3u(lines, target, confirm_overwrite=confirm_overwrite, lang=self.lang.get()):
            messagebox.showinfo(t["mb_done_title"], t["mb_done_msg"].format(target=target))


if __name__ == "__main__":
    app = M3UCreatorApp()
    app.mainloop()
