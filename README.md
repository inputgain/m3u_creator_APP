# M3U Creator App

Desktop app in Python to build `.m3u` playlists from drag-and-drop files/folders.

## Features

- Drag and drop files or folders.
- Recursive `.mp3` scan when a folder is dropped.
- Real-time editable preview list.
- Reorder items:
  - Drag-and-drop inside list with visual row highlight.
  - Move up/down buttons.
- Remove selected items.
- Toggle random order on/off.
- Larger drop zone integrated into preview area.
- Icon-labeled action buttons for quicker recognition.
- Save mode:
  - Manual location (file dialog).
  - USB root (auto-detected removable drives).
- Output with UTF-8 and overwrite confirmation.

## Install

```powershell
python -m pip install -r requirements.txt
```

## Run

```powershell
python app.py
```

## Notes

- The app currently includes only `.mp3` files.
- Playlist lines are normalized with `/`.
- If a track is outside the target `.m3u` directory tree, the app writes a path rooted from the drive root (without drive letter), to keep portable-style output.
