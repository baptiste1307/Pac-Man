# Packaging Guide — Pac-Man

This guide documents the procedures for compiling and packaging **Pac-Man** into standalone executable distributions for **macOS** and **Linux** using [PyInstaller](https://pyinstaller.org/) and [uv](https://docs.astral.sh/uv/).

---

## Important Build Rules

- **Platform-native compilation**: PyInstaller must be run on the target operating system (build the macOS `.app` bundle on macOS, and the Linux executable on Linux). Cross-compilation is not supported by PyInstaller.
- **Dependencies**: Ensure dependencies are synced with `uv sync` before building.

---

## macOS Build (`PacMan.app` & `PacMan-mac.zip`)

Run these commands on **macOS**:

### 1. Clean previous build artifacts
```bash
rm -rf build dist PacMan.spec
```

### 2. Build the macOS application bundle
```bash
uv run pyinstaller \
  --windowed \
  --icon=img/app_icon_42.icns \
  --name PacMan \
  --hidden-import mazegenerator \
  --hidden-import mazegenerator.mazegenerator \
  --add-data "config.json:." \
  --add-data "img:img" \
  --add-data "sounds:sounds" \
  --add-data "fonts:fonts" \
  --add-data "assets:assets" \
  package_entry.py
```

### 3. Create a distributable ZIP archive
```bash
cd dist
ditto -c -k --sequesterRsrc --keepParent PacMan.app PacMan-mac.zip
cd ..
```
*(The release-ready archive will be available at `dist/PacMan-mac.zip`).*

### 4. Test the packaged app
```bash
open dist/PacMan-mac.zip
```

---

## Linux Build (`PacMan-linux.zip`)

Run these commands on **Linux**:

### 1. Clean previous build artifacts
```bash
rm -rf build dist PacMan.spec
```

### 2. Build the Linux binary
```bash
uv run pyinstaller \
  --windowed \
  --icon=img/app_icon_42.png \
  --name PacMan \
  --hidden-import mazegenerator \
  --hidden-import mazegenerator.mazegenerator \
  --add-data "config.json:." \
  --add-data "img:img" \
  --add-data "sounds:sounds" \
  --add-data "fonts:fonts" \
  --add-data "assets:assets" \
  package_entry.py
```

### 3. Move external assets
Ensure runtime resources are located in the application directory:
```bash
cp -r assets fonts img sounds dist/PacMan/
```

### 4. Create the distributable ZIP archive
```bash
cd dist
zip -qr PacMan-linux.zip PacMan
cd ..
```
*(The release-ready archive will be available at `dist/PacMan-linux.zip`).*

### 5. Test the executable
```bash
cd dist/PacMan
./PacMan
```
