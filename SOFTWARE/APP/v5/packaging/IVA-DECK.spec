from pathlib import Path
base=Path(SPECPATH).parent
src=base/'iva_key_app'/'src'
a=Analysis([str(src/'main.py')], pathex=[str(src)], binaries=[],
 datas=[(str(src/'assets'),'assets'),(str(src/'settings.json'),'.'),(str(src/'keybinds.json'),'.'),(str(base/'LICENSE'),'.'),(str(base/'THIRD_PARTY_NOTICES.md'),'.'),(str(base/'build'/'licenses'),'THIRD_PARTY_LICENSES')],
 hiddenimports=['pynput.keyboard._win32','pynput.mouse._win32','pynput._util.win32','win32timezone','PyQt6.QtTest'],
 hookspath=[],hooksconfig={},runtime_hooks=[],excludes=['tkinter','matplotlib','numpy','scipy','pandas','IPython','pytest'],noarchive=False)
# Qt uses the ICU and UCRT provided by supported Windows versions.
# Build-tool PATH entries may contain incompatible ICU DLLs with the same names.
a.binaries = [entry for entry in a.binaries if not (
    Path(entry[0]).name.lower() in {'icuuc.dll', 'icuin.dll', 'ucrtbase.dll'} or
    Path(entry[0]).name.lower().startswith(('icudt', 'api-ms-win-')))]
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='IVA-DECK',debug=False,bootloader_ignore_signals=False,strip=False,upx=False,console=False,icon=str(src/'assets'/'iva-deck.ico'),version=str(base/'packaging'/'version_info.txt'))
coll=COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='IVA-DECK')
