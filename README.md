# UniConvert

**[Français](#français) | [English](#english)**

---

## Français

Application de bureau (Windows) pour convertir des fichiers sans passer par un site web ou une ligne de commande.

Glisse-dépose tes fichiers, choisis le format de sortie, clique sur Convertir. C'est tout.

### Formats pris en charge

| Depart | Vers |
|---|---|
| Images (png, jpg, bmp, gif, webp, ico) | png, jpg, bmp, gif, webp, ico, pdf, zip |
| PDF | png, jpg, txt, pdf (fusion) |
| Texte (.txt) | pdf, zip |
| Word (.docx) | txt, pdf |
| Markdown (.md) | html, pdf, txt |
| HTML | pdf, txt |
| CSV | json, xlsx |
| JSON | csv, yaml |
| YAML | json |
| Excel (.xlsx) | csv |
| ZIP | extraction |
| Audio (mp3, wav, ogg, m4a, flac...) | mp3, wav, ogg, m4a, flac |
| Video (mp4, avi, mkv, webm...) | mp4, avi, mkv, webm, mp3, wav |

Plusieurs images peuvent etre fusionnees en un seul PDF. Plusieurs PDF peuvent etre fusionnes en un seul. N'importe quel groupe de fichiers peut etre compresse en ZIP.

La conversion audio/video necessite ffmpeg installe et present dans le PATH.

### Utilisation

```bash
pip install -r requirements.txt
python main.py
```

### Construire un .exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name UniConvert --paths src --hidden-import app --hidden-import converters --collect-all customtkinter --collect-all tkinterdnd2 main.py
```

L'executable se trouve ensuite dans `dist/UniConvert.exe`.

### Stack

- Python 3.12
- customtkinter (interface)
- tkinterdnd2 (glisser-deposer)
- Pillow, PyMuPDF, pypdf, reportlab, python-docx, openpyxl, markdown, pyyaml, xhtml2pdf (conversions)
- ffmpeg (audio/video, optionnel)

---

## English

Desktop app (Windows) to convert files without going through a website or a command line.

Drag and drop your files, pick the output format, click Convert. That's it.

### Supported formats

| From | To |
|---|---|
| Images (png, jpg, bmp, gif, webp, ico) | png, jpg, bmp, gif, webp, ico, pdf, zip |
| PDF | png, jpg, txt, pdf (merge) |
| Text (.txt) | pdf, zip |
| Word (.docx) | txt, pdf |
| Markdown (.md) | html, pdf, txt |
| HTML | pdf, txt |
| CSV | json, xlsx |
| JSON | csv, yaml |
| YAML | json |
| Excel (.xlsx) | csv |
| ZIP | extraction |
| Audio (mp3, wav, ogg, m4a, flac...) | mp3, wav, ogg, m4a, flac |
| Video (mp4, avi, mkv, webm...) | mp4, avi, mkv, webm, mp3, wav |

Multiple images can be merged into a single PDF. Multiple PDFs can be merged into one. Any group of files can be zipped.

Audio/video conversion requires ffmpeg installed and available in PATH.

### Usage

```bash
pip install -r requirements.txt
python main.py
```

### Building a .exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name UniConvert --paths src --hidden-import app --hidden-import converters --collect-all customtkinter --collect-all tkinterdnd2 main.py
```

The executable will be in `dist/UniConvert.exe`.

### Stack

- Python 3.12
- customtkinter (UI)
- tkinterdnd2 (drag and drop)
- Pillow, PyMuPDF, pypdf, reportlab, python-docx, openpyxl, markdown, pyyaml, xhtml2pdf (conversions)
- ffmpeg (audio/video, optional)
