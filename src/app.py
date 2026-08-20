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


class App(BASE_CLASS):
    def __init__(self):
        super().__init__()
        self.title("UniConvert")
        self.geometry("620x520")
        self.minsize(560, 460)
        self.configure(bg="#1a1a1a")

        self.files = []
        self.out_dir = os.path.join(os.path.expanduser("~"), "Downloads")

        self._build_ui()

        if DND_AVAILABLE:
            self.drop_zone.drop_target_register(DND_FILES)
            self.drop_zone.dnd_bind("<<Drop>>", self._on_drop)

    def _build_ui(self):
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(root, text="UniConvert", font=("Segoe UI", 26, "bold"))
        title.pack(pady=(0, 4))
        subtitle = ctk.CTkLabel(
            root,
            text="Glisse tes fichiers ou choisis-les, puis convertis-les.",
            font=("Segoe UI", 12),
            text_color="#999999",
        )
        subtitle.pack(pady=(0, 16))

        self.drop_zone = ctk.CTkFrame(
            root, height=140, corner_radius=14, fg_color="#242424", border_width=2, border_color="#3a3a3a"
        )
        self.drop_zone.pack(fill="x", pady=(0, 12))
        self.drop_zone.pack_propagate(False)

        drop_label_text = "Depose tes fichiers ici" if DND_AVAILABLE else "Clique pour choisir des fichiers"
        self.drop_label = ctk.CTkLabel(self.drop_zone, text=drop_label_text, font=("Segoe UI", 14))
        self.drop_label.pack(expand=True)
        self.drop_zone.bind("<Button-1>", lambda e: self._browse())
        self.drop_label.bind("<Button-1>", lambda e: self._browse())

        browse_btn = ctk.CTkButton(root, text="Choisir des fichiers", command=self._browse, width=200)
        browse_btn.pack(pady=(0, 12))

        self.file_list = ctk.CTkTextbox(root, height=100, fg_color="#1f1f1f")
        self.file_list.pack(fill="x", pady=(0, 16))
        self.file_list.configure(state="disabled")

        format_frame = ctk.CTkFrame(root, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(format_frame, text="Convertir vers :", font=("Segoe UI", 13)).pack(side="left", padx=(0, 10))
        self.format_var = tk.StringVar(value="")
        self.format_menu = ctk.CTkOptionMenu(format_frame, variable=self.format_var, values=["-"])
        self.format_menu.pack(side="left")

        out_frame = ctk.CTkFrame(root, fg_color="transparent")
        out_frame.pack(fill="x", pady=(0, 16))
        self.out_label = ctk.CTkLabel(out_frame, text=f"Dossier de sortie : {self.out_dir}", font=("Segoe UI", 11), text_color="#999999")
        self.out_label.pack(side="left")
        ctk.CTkButton(out_frame, text="Changer", width=90, command=self._choose_out_dir).pack(side="right")

        self.convert_btn = ctk.CTkButton(
            root, text="Convertir", height=44, font=("Segoe UI", 15, "bold"), command=self._start_conversion
        )
        self.convert_btn.pack(fill="x", pady=(0, 8))

        self.status_label = ctk.CTkLabel(root, text="", font=("Segoe UI", 11), text_color="#7fdc7f")
        self.status_label.pack()

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

        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")
        for f in self.files:
            self.file_list.insert("end", os.path.basename(f) + "\n")
        self.file_list.configure(state="disabled")

        self._refresh_formats()

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
            self.out_label.configure(text=f"Dossier de sortie : {self.out_dir}")

    def _start_conversion(self):
        if not self.files:
            messagebox.showwarning("UniConvert", "Ajoute au moins un fichier.")
            return
        target = self.format_var.get()
        if not target or target in ("-", "non supporte"):
            messagebox.showwarning("UniConvert", "Choisis un format de sortie valide.")
            return

        self.convert_btn.configure(state="disabled", text="Conversion en cours...")
        self.status_label.configure(text="")

        thread = threading.Thread(target=self._convert_worker, args=(target,), daemon=True)
        thread.start()

    def _convert_worker(self, target):
        try:
            results = run_conversion(self.files, target, self.out_dir)
            self.after(0, lambda: self._on_success(results))
        except Exception as exc:
            self.after(0, lambda: self._on_error(exc))

    def _on_success(self, results):
        self.convert_btn.configure(state="normal", text="Convertir")
        self.status_label.configure(text=f"{len(results)} fichier(s) converti(s) avec succes.")
        messagebox.showinfo("UniConvert", f"Termine ! {len(results)} fichier(s) dans :\n{self.out_dir}")

    def _on_error(self, exc):
        self.convert_btn.configure(state="normal", text="Convertir")
        self.status_label.configure(text="", text_color="#e07070")
        messagebox.showerror("UniConvert", str(exc))


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
