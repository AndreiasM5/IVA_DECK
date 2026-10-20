from importlib import metadata
from pathlib import Path
import shutil
import sys
packages = ['PyQt6','PyQt6-Qt6','PyQt6_sip','pyserial','pynput','keyboard','pycaw','comtypes','pywin32','psutil','six','pyinstaller','pyinstaller-hooks-contrib','altgraph','packaging','pefile','pywin32-ctypes']
destination=Path(sys.argv[1]); destination.mkdir(parents=True,exist_ok=True)
for package in packages:
    dist=metadata.distribution(package)
    for relative in dist.files or []:
        if Path(str(relative)).name.lower().startswith(('license','copying','copyright','notice')):
            source=Path(dist.locate_file(relative))
            if source.is_file():
                target=destination/package/str(relative).replace('../','')
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source,target)
    (destination/(package+'-metadata.txt')).write_text((dist.read_text('METADATA') or ''),encoding='utf-8')
for base in [Path(sys.base_prefix),Path(sys.base_prefix).parent]:
    for name in ['LICENSE.txt','LICENSE']:
        if (base/name).is_file(): shutil.copyfile(base/name,destination/'PYTHON-LICENSE.txt')
