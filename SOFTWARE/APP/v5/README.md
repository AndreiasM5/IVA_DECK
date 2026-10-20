# IVA DECK V5

**Windows companion for your IVA DECK macro pad.** Purple and pink, nine programmable keys, three live rotary controls, and a simpler everyday workflow.

[Download Windows installer](https://github.com/AndreiasM5/IVA_DECK/releases/latest) · [Ghid în română](../../../docs/windows-app-v5.ro.md) · [GPLv3](LICENSE)

## Install and connect

1. In Releases, download **IVA-DECK-5.0.0-Setup-x64.exe** and run the installer. Python is included; no separate Python installation or administrator account is needed.
2. Pair **IVA_Deck_FINAL** in Windows Bluetooth settings, or connect USB.
3. Open **Conexiune**, refresh the ports and choose the matching Bluetooth outgoing serial port or USB port. COM numbers vary by computer.
4. Press a physical key. The status changes to **date primite** when data arrives.

Windows 10 21H2 or newer / Windows 11, x64. Bluetooth requires the serial service supported by the deck firmware. Close Arduino Serial Monitor or any other program using that port.

## Everyday controls

- **Taste & macro-uri:** animated potentiometers, assigned macro names, shortcuts and live key highlights. Click a key to change its assignment.
- **Bibliotecă macro:** add, capture, edit and remove a single simultaneous key combination or media command.
- **Volum:** select an audio target for each of the three hardware potentiometers. Refresh the list after starting playback in an application.
- **Dispozitiv:** live distance, validated buzzer controls and text LCD commands.
- **Conexiune:** Bluetooth at 9600 baud or USB at 115200 baud, with visible connection/data status.

Macro definitions, key assignments, audio targets and the last connected port are stored in **%APPDATA%\IVA DECK**. Updates and uninstall preserve them. Startup reopens the saved port if available. The app runs as a single instance; opening it again brings the existing window forward. Local diagnostics: `application.log` in that folder.

The app has no AI page, telemetry, activation or account requirement. SD-image workflows are deferred. The installer does not flash firmware. V4 remains in its original folder.

## Portable and source versions

The portable ZIP includes the executable and its `_internal` folder. Extract the entire archive and keep those files together; double click `IVA-DECK.exe`. Portable and installed copies use the same per-user data folder.

For development, use Python 3.12 x64 and install `requirements-build.txt` in a virtual environment, then run `iva_key_app/src/main.py`. First launch copies the bundled defaults to the data folder without overwriting existing configuration.

## Reproduce the Windows build

Install Python 3.12 x64 and Inno Setup 7 (Inno Setup 6 also supports this installer script). From this folder:

```powershell
py -3.12 -m venv .build-venv
.\build-windows.ps1 -Python .\.build-venv\Scripts\python.exe -InnoCompiler 'C:\Program Files\Inno Setup 7\ISCC.exe'
```

The build script pins Python package versions, collects dependency licenses, bundles the application with PyInstaller and creates an installer and portable ZIP in `release/`. Change `-InnoCompiler` to match your installation.

To exercise the executable without connecting hardware or executing OS shortcuts:

```powershell
.\dist\IVA-DECK\IVA-DECK.exe --smoke-test C:\Temp\iva-smoke
```

Check the process exit code and `smoke-result.json`. This writes only to the chosen test directory. The check covers nine keys, macro dispatch, proximity, three audio channels, knob animation, writable settings, five pages and a native screenshot. It does not replace testing with the physical deck or a separate clean Windows PC.

## License and release notes

V5 is free software under **GPL-3.0-only**, copyright © 2026 Ioan-Andrei Ivașcu. See LICENSE and THIRD_PARTY_NOTICES.md. This license applies to the V5 desktop application; other historical repository materials retain their existing status.

This first Windows release is **unsigned**. Windows may show an unknown publisher warning; verify the official repository and SHA-256 checksums in the release. Do not disable antivirus protection.
