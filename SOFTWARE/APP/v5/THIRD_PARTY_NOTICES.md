# Third-party software

IVA DECK V5 is copyright © 2026 Ioan-Andrei Ivașcu, distributed under GPL-3.0-only; see LICENSE. This covers the V5 desktop application and its reused desktop code only. It does not relicense the hardware, firmware, thesis or other repository contents.

The Windows package includes Python and the runtime libraries from requirements-build.txt. Notices are copied to THIRD_PARTY_LICENSES in the application bundle.

| Component | License and upstream source |
| --- | --- |
| Python | PSF — https://www.python.org/downloads/source/ |
| PyQt6 | GPLv3 — https://www.riverbankcomputing.com/software/pyqt/download |
| Qt 6 | LGPLv3 / GPLv3 and module notices — https://download.qt.io/archive/qt/ |
| pyserial | BSD — https://github.com/pyserial/pyserial |
| pynput | LGPLv3 — https://github.com/moses-palmer/pynput |
| keyboard | MIT — https://github.com/boppreh/keyboard |
| pycaw | MIT — https://github.com/AndreMiras/pycaw |
| comtypes | MIT — https://github.com/enthought/comtypes |
| pywin32 | PSF-based — https://github.com/mhammond/pywin32 |
| psutil | BSD — https://github.com/giampaolo/psutil |
| six | MIT — https://github.com/benjaminp/six |
| PyInstaller bootloader | GPL with distribution exception — https://pyinstaller.org/en/stable/license.html |

Exact V5 source and build instructions accompany the release. Upstream sources for bundled versions are available through the linked projects and Python source distributions. Qt is dynamically linked in _internal/PyQt6/Qt6/bin; compatible replacement libraries can be used there. V5 requires no account, activation, license fee, telemetry or AI training.
