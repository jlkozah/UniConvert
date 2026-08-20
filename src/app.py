import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

sys.path.insert(0, os.path.dirname(__file__))
from converters import TARGETS, detect_kind, run_conversion

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD

    BASE_CLASS = TkinterDnD.Tk
    DND_AVAILABLE = True
except ImportError:
    BASE_CLASS = tk.Tk
    DND_AVAILABLE = False

ACCENT = "#5b8def"
BG = "#15161a"
CARD = "#1e2025"
CARD_HOVER = "#262932"
BORDER = "#33363f"
TEXT_MUTED = "#9a9ea8"
GREEN = "#5fd97a"
RED = "#e26262"

KIND_ICONS = {
    "image": "🖼",
    "pdf": "📄",
    "txt": "📝",
    "docx": "📃",
    "md": "📘",
    "html": "🌐",
    "csv": "📊",
    "json": "🔣",
    "yaml": "🔣",
    "xlsx": "📈",
    "zip": "🗜",
    "audio": "🎵",
    "video": "🎬",
}


class FileRow(ctk.CTkFrame):
    def __init__(self, master, path, kind, on_remove):
        super().__init__(master, fg_color=CARD, corner_radius=10, height=44)
        self.path = path
        self.pack_propagate(False)

        icon = KIND_ICONS.get(kind, "📁")
        name = os.path.basename(path)
        if len(name) > 46:
            name = name[:43] + "..."

        ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 15)).pack(side="left", padx=(12, 8))
        ctk.CTkLabel(self, text=name, font=("Segoe UI", 12), anchor="w").pack(
            side="left", fill="x", expand=True
        )
        ctk.CTkButton(
            self,
            text="✕",
            width=28,
            height=28,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#3a2222",
            text_color=TEXT_MUTED,
            command=lambda: on_remove(path),
        ).pack(side="right", padx=8)


class App(BASE_CLASS):
    def __init__(self):
        super().__init__()
        self.title("UniConvert")
        self.geometry("720x680")
        self.minsize(620, 560)
        self.configure(bg=BG)

        self.files = []
        self.out_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.row_widgets = {}

        self._build_ui()

        if DND_AVAILABLE:
            self.drop_zone.drop_target_register(DND_FILES)
            self.drop_zone.dnd_bind("<<Drop>>", self._on_drop)

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color=BG)
        outer.pack(fill="both", expand=True)

        header = ctk.CTkFrame(outer, fg_color=BG)
        header.pack(fill="x", padx=28, pady=(24, 8))
        ctk.CTkLabel(header, text="UniConvert", font=("Segoe UI", 28, "bold")).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Images, PDF, texte, tableurs, audio, video, archives — glisse, choisis, convertis.",
            font=("Segoe UI", 12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(2, 0))

        body = ctk.CTkFrame(outer, fg_color=BG)
        body.pack(fill="both", expand=True, padx=28, pady=(8, 20))

        self.drop_zone = ctk.CTkFrame(
            body, height=120, corner_radius=16, fg_color=CARD, border_width=2, border_color=BORDER
        )
        self.drop_zone.pack(fill="x", pady=(0, 14))
        self.drop_zone.pack_propagate(False)

        drop_text = "Depose des fichiers ici  (ou clique)" if DND_AVAILABLE else "Clique pour choisir des fichiers"
        self.drop_label = ctk.CTkLabel(
            self.drop_zone, text=f"⇩  {drop_text}", font=("Segoe UI", 14), text_color=TEXT_MUTED
        )
        self.drop_label.pack(expand=True)
        for w in (self.drop_zone, self.drop_label):
            w.bind("<Button-1>", lambda e: self._browse())
            w.bind("<Enter>", lambda e: self.drop_zone.configure(border_color=ACCENT))
            w.bind("<Leave>", lambda e: self.drop_zone.configure(border_color=BORDER))

        list_header = ctk.CTkFrame(body, fg_color=BG)
        list_header.pack(fill="x", pady=(0, 6))
        self.count_label = ctk.CTkLabel(
            list_header, text="Aucun fichier", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED
        )
        self.count_label.pack(side="left")
        ctk.CTkButton(
            list_header,
            text="Tout effacer",
            width=100,
            height=26,
            corner_radius=8,
            fg_color="transparent",
            hover_color=CARD_HOVER,
            text_color=TEXT_MUTED,
            font=("Segoe UI", 11),
            command=self._clear_files,
        ).pack(side="right")

        self.list_scroll = ctk.CTkScrollableFrame(body, fg_color="transparent", height=170)
        self.list_scroll.pack(fill="x", pady=(0, 16))

        options = ctk.CTkFrame(body, fg_color=CARD, corner_radius=14)
        options.pack(fill="x", pady=(0, 16))
        opt_inner = ctk.CTkFrame(options, fg_color="transparent")
        opt_inner.pack(fill="x", padx=18, pady=16)

        fmt_row = ctk.CTkFrame(opt_inner, fg_color="transparent")
        fmt_row.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(fmt_row, text="Convertir vers", font=("Segoe UI", 13, "bold")).pack(side="left")
        self.format_var = tk.StringVar(value="-")
        self.format_menu = ctk.CTkOptionMenu(
            fmt_row, variable=self.format_var, values=["-"], width=140, fg_color=ACCENT, button_color=ACCENT
        )
        self.format_menu.pack(side="right")

        out_row = ctk.CTkFrame(opt_inner, fg_color="transparent")
        out_row.pack(fill="x")
        self.out_label = ctk.CTkLabel(
            out_row, text=self._short_out_dir(), font=("Segoe UI", 11), text_color=TEXT_MUTED, anchor="w"
        )
        self.out_label.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            out_row,
            text="Changer le dossier",
            width=140,
            height=28,
            corner_radius=8,
            fg_color="transparent",
            hover_color=CARD_HOVER,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT_MUTED,
            font=("Segoe UI", 11),
            command=self._choose_out_dir,
        ).pack(side="right")

        self.convert_btn = ctk.CTkButton(
            body,
            text="Convertir",
            height=48,
            corner_radius=12,
            font=("Segoe UI", 15, "bold"),
            fg_color=ACCENT,
            hover_color="#4573d1",
            command=self._start_conversion,
        )
        self.convert_btn.pack(fill="x", pady=(0, 10))

        self.progress = ctk.CTkProgressBar(body, height=6, corner_radius=3, progress_color=ACCENT)
        self.progress.set(0)
        self.progress.pack(fill="x", pady=(0, 8))
        self.progress.pack_forget()

        self.status_label = ctk.CTkLabel(body, text="", font=("Segoe UI", 12))
        self.status_label.pack()

    def _short_out_dir(self):
        d = self.out_dir
        if len(d) > 55:
            d = "..." + d[-52:]
        return f"📁  {d}"

    def _on_drop(self, event):
        raw = self.tk.splitlist(event.data)
        self._add_files(raw)

    def _browse(self):
        paths = filedialog.askopenfilenames(title="Choisir des fichiers")
        if paths:
            self._add_files(paths)

    def _add_files(self, paths):
        for p in paths:
            p = p.strip("{}")
            if os.path.isfile(p) and p not in self.files:
                self.files.append(p)
        self._refresh_list()
        self._refresh_formats()

    def _remove_file(self, path):
        self.files = [f for f in self.files if f != path]
        self._refresh_list()
        self._refresh_formats()

    def _clear_files(self):
        self.files = []
        self._refresh_list()
        self._refresh_formats()

    def _refresh_list(self):
        for child in self.list_scroll.winfo_children():
            child.destroy()

        if not self.files:
            self.count_label.configure(text="Aucun fichier")
            return

        self.count_label.configure(text=f"{len(self.files)} fichier(s)")
        for f in self.files:
            kind = detect_kind(f)
            row = FileRow(self.list_scroll, f, kind, self._remove_file)
            row.pack(fill="x", pady=3)

    def _refresh_formats(self):
        if not self.files:
            self.format_menu.configure(values=["-"])
            self.format_var.set("-")
            return

        kind = detect_kind(self.files[0])
        options = TARGETS.get(kind, [])
        if options:
            self.format_menu.configure(values=options)
            self.format_var.set(options[0])
        else:
            self.format_menu.configure(values=["non supporte"])
            self.format_var.set("non supporte")

    def _choose_out_dir(self):
        d = filedialog.askdirectory(title="Dossier de sortie")
        if d:
            self.out_dir = d
            self.out_label.configure(text=self._short_out_dir())

    def _start_conversion(self):
        if not self.files:
            messagebox.showwarning("UniConvert", "Ajoute au moins un fichier.")
            return
        target = self.format_var.get()
        if not target or target in ("-", "non supporte"):
            messagebox.showwarning("UniConvert", "Choisis un format de sortie valide.")
            return

        self.convert_btn.configure(state="disabled", text="Conversion en cours...")
        self.status_label.configure(text="", text_color=TEXT_MUTED)
        self.progress.pack(fill="x", pady=(0, 8))
        self.progress.configure(mode="indeterminate")
        self.progress.start()

        thread = threading.Thread(target=self._convert_worker, args=(target,), daemon=True)
        thread.start()

    def _convert_worker(self, target):
        try:
            results = run_conversion(self.files, target, self.out_dir)
            self.after(0, lambda: self._on_success(results))
        except Exception as exc:
            self.after(0, lambda: self._on_error(exc))

    def _on_success(self, results):
        self.progress.stop()
        self.progress.pack_forget()
        self.convert_btn.configure(state="normal", text="Convertir")
        self.status_label.configure(
            text=f"✓  {len(results)} fichier(s) converti(s) avec succes", text_color=GREEN
        )
        messagebox.showinfo("UniConvert", f"Termine ! {len(results)} fichier(s) dans :\n{self.out_dir}")

    def _on_error(self, exc):
        self.progress.stop()
        self.progress.pack_forget()
        self.convert_btn.configure(state="normal", text="Convertir")
        self.status_label.configure(text="✕  Echec de la conversion", text_color=RED)
        messagebox.showerror("UniConvert", str(exc))


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
