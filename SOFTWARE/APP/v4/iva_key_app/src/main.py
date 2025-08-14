from PyQt6.QtWidgets import QApplication
import sys
from ui.main_window import MainWindow
import atexit
import datetime
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), '../../session_log.txt')
CURRENT_SESSION_FILE = os.path.join(os.path.dirname(__file__), '../../current_session_log.txt')

with open(CURRENT_SESSION_FILE, 'w', encoding='utf-8') as f:
    f.write("")

session_start_time = datetime.datetime.now()
with open(LOG_FILE, 'a', encoding='utf-8') as f:
    f.write(f"\n=== SESSION START: {session_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
with open(CURRENT_SESSION_FILE, 'a', encoding='utf-8') as f:
    f.write(f"\n=== SESSION START: {session_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

def log_event(event):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    line = f"[{timestamp}] {event}\n"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line)
    with open(CURRENT_SESSION_FILE, 'a', encoding='utf-8') as f:
        f.write(line)

def end_session():
    session_end_time = datetime.datetime.now()
    end_line = f"=== SESSION END: {session_end_time.strftime('%Y-%m-%d %H:%M:%S')} ===\n"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(end_line)
    with open(CURRENT_SESSION_FILE, 'a', encoding='utf-8') as f:
        f.write(end_line)

atexit.register(end_session)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()