STRINGS = {
    "fr": {
        "app_name": "UniConvert",
        "tagline": "Convertisseur universel",
        "formats_supported": "FORMATS PRIS EN CHARGE",
        "drop_here": "Depose tes fichiers ici",
        "browse_here": "Clique pour choisir des fichiers",
        "browse_hint": "ou clique pour parcourir tes dossiers",
        "no_file": "Aucun fichier",
        "file_count": "{n} fichier(s)",
        "clear_all": "Tout effacer",
        "empty_hint": "Les fichiers ajoutes apparaitront ici",
        "output_format": "Format de sortie",
        "change": "Changer",
        "convert": "Convertir",
        "converting": "Conversion en cours...",
        "success": "✓  {n} fichier(s) converti(s) avec succes",
        "error": "✕  Echec de la conversion",
        "warn_no_file": "Ajoute au moins un fichier.",
        "warn_no_format": "Choisis un format de sortie valide.",
        "done_title": "UniConvert",
        "done_msg": "Termine ! {n} fichier(s) dans :\n{dir}",
        "choose_files_title": "Choisir des fichiers",
        "choose_dir_title": "Dossier de sortie",
        "not_supported": "non supporte",
    },
    "en": {
        "app_name": "UniConvert",
        "tagline": "Universal converter",
        "formats_supported": "SUPPORTED FORMATS",
        "drop_here": "Drop your files here",
        "browse_here": "Click to choose files",
        "browse_hint": "or click to browse your folders",
        "no_file": "No file",
        "file_count": "{n} file(s)",
        "clear_all": "Clear all",
        "empty_hint": "Added files will appear here",
        "output_format": "Output format",
        "change": "Change",
        "convert": "Convert",
        "converting": "Converting...",
        "success": "✓  {n} file(s) converted successfully",
        "error": "✕  Conversion failed",
        "warn_no_file": "Add at least one file.",
        "warn_no_format": "Choose a valid output format.",
        "done_title": "UniConvert",
        "done_msg": "Done! {n} file(s) in:\n{dir}",
        "choose_files_title": "Choose files",
        "choose_dir_title": "Output folder",
        "not_supported": "not supported",
    },
}

FORMAT_CHIPS = {
    "fr": [
        ("🖼", "Images"), ("📄", "PDF"), ("📃", "Word"), ("📘", "Markdown"),
        ("🌐", "HTML"), ("📊", "CSV / Excel"), ("🔣", "JSON / YAML"),
        ("🗜", "ZIP"), ("🎵", "Audio"), ("🎬", "Video"),
    ],
    "en": [
        ("🖼", "Images"), ("📄", "PDF"), ("📃", "Word"), ("📘", "Markdown"),
        ("🌐", "HTML"), ("📊", "CSV / Excel"), ("🔣", "JSON / YAML"),
        ("🗜", "ZIP"), ("🎵", "Audio"), ("🎬", "Video"),
    ],
}


def t(lang, key, **kwargs):
    text = STRINGS.get(lang, STRINGS["en"]).get(key, key)
    return text.format(**kwargs) if kwargs else text
