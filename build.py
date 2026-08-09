"""Build script for M3U Creator App."""
import re
import subprocess
import sys


def get_version():
    with open("app.py", encoding="utf-8") as f:
        match = re.search(r'__version__\s*=\s*"([^"]+)"', f.read())
        if not match:
            raise SystemExit("No se pudo leer __version__ de app.py")
        return match.group(1)


def generate_version_info(version):
    major, minor, patch = version.split(".")
    return f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, 0),
    prodvers=({major}, {minor}, {patch}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [StringTable(
        u'080904b0',
        [StringStruct(u'CompanyName', u'inputgain'),
         StringStruct(u'FileDescription', u'M3U Creator App'),
         StringStruct(u'FileVersion', u'{version}'),
         StringStruct(u'InternalName', u'm3u_creator'),
         StringStruct(u'OriginalFilename', u'M3U Creator App.exe'),
         StringStruct(u'ProductName', u'M3U Creator App'),
         StringStruct(u'ProductVersion', u'{version}'),
         StringStruct(u'LegalCopyright', u'Copyright (c) 2026 inputgain'),
         StringStruct(u'LegalTrademarks', u'MIT License')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [2057, 1200])])
  ]
)
"""


def main():
    version = get_version()
    print(f"Building M3U Creator App v{version}...")

    version_info = generate_version_info(version)
    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write(version_info)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--icon=assets\\app_icon.ico",
        "--name", f"M3U Creator App v{version}",
        "--hidden-import", "tkinterdnd2",
        "--add-data", "assets;assets",
        "--collect-all", "tkinterdnd2",
        "--version-file", "version_info.txt",
        "app.py"
    ]

    subprocess.run(cmd, check=True)
    print(f"\nBuild completado: dist\\M3U Creator App v{version}.exe")


if __name__ == "__main__":
    main()
