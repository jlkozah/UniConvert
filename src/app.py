import locale
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from converters import TARGETS, detect_kind, run_conversion
from lang import FORMAT_CHIPS, t

if getattr(sys, "frozen", False):
    ASSETS_DIR = os.path.join(sys._MEIPASS, "assets")
else:
    ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD

    BASE_CLASS = TkinterDnD.Tk
    DND_AVAILABLE = True
except ImportError:
    BASE_CLASS = tk.Tk
    DND_AVAILABLE = False

BG = "#0e0f14"
SIDEBAR = "#131521"
CARD = "#1a1c28"
CARD_ALT = "#20232f"
CARD_HOVER = "#262a38"
BORDER = "#2c2f3d"
TEXT = "#e8e9ee"
TEXT_MUTED = "#8a8ea0"
ACCENT_A = "#5b7cfa"
ACCENT_B = "#9b6bfa"
ACCENT_HOVER = "#4a68e0"
GREEN = "#4ade80"
RED = "#f26d6d"

KIND_LABELS = {
    "image": ("🖼", "IMG", "#5b7cfa"),
    "pdf": ("📄", "PDF", "#f26d6d"),
    "txt": ("📝", "TXT", "#8a8ea0"),
    "docx": ("📃", "DOCX", "#4a90e2"),
    "md": ("📘", "MD", "#4ade80"),
    "html": ("🌐", "HTML", "#f5a623"),
    "csv": ("📊", "CSV", "#4ade80"),
    "json": ("🔣", "JSON", "#f5a623"),
    "yaml": ("🔣", "YAML", "#f5a623"),
    "xlsx": ("📈", "XLSX", "#1d8348"),
    "zip": ("🗜", "ZIP", "#9b6bfa"),
    "audio": ("🎵", "AUDIO", "#e879b9"),
    "video": ("🎬", "VIDEO", "#f26d6d"),
}


def fmt_size(num_bytes):
    for unit in ("o", "Ko", "Mo", "Go"):
        if num_bytes < 1024:
            return f"{num_bytes:.0f} {unit}" if unit == "o" else f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} To"


def detect_default_lang():
    try:
        code = locale.getdefaultlocale()[0] or ""
    except Exception:
        code = ""
    return "fr" if code.lower().startswith("fr") else "en"


class FileRow(ctk.CTkFrame):
    def __init__(self, master, path, kind, on_remove):
        super().__init__(master, fg_color=CARD, corner_radius=12, height=56)
        self.path = path
        self.pack_propagate(False)

        thumb = self._make_thumb(path, kind)
        thumb_holder = ctk.CTkLabel(self, image=thumb, text="", width=40, height=40)
        thumb_holder.image = thumb
        thumb_holder.pack(side="left", padx=(10, 12), pady=8)

        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=6)

        name = os.path.basename(path)
        if len(name) > 50:
            name = name[:47] + "..."
        ctk.CTkLabel(info, text=name, font=("Segoe UI", 12, "bold"), text_color=TEXT, anchor="w").pack(
            fill="x", anchor="w"
        )

        try:
            size_txt = fmt_size(os.path.getsize(path))
        except OSError:
            size_txt = "?"
        _, label, color = KIND_LABELS.get(kind, ("📁", "?", TEXT_MUTED))
        sub = ctk.CTkFrame(info, fg_color="transparent")
        sub.pack(fill="x", anchor="w")
        badge = ctk.CTkLabel(
            sub, text=label, font=("Segoe UI", 9, "bold"), text_color=color,
            fg_color=CARD_ALT, corner_radius=6, width=44, height=18,
        )
        badge.pack(side="left")
        ctk.CTkLabel(sub, text=f"  {size_txt}", font=("Segoe UI", 10), text_color=TEXT_MUTED).pack(side="left")

        ctk.CTkButton(
            self,
            text="✕",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            hover_color="#3a2233",
            text_color=TEXT_MUTED,
            font=("Segoe UI", 12),
            command=lambda: on_remove(path),
        ).pack(side="right", padx=10)

    def _make_thumb(self, path, kind):
        size = (40, 40)
        if kind == "image":
            try:
                img = Image.open(path).convert("RGB")
                img.thumbnail(size)
                canvas = Image.new("RGB", size, (26, 28, 40))
                x = (size[0] - img.width) // 2
                y = (size[1] - img.height) // 2
                canvas.paste(img, (x, y))
                return ctk.CTkImage(light_image=canvas, dark_image=canvas, size=size)
            except Exception:
                pass

        emoji, _, color = KIND_LABELS.get(kind, ("📁", "?", TEXT_MUTED))
        canvas = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        from PIL import ImageDraw

        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle([0, 0, 199, 199], radius=40, fill=CARD_ALT)
        try:
            from PIL import ImageFont

            font = ImageFont.truetype("seguiemj.ttf", 90)
            draw.text((100, 100), emoji, font=font, anchor="mm", embedded_color=True)
        except Exception:
            draw.ellipse([60, 60, 140, 140], fill=color)
        return ctk.CTkImage(light_image=canvas, dark_image=canvas, size=size)


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, app_icon, lang, on_lang_change):
        super().__init__(master, fg_color=SIDEBAR, corner_radius=0, width=220)
        self.pack_propagate(False)
        self.lang = lang
        self.on_lang_change = on_lang_change

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(28, 20))

        header_row = ctk.CTkFrame(top, fg_color="transparent")
        header_row.pack(fill="x")
        if app_icon:
            ctk.CTkLabel(header_row, image=app_icon, text="").pack(side="left")

        lang_switch = ctk.CTkFrame(header_row, fg_color=CARD_ALT, corner_radius=8)
        lang_switch.pack(side="right", anchor="n")
        self.fr_btn = ctk.CTkButton(
            lang_switch, text="FR", width=34, height=26, corner_radius=6,
            font=("Segoe UI", 10, "bold"),
            fg_color=ACCENT_A if lang == "fr" else "transparent",
            text_color=TEXT if lang == "fr" else TEXT_MUTED,
            hover_color=ACCENT_HOVER,
            command=lambda: self.on_lang_change("fr"),
        )
        self.fr_btn.pack(side="left", padx=(3, 1), pady=3)
        self.en_btn = ctk.CTkButton(
            lang_switch, text="EN", width=34, height=26, corner_radius=6,
            font=("Segoe UI", 10, "bold"),
            fg_color=ACCENT_A if lang == "en" else "transparent",
            text_color=TEXT if lang == "en" else TEXT_MUTED,
            hover_color=ACCENT_HOVER,
            command=lambda: self.on_lang_change("en"),
        )
        self.en_btn.pack(side="left", padx=(1, 3), pady=3)

        ctk.CTkLabel(top, text=t(lang, "app_name"), font=("Segoe UI", 20, "bold"), text_color=TEXT).pack(
            anchor="w", pady=(14, 0)
        )
        ctk.CTkLabel(
            top, text=t(lang, "tagline"), font=("Segoe UI", 11), text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

        divider = ctk.CTkFrame(self, fg_color=BORDER, height=1)
        divider.pack(fill="x", padx=24, pady=18)

        formats_frame = ctk.CTkFrame(self, fg_color="transparent")
        formats_frame.pack(fill="x", padx=24)
        ctk.CTkLabel(
            formats_frame, text=t(lang, "formats_supported"), font=("Segoe UI", 10, "bold"), text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        for emoji, label in FORMAT_CHIPS.get(lang, FORMAT_CHIPS["en"]):
            row = ctk.CTkFrame(formats_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=emoji, font=("Segoe UI Emoji", 13)).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 11), text_color=TEXT_MUTED).pack(side="left")

        ctk.CTkLabel(
            self, text="v1.2", font=("Segoe UI", 10), text_color="#4a4d5c"
        ).pack(side="bottom", pady=16)


class App(BASE_CLASS):
    def __init__(self):
        super().__init__()
        self.title("UniConvert")
        self.geometry("980x680")
        self.minsize(860, 580)
        self.configure(bg=BG)

        self.lang = detect_default_lang()
        self.files = []
        self.out_dir = os.path.join(os.path.expanduser("~"), "Downloads")

        self._load_icon()
        self._build_ui()

        if DND_AVAILABLE:
            self.drop_zone.drop_target_register(DND_FILES)
            self.drop_zone.dnd_bind("<<Drop>>", self._on_drop)

    def _load_icon(self):
        self.app_icon_img = None
        png_path = os.path.join(ASSETS_DIR, "icon.png")
        ico_path = os.path.join(ASSETS_DIR, "icon.ico")
        if os.path.exists(png_path):
            pil_img = Image.open(png_path).convert("RGBA")
            small = pil_img.copy()
            small.thumbnail((40, 40))
            self.app_icon_img = ctk.CTkImage(light_image=small, dark_image=small, size=small.size)
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

    def _set_lang(self, lang):
        if lang == self.lang:
            return
        self.lang = lang
        for child in self.winfo_children():
            child.destroy()
        self._build_ui()
        if DND_AVAILABLE:
            self.drop_zone.drop_target_register(DND_FILES)
            self.drop_zone.dnd_bind("<<Drop>>", self._on_drop)
        self._refresh_list()
        self._refresh_formats()

    def _build_ui(self):
        L = self.lang
        root = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        root.pack(fill="both", expand=True)

        self.sidebar = Sidebar(root, self.app_icon_img, L, self._set_lang)
        self.sidebar.pack(side="left", fill="y")

        main = ctk.CTkFrame(root, fg_color=BG)
        main.pack(side="left", fill="both", expand=True)

        content = ctk.CTkFrame(main, fg_color=BG)
        content.pack(fill="both", expand=True, padx=32, pady=28)

        self.drop_zone = ctk.CTkFrame(
            content, height=130, corner_radius=18, fg_color=CARD, border_width=2, border_color=BORDER
        )
        self.drop_zone.pack(fill="x", pady=(0, 18))
        self.drop_zone.pack_propagate(False)

        drop_text = t(L, "drop_here") if DND_AVAILABLE else t(L, "browse_here")
        inner_drop = ctk.CTkFrame(self.drop_zone, fg_color="transparent")
        inner_drop.pack(expand=True)
        ctk.CTkLabel(inner_drop, text="⇪", font=("Segoe UI", 26), text_color=ACCENT_A).pack()
        self.drop_label = ctk.CTkLabel(inner_drop, text=drop_text, font=("Segoe UI", 14, "bold"), text_color=TEXT)
        self.drop_label.pack(pady=(4, 0))
        ctk.CTkLabel(
            inner_drop, text=t(L, "browse_hint"), font=("Segoe UI", 11), text_color=TEXT_MUTED
        ).pack()

        for w in (self.drop_zone, inner_drop, self.drop_label):
            w.bind("<Button-1>", lambda e: self._browse())
            w.bind("<Enter>", lambda e: self.drop_zone.configure(border_color=ACCENT_A))
            w.bind("<Leave>", lambda e: self.drop_zone.configure(border_color=BORDER))

        list_header = ctk.CTkFrame(content, fg_color="transparent")
        list_header.pack(fill="x", pady=(0, 8))
        self.count_label = ctk.CTkLabel(
            list_header, text=t(L, "no_file"), font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED
        )
        self.count_label.pack(side="left")
        ctk.CTkButton(
            list_header,
            text=t(L, "clear_all"),
            width=100,
            height=26,
            corner_radius=8,
            fg_color="transparent",
            hover_color=CARD_HOVER,
            text_color=TEXT_MUTED,
            font=("Segoe UI", 11),
            command=self._clear_files,
        ).pack(side="right")

        self.list_scroll = ctk.CTkScrollableFrame(content, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, pady=(0, 16))

        bottom = ctk.CTkFrame(content, fg_color=CARD, corner_radius=16)
        bottom.pack(fill="x")
        bottom_inner = ctk.CTkFrame(bottom, fg_color="transparent")
        bottom_inner.pack(fill="x", padx=20, pady=18)

        row1 = ctk.CTkFrame(bottom_inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(row1, text=t(L, "output_format"), font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(
            side="left"
        )
        self.format_var = tk.StringVar(value="-")
        self.format_menu = ctk.CTkOptionMenu(
            row1,
            variable=self.format_var,
            values=["-"],
            width=150,
            height=32,
            corner_radius=8,
            fg_color=ACCENT_A,
            button_color=ACCENT_A,
            button_hover_color=ACCENT_HOVER,
            dropdown_fg_color=CARD_ALT,
        )
        self.format_menu.pack(side="right")

        row2 = ctk.CTkFrame(bottom_inner, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 16))
        self.out_label = ctk.CTkLabel(
            row2, text=self._short_out_dir(), font=("Segoe UI", 11), text_color=TEXT_MUTED, anchor="w"
        )
        self.out_label.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            row2,
            text=t(L, "change"),
            width=100,
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
            bottom_inner,
            text=t(L, "convert"),
            height=46,
            corner_radius=12,
            font=("Segoe UI", 14, "bold"),
            fg_color=ACCENT_A,
            hover_color=ACCENT_HOVER,
            command=self._start_conversion,
        )
        self.convert_btn.pack(fill="x")

        self.progress = ctk.CTkProgressBar(bottom_inner, height=5, corner_radius=3, progress_color=ACCENT_B)
        self.status_label = ctk.CTkLabel(bottom_inner, text="", font=("Segoe UI", 11))
        self.status_label.pack(pady=(10, 0))

    def _short_out_dir(self):
        d = self.out_dir
        if len(d) > 60:
            d = "..." + d[-57:]
        return f"📁  {d}"

    def _on_drop(self, event):
        raw = self.tk.splitlist(event.data)
        self._add_files(raw)

    def _browse(self):
        paths = filedialog.askopenfilenames(title=t(self.lang, "choose_files_title"))
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
            self.count_label.configure(text=t(self.lang, "no_file"))
            placeholder = ctk.CTkLabel(
                self.list_scroll, text=t(self.lang, "empty_hint"),
                font=("Segoe UI", 11), text_color="#4a4d5c",
            )
            placeholder.pack(pady=30)
            return

        self.count_label.configure(text=t(self.lang, "file_count", n=len(self.files)))
        for f in self.files:
            kind = detect_kind(f)
            row = FileRow(self.list_scroll, f, kind, self._remove_file)
            row.pack(fill="x", pady=4)

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
            not_supported = t(self.lang, "not_supported")
            self.format_menu.configure(values=[not_supported])
            self.format_var.set(not_supported)

    def _choose_out_dir(self):
        d = filedialog.askdirectory(title=t(self.lang, "choose_dir_title"))
        if d:
            self.out_dir = d
            self.out_label.configure(text=self._short_out_dir())

    def _start_conversion(self):
        L = self.lang
        if not self.files:
            messagebox.showwarning("UniConvert", t(L, "warn_no_file"))
            return
        target = self.format_var.get()
        if not target or target in ("-", t(L, "not_supported")):
            messagebox.showwarning("UniConvert", t(L, "warn_no_format"))
            return

        self.convert_btn.configure(state="disabled", text=t(L, "converting"))
        self.status_label.configure(text="")
        self.progress.pack(fill="x", pady=(10, 0))
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
        L = self.lang
        self.progress.stop()
        self.progress.pack_forget()
        self.convert_btn.configure(state="normal", text=t(L, "convert"))
        self.status_label.configure(text=t(L, "success", n=len(results)), text_color=GREEN)
        messagebox.showinfo(t(L, "done_title"), t(L, "done_msg", n=len(results), dir=self.out_dir))

    def _on_error(self, exc):
        L = self.lang
        self.progress.stop()
        self.progress.pack_forget()
        self.convert_btn.configure(state="normal", text=t(L, "convert"))
        self.status_label.configure(text=t(L, "error"), text_color=RED)
        messagebox.showerror("UniConvert", str(exc))


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
