# UniConvert

Petite application de bureau (Windows) pour convertir des fichiers sans passer par un site web ou une ligne de commande.

Glisse-dépose tes fichiers, choisis le format de sortie, clique sur Convertir. C'est tout.

## Formats supportes

| Depart | Vers |
|---|---|
| Images (png, jpg, bmp, gif, webp, ico) | png, jpg, bmp, gif, webp, ico, pdf |
| PDF | png, jpg, txt |
| Texte (.txt) | pdf |
| Word (.docx) | txt, pdf |
| CSV | json, xlsx |
| JSON | csv |
| Excel (.xlsx) | csv |

Plusieurs images peuvent aussi etre fusionnees en un seul PDF.

## Utilisation

```bash
pip install -r requirements.txt
python main.py
```

## Construire un .exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name UniConvert main.py
```

L'executable se trouve ensuite dans `dist/UniConvert.exe`.

## Stack

- Python 3.12
- customtkinter (interface)
- tkinterdnd2 (glisser-deposer)
- Pillow, PyMuPDF, pypdf, reportlab, python-docx, openpyxl (conversions)
