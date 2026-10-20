"""Writable per-user data, separate from installed application resources."""
import json
import os
import shutil
from pathlib import Path

VERSION = '5.0.0'
RESOURCE_DIR = Path(__file__).resolve().parent

def data_dir():
    override = os.environ.get('IVA_DECK_DATA_DIR')
    if override:
        return Path(override).resolve()
    return Path(os.environ.get('APPDATA', str(Path.home()))) / 'IVA DECK'

def prepare_data():
    directory = data_dir()
    directory.mkdir(parents=True, exist_ok=True)
    for name in ('settings.json', 'keybinds.json'):
        target = directory / name
        if not target.exists():
            shutil.copyfile(RESOURCE_DIR / name, target)
        try:
            json.loads(target.read_text(encoding='utf-8-sig'))
        except (ValueError, UnicodeError):
            # Keep the damaged file for recovery rather than deleting user data.
            import datetime
            backup = target.with_name(name + '.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.bak')
            target.replace(backup)
            shutil.copyfile(RESOURCE_DIR / name, target)
    return directory
