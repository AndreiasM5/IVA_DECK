# Getting started

[← Overview](../README.md)

The original application was developed with Python 3.10 and tested in the thesis on Windows 11. From the repository root:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r SOFTWARE/APP/v4/iva_key_app/requirements.txt
cd SOFTWARE/APP/v4/iva_key_app/src
..\..\..\..\..\.venv\Scripts\python.exe main.py
```

Run from `src` because the app resolves `settings.json` and `keybinds.json` relative to its working directory. No historical dependency lock file is available.

## Connection

1. Connect a compatible ESP32 by USB or pair its Bluetooth serial service in Windows.
2. Open **Setări**, choose its COM port, and select **Conectează USB** or **Conectează Bluetooth**.
3. Observe events in **Taste**, assign macros in **Keybinds**, and select audio targets in **Volum**.

The GUI opens **115200 baud for USB** and **9600 baud for Bluetooth serial**. Historical standalone tests can use different rates. Close Arduino Serial Monitor before opening the same COM port in the app.

| Page | Purpose |
| --- | --- |
| Taste | Nine-key live feedback |
| Volum | Three Windows audio controls |
| LCD | Display commands and SD files |
| Keybinds | Macro definitions and assignments |
| AI | Labeled event collection |
| Proximitate | Distance feedback |
| Buzz | Buzzer frequency and duration |
| Setări | Serial connection |

The voice module is experimental and disabled in the active GUI. Normal use does not require its optional dependencies.

## Data and troubleshooting

`src/keybinds.json` stores macro definitions and `src/settings.json` stores key assignments. `main.py` writes session logs in `SOFTWARE/APP/v4/`; the GUI may write `src/ai_labeled_data.csv`. Keep new interaction data local; generated logs and models are ignored by Git.

If a port cannot open, confirm the port and close other serial programs. If events do not appear, check compatible firmware and the [expected JSON fields](protocol.md). If audio sessions are missing, start the target app and play audio. The app depends on Windows COM libraries and is not currently cross-platform.

Scripts in `SOFTWARE/APP/tests/` use hardcoded development COM ports. Inspect them before running. Full device reproduction depends on the [firmware status](../SOFTWARE/DECK/v6_esp32/README.md).
