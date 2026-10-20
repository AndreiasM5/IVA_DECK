# Release validation — V5.0.0

Built on Windows 11 x64 with official CPython 3.12.10 x64, PyInstaller 6.22.3 and Inno Setup 7.1.0. Python dependencies are pinned in requirements-build.txt.

Passed locally:

- Frozen executable starts without launching an installed Python interpreter.
- Nine-key event decoding and macro dispatch, without executing OS shortcuts in the automated check.
- Three volume channels, proximity updates, animated knob rotation, configuration writes and five-page navigation.
- Native Windows rendering and application icon.
- Installer completes; installed executable passes the same checks.
- Reinstallation completes and preserves user configuration.
- Uninstaller completes and preserves external user configuration.
- Portable archive extracts and passes the same executable checks.
- Second launch exits and activates the existing instance.

USB/Bluetooth behavior reuses the device protocol tested during V4/V5 development. Automated packaging checks do not send device commands or flash firmware. Validation on another clean Windows PC remains outstanding. The installer is unsigned.

To repeat executable checks:

```powershell
.\dist\IVA-DECK\IVA-DECK.exe --smoke-test C:\Temp\iva-smoke
```

The process must exit with code 0 and create smoke-result.json in that directory. This check uses isolated configuration and does not open a device port or send keyboard shortcuts to Windows.
