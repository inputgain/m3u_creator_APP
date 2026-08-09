# Contributing

## Stack

- Python 3.12+ single-file Tkinter app (`app.py`)
- `tkinterdnd2` for drag-and-drop

## Development Setup

1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Run the app:

```powershell
python app.py
```

## Build Executable

```powershell
py build.py
```

The script reads `__version__` from `app.py` and generates the .exe with embedded version info.

Output: `dist\M3U Creator App v{version}.exe`

## Code Notes

- App only scans `.mp3` files
- Playlist output uses forward slashes (`/`) regardless of OS
- Bilingual support: `LANG` dict, `_toggle_language()` swaps language

## Git

- Main branch with remote on GitHub
- Tags for versioned releases (e.g. `v1.4.0`)
- No CI, linting, type-checking, or test config
