import argparse
import ctypes
import hashlib
import json
import os
import sys
import traceback
from pathlib import Path
from app_paths import VERSION, prepare_data


def smoke_test(window, output):
    """Exercise the frozen build without opening ports or sending OS shortcuts."""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtTest import QTest
    checks = []
    window.simuleaza_macro = lambda name: checks.append('macro:' + name)
    window.set_windows_volume = lambda *args: None
    assert len(window.taste_buttons) == 9
    window.handle_uart_message({'type': 'key', 'key': 'pressed', 'value': 53})
    assert window.press_count == 1
    window.handle_uart_message({'type': 'proxy', 'key': 'distance', 'value': 75})
    assert '75' in window.proxy_distance_label.text()
    for key, raw, expected in [('0', 4095, 0), ('1', 2048, 50), ('2', 0, 100)]:
        window.handle_uart_message({'type': 'volume', 'key': key, 'value': raw})
        assert window.potentiometers[key].value == expected
    window.handle_uart_message({'type': 'volume', 'key': '0', 'value': 2048})
    QTest.qWait(150)
    assert abs(window.potentiometers['0'].position - 50) < 0.1
    window.save_preference('release_smoke_test', True)
    assert window.read_preferences()['release_smoke_test'] is True
    for index in range(5):
        window.navigate(index)
        QApplication.processEvents()
        assert window.pages.currentIndex() == index
    window.navigate(0)
    window.resize(1180, 810)
    window._reset_taste_btn(4)
    QApplication.processEvents()
    window.grab().save(str(output / 'screenshot.png'))
    report = {'version': VERSION, 'frozen': bool(getattr(sys, 'frozen', False)),
              'checks': ['9 keys', 'macro dispatch', 'proximity', '3 audio channels',
                         'knob animation', 'settings write', '5 pages', 'icon and screenshot'],
              'dispatched': checks}
    (output / 'smoke-result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    window.close()


def main():
    parser = argparse.ArgumentParser(description='IVA DECK desktop companion')
    parser.add_argument('--version', action='version', version=VERSION)
    parser.add_argument('--bluetooth', help='Optional Bluetooth COM port')
    parser.add_argument('--smoke-test', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.smoke_test:
        args.smoke_test = args.smoke_test.resolve()
        os.environ['IVA_DECK_DATA_DIR'] = str(args.smoke_test)
    directory = prepare_data()
    os.chdir(directory)
    # Windowed executables have no console; keep diagnostics available locally.
    log_stream = open(directory / 'application.log', 'a', encoding='utf-8', buffering=1)
    sys.stdout = sys.stderr = log_stream
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtNetwork import QLocalServer, QLocalSocket
    from ui.main_window import MainWindow
    if sys.platform == 'win32':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('IVA.DECK.V5')
    app = QApplication(sys.argv[:1])
    app.setApplicationName('IVA DECK')
    app.setApplicationVersion(VERSION)
    server = None
    if not args.smoke_test:
        instance_name = 'IVA-DECK-V5-' + hashlib.sha256(str(directory).encode()).hexdigest()[:16]
        probe = QLocalSocket()
        probe.connectToServer(instance_name)
        if probe.waitForConnected(300):
            probe.disconnectFromServer()
            return 0
        server = QLocalServer()
        if not server.listen(instance_name):
            QLocalServer.removeServer(instance_name)
            server.listen(instance_name)
    window = MainWindow()
    def show_error(exc_type, value, tb):
        traceback.print_exception(exc_type, value, tb, file=log_stream)
        if args.smoke_test:
            app.exit(1)
        else:
            QMessageBox.critical(window, 'IVA DECK', f'A apărut o eroare. Detalii în {directory / "application.log"}')
    sys.excepthook = show_error
    if server:
        def activate():
            client = server.nextPendingConnection()
            if client: client.deleteLater()
            window.showNormal()
            window.raise_()
            window.activateWindow()
        server.newConnection.connect(activate)
    window.show()
    if args.smoke_test:
        try:
            smoke_test(window, args.smoke_test)
            return 0
        except Exception:
            traceback.print_exc(file=log_stream)
            return 1
    if args.bluetooth:
        def connect():
            index = window.port_selector_bt.findData(args.bluetooth)
            if index >= 0:
                window.port_selector_bt.setCurrentIndex(index)
                window.reconecteaza_serial('bt')
        QTimer.singleShot(300, connect)
    else:
        QTimer.singleShot(300, window.reconnect_saved)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
