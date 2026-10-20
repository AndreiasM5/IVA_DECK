# IVA DECK V5 source

See [the V5 guide](../README.md) for installation, connections, user-data locations and build instructions.

Start with `src/main.py`. Runtime data is stored under `%APPDATA%\IVA DECK`, separately from this source tree and the installed files. To use isolated test data, set `IVA_DECK_DATA_DIR` before startup.

The V5 interface is `src/ui/main_window.py`; `device_backend.py` preserves the historical V4 macro/audio/device command implementation used by V5. V5 overrides event handling and uses the Qt event loop for UI updates. Assets are in `src/assets`.
