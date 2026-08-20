# UniConvert

Application de bureau (Windows) pour convertir des fichiers sans passer par un site web ou une ligne de commande.

Glisse-dépose tes fichiers, choisis le format de sortie, clique sur Convertir. C'est tout.

## Formats supportes

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

## Utilisation

```bash
pip install -r requirements.txt
python main.py
```

## Construire un .exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name UniConvert --paths src --hidden-import app --hidden-import converters --collect-all customtkinter --collect-all tkinterdnd2 main.py
```

L'executable se trouve ensuite dans `dist/UniConvert.exe`.

## Stack

- Python 3.12
- customtkinter (interface)
- tkinterdnd2 (glisser-deposer)
- Pillow, PyMuPDF, pypdf, reportlab, python-docx, openpyxl, markdown, pyyaml, xhtml2pdf (conversions)
- ffmpeg (audio/video, optionnel)
