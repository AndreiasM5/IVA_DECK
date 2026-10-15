# IVA Key App

Windows companion for IVA DECK, built with Python / PyQt6.

[Overview](../../../../README.md) · [Setup guide](../../../../docs/getting-started.md) · [Protocol](../../../../docs/protocol.md)

Create `.venv` at the repository root, install `requirements.txt`, and launch `src/main.py` with `src` as the working directory. The setup guide provides the complete commands. USB uses 115200 baud and Bluetooth serial uses 9600.

| File | Role |
| --- | --- |
| `src/main.py` | Qt entry point and session logging |
| `src/ui/main_window.py` | Active GUI, events, macros, and Windows audio |
| `src/serial_comm/serial_manager.py` | Serial-port discovery |
| `src/keybinds.json` | Macro definitions |
| `src/settings.json` | Key assignments |
| `src/voice/` | Experimental module; GUI page disabled |

The AI CLI is in the parent directory, with `requirements-ai.txt`. Optional voice packages are in `requirements-voice.txt`. The normal install list excludes standard-library `json` and includes the Windows COM dependencies used by the source. Versions were not historically pinned; full integration has not been retested.
