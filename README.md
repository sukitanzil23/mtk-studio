# MTK Studio

A modern desktop GUI for MediaTek FRP bypass, built on Python + pywebview + mtkclient.

## Requirements

- Python 3.12.x
- Windows 10/11 recommended
- USB drivers: install via [Zadig](https://zadig.akeo.ie/) (select libusb-win32)

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Mock Mode

Enable **Settings > Mock Mode** to simulate a full FRP bypass without real hardware.
Ideal for development and UI testing. A fake MT6765 device is simulated with realistic log output.

## Build Standalone Executable

```bash
python build.py
```

Output: `dist/MTK Studio/MTK Studio.exe`

## Project Structure

| File | Purpose |
|------|---------|
| `main.py` | pywebview window entry point |
| `api.py` | Python API exposed to JS |
| `bridge.py` | Real mtkclient integration |
| `mock.py` | Mock bridge for testing |
| `config.py` | Settings (~/.mtk-studio/config.json) |
| `usb_monitor.py` | USB device polling |
| `build.py` | PyInstaller build script |
| `ui/` | Frontend (HTML/CSS/JS, Tailwind CDN) |

## Credits

- [mtkclient](https://github.com/bkerler/mtkclient) by B.Kerler -- GPLv3
- [pywebview](https://pywebview.flowrl.com/)
- UI: Tailwind CSS + Public Sans
