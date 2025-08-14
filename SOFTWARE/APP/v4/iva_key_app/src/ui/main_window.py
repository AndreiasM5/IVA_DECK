from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QListWidget, QStackedWidget, QHBoxLayout, QVBoxLayout, QPushButton, QGridLayout, QLineEdit, QFileDialog, QComboBox, QSlider, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsRectItem, QTextEdit
from PyQt6.QtGui import QPalette, QColor, QPen
from PyQt6.QtCore import Qt, QEvent, QTimer, pyqtSignal
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume
import comtypes
import json
import os
import threading
from pynput.keyboard import Controller
from serial_comm.serial_manager import get_serial_ports
import math
import sys
import os
import time  # pentru funcțiile de SD card
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Elimină importul direct pentru log_event, folosește import lazy la runtime
log_event = None

class MainWindow(QMainWindow):
    highlight_taste_btn = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("IVA Key App")
        self.setGeometry(100, 100, 1000, 600)

        self.set_dark_theme()
        self.setup_ui()
        self.serial_conn = None
        self.serial_running = False
        self.available_ports = {}
        self.update_serial_ports()
        self.serial_thread = None

        self.keyboard = Controller()
        self.keybinds = {}
        self.load_keybinds()

        self.highlight_taste_btn.connect(self._highlight_taste_btn)

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        self.menu = QListWidget()
        self.menu.addItems([
            # "Home",  # comentat temporar
            "Taste", "Volum", "LCD", "Keybinds",
            "AI",
            # "Recunoaștere vocală",  # comentat temporar
            "Proximitate", "Buzz", "Setări"])
        self.menu.setStyleSheet("""
            QListWidget {
                background-color: #2a2a3d;
                color: #ffffff;
                font-size: 16px;
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #d77aff;
                color: #000000;
            }
        """)
        self.menu.setFixedWidth(200)
        self.menu.currentRowChanged.connect(self.display_page)

        self.pages = QStackedWidget()
        # self.pages.addWidget(self.create_page("Home"))  # comentat temporar
        self.pages.addWidget(self.create_page("Taste"))
        self.pages.addWidget(self.create_page("Volum"))
        self.pages.addWidget(self.create_page("LCD"))
        self.pages.addWidget(self.create_page("Keybinds"))
        self.pages.addWidget(self.create_page("AI"))  # Adaugă pagina AI
        # self.pages.addWidget(self.create_page("Recunoaștere vocală"))  # comentat temporar
        self.pages.addWidget(self.create_page("Proximitate"))
        self.pages.addWidget(self.create_page("Buzz"))
        self.pages.addWidget(self.create_page("Setări"))

        main_layout.addWidget(self.menu)
        main_layout.addWidget(self.pages)

        self.setCentralWidget(main_widget)

    def create_page(self, name):
        page = QWidget()
        layout = QVBoxLayout()

        if name == "Taste":
            # Centrare completă grid (vertical și orizontal)
            outer_layout = QVBoxLayout()
            outer_layout.addStretch(1)
            hbox = QHBoxLayout()
            hbox.addStretch(1)
            self.taste_buttons = []
            grid = QGridLayout()
            grid.setSpacing(20)
            # Creează 9 butoane pentru taste, aranjate 3x3
            for i in range(9):
                btn = QPushButton(f"{i+1}")
                btn.setFixedSize(120, 80)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2a2a3d;
                        color: #ffffff;
                        font-size: 32px;
                        border-radius: 12px;
                        border: 2px solid #d77aff;
                        padding: 0px;
                        text-align: center;
                    }
                """)
                btn.installEventFilter(self)
                self.taste_buttons.append(btn)
                grid.addWidget(btn, i//3, i%3)
            hbox.addLayout(grid)
            hbox.addStretch(1)
            outer_layout.addLayout(hbox)
            outer_layout.addStretch(1)
            layout.addLayout(outer_layout)

        elif name == "Keybinds":
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.keybind_inputs = {}
            self.load_keybinds()
            # Macro UI
            macro_label = QLabel("Adaugă macro nou:")
            macro_label.setStyleSheet("color: #f5c2ff; font-size: 16px;")
            layout.addWidget(macro_label)
            macro_name_input = QLineEdit()
            macro_name_input.setPlaceholderText("Nume macro (ex: Copy)")
            macro_name_input.setStyleSheet("color: #ffffff; font-size: 13px; background-color: #2a2a3d; padding: 5px;")
            layout.addWidget(macro_name_input)
            macro_keys_input = QLineEdit()
            macro_keys_input.setPlaceholderText("Combinatie taste (ex: Ctrl+C)")
            macro_keys_input.setStyleSheet("color: #ffffff; font-size: 13px; background-color: #2a2a3d; padding: 5px;")
            layout.addWidget(macro_keys_input)
            record_btn = QPushButton("Înregistrează combinație")
            self._macro_recording_listener = None
            self._macro_recording_active = False
            def start_stop_capture():
                if not self._macro_recording_active:
                    macro_keys_input.setText("")
                    self._macro_recording_active = True
                    record_btn.setText("Oprește înregistrarea")
                    self.current_key_sequence = []
                    from pynput import keyboard
                    def on_press(key):
                        try:
                            k = key.char.upper()
                        except:
                            k = str(key).replace("Key.", "").upper()
                        if k not in self.current_key_sequence:
                            self.current_key_sequence.append(k)
                        combined = "+".join(self.current_key_sequence)
                        macro_keys_input.setText(combined)
                    def on_release(key):
                        if not self._macro_recording_active:
                            return False
                    self._macro_recording_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
                    self._macro_recording_listener.start()
                else:
                    self._macro_recording_active = False
                    record_btn.setText("Înregistrează combinație")
                    if self._macro_recording_listener:
                        self._macro_recording_listener.stop()
                        self._macro_recording_listener = None
            record_btn.clicked.connect(start_stop_capture)
            layout.addWidget(record_btn)
            add_macro_btn = QPushButton("Adaugă macro")
            def add_macro():
                name = macro_name_input.text().strip()
                keys = macro_keys_input.text().strip()
                if name and keys:
                    self.save_macro(name, keys)
                    macro_name_input.setText("")
                    macro_keys_input.setText("")
                    self.refresh_macro_list(layout)
                    self.refresh_macro_assign()
            add_macro_btn.clicked.connect(add_macro)
            layout.addWidget(add_macro_btn)
            # Listă macro-uri existente
            self.macro_list_label = QLabel()
            layout.addWidget(self.macro_list_label)
            self.refresh_macro_list(layout)
            # Dropdown asignare macro la taste
            self.taste_macro_map = self.load_taste_macro_map()
            self.macros = self.load_macros()
            self.macro_assign_combos = []
            assign_label = QLabel("Asignează macro la fiecare tastă:")
            assign_label.setStyleSheet("color: #f5c2ff; font-size: 15px; margin-top: 10px;")
            layout.addWidget(assign_label)
            for i in range(9):
                h = QHBoxLayout()
                key = f"T{i+1}"
                lbl = QLabel(f"Tasta {i+1}")
                lbl.setStyleSheet("color: #fff; font-size: 14px;")
                h.addWidget(lbl)
                macro_combo = QComboBox()
                macro_combo.addItem("--Niciun macro--")
                for macro_name in self.macros:
                    macro_combo.addItem(macro_name)
                # Preselectează dacă există mapping
                if key in self.taste_macro_map:
                    idx = macro_combo.findText(self.taste_macro_map[key])
                    if idx >= 0:
                        macro_combo.setCurrentIndex(idx)
                macro_combo.currentTextChanged.connect(lambda val, idx=i: self.save_taste_macro(idx, val))
                h.addWidget(macro_combo)
                self.macro_assign_combos.append(macro_combo)
                layout.addLayout(h)

            # === Editare/ștergere macro ===
            edit_label = QLabel("Editează sau șterge un macro existent:")
            edit_label.setStyleSheet("color: #f5c2ff; font-size: 15px; margin-top: 10px;")
            layout.addWidget(edit_label)
            self.edit_macro_combo = QComboBox()
            self.edit_macro_combo.addItem("--Selectează macro--")
            for macro_name in self.macros:
                self.edit_macro_combo.addItem(macro_name)
            layout.addWidget(self.edit_macro_combo)
            self.edit_macro_keys_input = QLineEdit()
            self.edit_macro_keys_input.setPlaceholderText("Combinatie taste nouă")
            self.edit_macro_keys_input.setStyleSheet("color: #ffffff; font-size: 13px; background-color: #2a2a3d; padding: 5px;")
            layout.addWidget(self.edit_macro_keys_input)
            def on_macro_select(name):
                if name in self.macros:
                    self.edit_macro_keys_input.setText(self.macros[name])
                else:
                    self.edit_macro_keys_input.setText("")
            self.edit_macro_combo.currentTextChanged.connect(on_macro_select)
            # Buton modificare
            update_btn = QPushButton("Modifică macro")
            def update_macro():
                name = self.edit_macro_combo.currentText()
                keys = self.edit_macro_keys_input.text().strip()
                if name in self.macros and keys:
                    self.save_macro(name, keys)
                    self.refresh_macro_list(layout)
                    self.refresh_macro_assign()
                    # Actualizează și QComboBox-ul de editare
                    self.edit_macro_combo.clear()
                    self.edit_macro_combo.addItem("--Selectează macro--")
                    for macro_name in self.macros:
                        self.edit_macro_combo.addItem(macro_name)
            update_btn.clicked.connect(update_macro)
            layout.addWidget(update_btn)
            # Buton ștergere
            delete_btn = QPushButton("Șterge macro")
            def delete_macro():
                name = self.edit_macro_combo.currentText()
                if name in self.macros:
                    # Șterge macro din fișier și din mapping
                    data = {}
                    if os.path.exists("keybinds.json"):
                        with open("keybinds.json", "r") as f:
                            data = json.load(f)
                    if "macros" in data and name in data["macros"]:
                        del data["macros"][name]
                        with open("keybinds.json", "w") as f:
                            json.dump(data, f, indent=4)
                    # Șterge din mapping taste
                    for k in list(self.taste_macro_map.keys()):
                        if self.taste_macro_map[k] == name:
                            self.taste_macro_map[k] = "--Niciun macro--"
                    self.save_taste_macro(0, self.taste_macro_map.get("T1", "--Niciun macro--"))  # forțează salvarea
                    self.refresh_macro_list(layout)
                    self.refresh_macro_assign()
                    self.edit_macro_combo.clear()
                    self.edit_macro_combo.addItem("--Selectează macro--")
                    self.edit_macro_keys_input.setText("")
                    for macro_name in self.macros:
                        self.edit_macro_combo.addItem(macro_name)
            delete_btn.clicked.connect(delete_macro)
            layout.addWidget(delete_btn)

        elif name == "Setări":
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            # === SERIAL CLASIC ===
            layout.addWidget(QLabel("Conectare prin cablu:"))
            self.port_selector_usb = QComboBox()
            layout.addWidget(self.port_selector_usb)

            usb_btn = QPushButton("Conectează USB")
            usb_btn.clicked.connect(lambda: self.reconecteaza_serial("usb"))
            layout.addWidget(usb_btn)

            # === BLUETOOTH ===
            layout.addWidget(QLabel("Conectare Bluetooth:"))
            self.port_selector_bt = QComboBox()
            layout.addWidget(self.port_selector_bt)

            bt_btn = QPushButton("Conectează Bluetooth")
            bt_btn.clicked.connect(lambda: self.reconecteaza_serial("bt"))
            layout.addWidget(bt_btn)

            # === Status conexiune ===
            self.status_label = QLabel("Nicio conexiune activă")
            self.status_label.setStyleSheet("color: #f5c2ff; font-size: 13px; margin-top: 10px;")
            layout.addWidget(self.status_label)

            self.update_serial_ports()

        elif name == "Volum":
            # Centrare completă pentru slidere
            outer_layout = QVBoxLayout()
            outer_layout.addStretch(1)
            hbox = QHBoxLayout()
            hbox.addStretch(1)
            self.volume_sliders = {}
            self.volume_combo = {}
            slider_names = [
                ("0", "#ffb700", "Volum 1"),
                ("1", "#00e1ff", "Volum 2"),
                ("2", "#d77aff", "Volum 3")
            ]
            app_list = self.get_audio_sessions_list()
            for i, (key, color, label) in enumerate(slider_names):
                vbox = QVBoxLayout()
                lbl = QLabel(label)
                lbl.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                vbox.addWidget(lbl)
                combo = QComboBox()
                combo.addItem("Master Volume")
                for app in app_list:
                    combo.addItem(app)
                self.volume_combo[key] = combo
                vbox.addWidget(combo)
                slider = QSlider(Qt.Orientation.Vertical)
                slider.setMinimum(0)
                slider.setMaximum(100)
                slider.setValue(0)
                slider.setFixedSize(90, 420)
                slider.setStyleSheet(f"""
                    QSlider::groove:vertical {{
                        background: #22223b;
                        border: 3px solid {color};
                        width: 48px;
                        border-radius: 24px;
                        margin: 0 0 0 0;
                    }}
                    QSlider::handle:vertical {{
                        background: {color};
                        border: 3px solid #fff;
                        height: 60px;
                        margin: 0 -22px;
                        border-radius: 30px;
                    }}
                """)
                slider.setEnabled(False)
                vbox.addWidget(slider)
                self.volume_sliders[key] = slider
                hbox.addLayout(vbox)
                if i < len(slider_names) - 1:
                    hbox.addSpacing(80)
            hbox.addStretch(1)
            outer_layout.addLayout(hbox)
            outer_layout.addStretch(1)
            layout.addLayout(outer_layout)

        elif name == "Proximitate":
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.proxy_distance_label = QLabel("Distanta: -- mm")
            self.proxy_distance_label.setStyleSheet("color: #00ff00; font-size: 32px; font-weight: bold;")
            self.proxy_distance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.proxy_distance_label)

        elif name == "Buzz":
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            freq_label = QLabel("Frecvență (Hz):")
            freq_label.setStyleSheet("color: #f5c2ff; font-size: 15px;")
            layout.addWidget(freq_label)
            self.buzz_freq = QLineEdit("1500")
            self.buzz_freq.setStyleSheet("color: #fff; background-color: #2a2a3d; font-size: 15px;")
            layout.addWidget(self.buzz_freq)
            dur_label = QLabel("Durată (ms):")
            dur_label.setStyleSheet("color: #f5c2ff; font-size: 15px;")
            layout.addWidget(dur_label)
            self.buzz_dur = QLineEdit("400")
            self.buzz_dur.setStyleSheet("color: #fff; background-color: #2a2a3d; font-size: 15px;")
            layout.addWidget(self.buzz_dur)
            buzz_btn = QPushButton("Sună buzzer")
            buzz_btn.setStyleSheet("font-size: 16px; background-color: #d77aff; color: #000; padding: 8px;")
            buzz_btn.clicked.connect(self.trimite_buzz)
            layout.addWidget(buzz_btn)
            self.buzz_status = QLabel("")
            self.buzz_status.setStyleSheet("color: #fff; font-size: 13px;")
            layout.addWidget(self.buzz_status)

        elif name == "LCD":
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            # Preview imagine
            self.lcd_image_label = QLabel("Preview imagine LCD")
            self.lcd_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lcd_image_label.setStyleSheet("border: 2px solid #d77aff; padding: 5px;")
            layout.addWidget(self.lcd_image_label)

            # Input text pentru LCD
            self.lcd_text_input = QLineEdit()
            self.lcd_text_input.setPlaceholderText("Text pentru LCD")
            self.lcd_text_input.setStyleSheet("color: #ffffff; font-size: 14px; background-color: #2a2a3d; padding: 5px;")
            layout.addWidget(self.lcd_text_input)

            # Buton pentru actualizare text LCD
            update_lcd_btn = QPushButton("Actualizează LCD")
            update_lcd_btn.setStyleSheet("font-size: 15px; background-color: #d77aff; color: #000; padding: 6px;")
            update_lcd_btn.clicked.connect(self.update_lcd_text)
            layout.addWidget(update_lcd_btn)

            # === Listare SD Card ===
            self.sd_list_btn = QPushButton("Listează SD Card")
            self.sd_list_btn.setStyleSheet("font-size: 15px; background-color: #d77aff; color: #000; padding: 6px;")
            self.sd_list_btn.clicked.connect(self.listeaza_sd_card)
            layout.addWidget(self.sd_list_btn)
            self.sd_files_combo = QComboBox()
            self.sd_files_combo.setStyleSheet("background-color: #2a2a3d; color: #fff; font-size: 14px;")
            layout.addWidget(self.sd_files_combo)
            self.display_sd_btn = QPushButton("Afișează pe LCD")
            self.display_sd_btn.setStyleSheet("font-size: 15px; background-color: #d77aff; color: #000; padding: 6px;")
            self.display_sd_btn.clicked.connect(self.afiseaza_sd_imagine)
            layout.addWidget(self.display_sd_btn)
            # --- RAW SD output area ---
            from PyQt6.QtWidgets import QTextEdit
            self.sd_raw_output = QTextEdit()
            self.sd_raw_output.setReadOnly(True)
            self.sd_raw_output.setStyleSheet("background-color: #181828; color: #aaffaa; font-size: 13px;")
            self.sd_raw_output.setPlaceholderText("[ESP] output live aici...")
            layout.addWidget(self.sd_raw_output)
            # ---
            self.lcd_status = QLabel("")
            self.lcd_status.setStyleSheet("color: #fff; font-size: 13px;")
            layout.addWidget(self.lcd_status)

        elif name == "AI":
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            # === UI pentru recunoaștere utilizator ===
            user_label = QLabel("Nume utilizator (pentru colectare date):")
            user_label.setStyleSheet("color: #f5c2ff; font-size: 15px;")
            layout.addWidget(user_label)
            self.ai_user_input = QLineEdit()
            self.ai_user_input.setPlaceholderText("ex: IVASCU")
            self.ai_user_input.setStyleSheet("color: #fff; background-color: #2a2a3d; font-size: 15px;")
            layout.addWidget(self.ai_user_input)
            set_user_btn = QPushButton("Setează utilizator")
            set_user_btn.setStyleSheet("font-size: 15px; background-color: #d77aff; color: #000; padding: 6px;")
            set_user_btn.clicked.connect(self.set_ai_user)
            layout.addWidget(set_user_btn)
            self.ai_user_status = QLabel("")
            self.ai_user_status.setStyleSheet("color: #fff; font-size: 13px;")
            layout.addWidget(self.ai_user_status)
            # Colectare date
            self.ai_collect_btn = QPushButton("Începe colectare date")
            self.ai_collect_btn.setStyleSheet("font-size: 15px; background-color: #d77aff; color: #000; padding: 6px;")
            self.ai_collect_btn.clicked.connect(self.toggle_ai_collect)
            layout.addWidget(self.ai_collect_btn)
            self.ai_collect_status = QLabel("")
            self.ai_collect_status.setStyleSheet("color: #fff; font-size: 13px;")
            layout.addWidget(self.ai_collect_status)
            # Antrenare model
            self.ai_train_btn = QPushButton("Antrenează modelul AI")
            self.ai_train_btn.setStyleSheet("font-size: 15px; background-color: #d77aff; color: #000; padding: 6px;")
            self.ai_train_btn.clicked.connect(self.train_ai_model)
            layout.addWidget(self.ai_train_btn)
            self.ai_train_status = QLabel("")
            self.ai_train_status.setStyleSheet("color: #fff; font-size: 13px;")
            layout.addWidget(self.ai_train_status)
            # Testare model
            self.ai_test_btn = QPushButton("Testează modelul pe sesiunea curentă")
            self.ai_test_btn.setStyleSheet("font-size: 15px; background-color: #d77aff; color: #000; padding: 6px;")
            self.ai_test_btn.clicked.connect(self.test_ai_model)
            layout.addWidget(self.ai_test_btn)
            self.ai_test_status = QLabel("")
            self.ai_test_status.setStyleSheet("color: #fff; font-size: 13px;")
            layout.addWidget(self.ai_test_status)

        else:
            # label = QLabel(name)
            # label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # label.setStyleSheet("font-size: 24px; color: #f5c2ff;")
            # layout.addWidget(label)
            pass  # comentat temporar

        page.setLayout(layout)
        return page

    def display_page(self, index):
        self.pages.setCurrentIndex(index)

    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e2f"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#121212"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1e1e1e"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#2a2a3d"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#f5c2ff"))
        palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff00ff"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#d77aff"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        self.setPalette(palette)

    def update_serial_ports(self):
        self.port_selector_usb.clear()
        self.port_selector_bt.clear()
        self.available_ports = {}

        ports = get_serial_ports()
        for port in ports:
            label = port["label"]
            device = port["device"]
            # Separă USB și Bluetooth după friendly name
            if "bluetooth" in label.lower():
                self.port_selector_bt.addItem(label)
            else:
                self.port_selector_usb.addItem(label)
            self.available_ports[label] = device

    def load_keybinds(self):
        if os.path.exists("keybinds.json"):
            with open("keybinds.json", "r") as f:
                self.keybinds = json.load(f)
        else:
            self.keybinds = {}

    def reconecteaza_serial(self, source):
        selector = self.port_selector_usb if source == "usb" else self.port_selector_bt
        selected_label = selector.currentText()
        port = self.available_ports.get(selected_label, selected_label)

        try:
            import serial
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_running = False
                self.serial_conn.close()

            baudrate = 9600 if source == "bt" else 115200
            self.serial_conn = serial.Serial(port, baudrate, timeout=1)
            self.serial_running = True
            self.serial_thread = threading.Thread(target=self.serial_listen_loop, daemon=True)
            self.serial_thread.start()

            self.status_label.setText(f"✅ Conectat: {selected_label}")
            print(f"[UART] Conectat la {port}")
        except Exception as e:
            self.status_label.setText(f"❌ Eroare la conectare: {e}")
            print(f"[UART] Eroare la conectare: {e}")

    def serial_listen_loop(self):
        import json
        while self.serial_running and self.serial_conn and self.serial_conn.is_open:
            try:
                line = self.serial_conn.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    print(f"[UART] Primit: {line}")
                    if line.startswith("{") and line.endswith("}"):
                        try:
                            data = json.loads(line)
                            self.handle_uart_message(data)
                        except Exception as e:
                            print(f"[UART] Eroare la parsare JSON: {e}")
                    else:
                        pass
            except Exception as e:
                print(f"[UART] Eroare la citire: {e}")

    def get_audio_sessions_list(self):
        sessions = AudioUtilities.GetAllSessions()
        app_names = set()
        for session in sessions:
            if session.Process and session.Process.name():
                app_names.add(session.Process.name())
        return sorted(app_names)

    def set_windows_volume(self, app_name, percent):
        if app_name == "Master Volume":
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
            volume = comtypes.cast(interface, comtypes.POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(percent/100, None)
        else:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.Process.name() == app_name:
                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    volume.SetMasterVolume(percent/100, None)

    def load_macros(self):
        if os.path.exists("keybinds.json"):
            with open("keybinds.json", "r") as f:
                data = json.load(f)
                return data.get("macros", {})
        return {}

    def save_macro(self, name, keys):
        data = {}
        if os.path.exists("keybinds.json"):
            with open("keybinds.json", "r") as f:
                data = json.load(f)
        if "macros" not in data:
            data["macros"] = {}
        data["macros"][name] = keys
        with open("keybinds.json", "w") as f:
            json.dump(data, f, indent=4)
        self.macros = data["macros"]

    def refresh_macro_list(self, layout):
        self.macros = self.load_macros()
        text = "<b>Macro-uri definite:</b><br>"
        for name, keys in self.macros.items():
            text += f"<span style='color:#d77aff'>{name}</span>: <span style='color:#fff'>{keys}</span><br>"
        self.macro_list_label.setText(text)

    def load_taste_macro_map(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                data = json.load(f)
                return data.get("taste_macro_map", {})
        return {}

    def save_taste_macro(self, idx, macro_name):
        key = f"T{idx+1}"
        self.taste_macro_map[key] = macro_name
        # Salvează în settings.json
        data = {}
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                data = json.load(f)
        data["taste_macro_map"] = self.taste_macro_map
        with open("settings.json", "w") as f:
            json.dump(data, f, indent=4)

    def activate_key_capture(self, line_edit):
        # Captură combinație taste cu pynput
        from pynput import keyboard
        self.current_key_sequence = []
        def on_press(key):
            try:
                k = key.char.upper()
            except:
                k = str(key).replace("Key.", "").upper()
            if k not in self.current_key_sequence:
                self.current_key_sequence.append(k)
            combined = "+".join(self.current_key_sequence)
            line_edit.setText(combined)
        def on_release(key):
            if key == keyboard.Key.enter:
                return False
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

    def simuleaza_macro(self, macro_name):
        macros = self.load_macros()
        if macro_name in macros:
            command_str = macros[macro_name]
            self.simuleaza_keybind(command_str)

    def refresh_macro_assign(self, layout=None):
        self.macros = self.load_macros()
        for i, combo in enumerate(self.macro_assign_combos):
            current = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("--Niciun macro--")
            for macro_name in self.macros:
                combo.addItem(macro_name)
            if current in self.macros or current == "--Niciun macro--":
                idx = combo.findText(current)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            combo.blockSignals(False)

    def simuleaza_keybind(self, command_str):
        try:
            import keyboard as kb  
        except ImportError:
            kb = None
        from pynput.keyboard import Key, Controller
        keyboard = self.keyboard if hasattr(self, 'keyboard') else Controller()
        key_map = {
            "CTRL": Key.ctrl,
            "SHIFT": Key.shift,
            "ALT": Key.alt,
            "CMD": Key.cmd,
            "WIN": Key.cmd,
            "ENTER": Key.enter,
            "ESC": Key.esc,
            "SPACE": Key.space,
            "TAB": Key.tab,
            "BACKSPACE": Key.backspace,
            "UP": Key.up,
            "DOWN": Key.down,
            "LEFT": Key.left,
            "RIGHT": Key.right,
            "MEDIA_PLAY_PAUSE": "play/pause media",
            "MEDIA_NEXT": "next track",
            "MEDIA_PREV": "previous track",
            "MEDIA_PREVIOUS": "previous track",
            "MEDIA_STOP": "stop media"
        }
        keys = [k.strip().upper() for k in command_str.split("+")]
        if kb and len(keys) == 1 and keys[0] in ["MEDIA_PLAY_PAUSE", "MEDIA_NEXT", "MEDIA_PREV", "MEDIA_PREVIOUS", "MEDIA_STOP"]:
            try:
                kb.send(key_map[keys[0]])
                return
            except Exception as e:
                print(f"[Keybind] Eroare la simulare media: {e}")
        parsed_keys = [key_map.get(k, k.lower()) for k in keys]
        try:
            for k in parsed_keys:
                keyboard.press(k)
            for k in reversed(parsed_keys):
                keyboard.release(k)
        except Exception as e:
            print(f"[Keybind] Eroare la simulare: {e}")

    def handle_uart_message(self, data):
        global log_event
        if log_event is None:
            try:
                from main import log_event as _log_event
                log_event = _log_event
            except Exception:
                log_event = lambda x: None
        log_event(f"UART: {data}")
        # === AI: colectare date etichetate ===
        if hasattr(self, 'ai_collecting') and self.ai_collecting and hasattr(self, 'current_ai_user'):
            if data.get("type") == "key" and data.get("key") == "pressed":
                import datetime
                # Salvează: timestamp, tasta, user_label
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                value = str(data.get("value"))
                ai_row = {
                    "timestamp": ts,
                    "tasta": value,
                    "user": self.current_ai_user
                }
                # Scrie în fișier CSV (append)
                try:
                    with open("ai_labeled_data.csv", "a", encoding="utf-8") as f:
                        if f.tell() == 0:
                            f.write("timestamp,tasta,user\n")
                        f.write(f"{ts},{value},{self.current_ai_user}\n")
                except Exception as e:
                    if hasattr(self, 'ai_collect_status'):
                        self.ai_collect_status.setText(f"Eroare la scriere date AI: {e}")
        key_map = {
            "49": 3,  # tasta 3
            "50": 2,  # tasta 2
            "51": 1,  # tasta 1
            "52": 6,  # tasta 6
            "53": 5,  # tasta 5
            "54": 4,  # tasta 4
            "55": 9,  # tasta 9
            "56": 8,  # tasta 8
            "57": 7,  # tasta 7
        }
        if data.get("type") == "key" and data.get("key") == "pressed":
            value = str(data.get("value"))
            idx = key_map.get(value)
            if idx and hasattr(self, "taste_buttons"):
                self.highlight_taste_btn.emit(idx-1)
                key = f"T{idx}"
                macro_name = self.taste_macro_map.get(key)
                if macro_name and macro_name != "--Niciun macro--":
                    self.simuleaza_macro(macro_name)
        if data.get("type") == "volume":
            key = str(data.get("key", ""))
            value = data.get("value", 0)
            if hasattr(self, "volume_sliders") and key in self.volume_sliders:
                percent = max(0, min(100, int(((4095 - value) / 4095) * 100)))
                self.volume_sliders[key].setValue(percent)
                if key in self.volume_combo:
                    app_name = self.volume_combo[key].currentText()
                    self.set_windows_volume(app_name, percent)
        if data.get("type") == "proxy" and data.get("key") == "distance":
            value = data.get("value", 0)
            if hasattr(self, "proxy_distance_label"):
                if value <= 30:
                    color = QColor(0, 255, 0)
                elif value >= 80:
                    color = QColor(255, 0, 0)
                else:
                    ratio = (value-30)/50
                    r = int(0 + ratio*(255-0))
                    g = int(255 - ratio*(255-0))
                    color = QColor(r, g, 0)
                self.proxy_distance_label.setText(f"Distanta: {value} mm")
                self.proxy_distance_label.setStyleSheet(f"color: {color.name()}; font-size: 32px; font-weight: bold;")

    def _highlight_taste_btn(self, idx):
        for btn in self.taste_buttons:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a3d;
                    color: #ffffff;
                    font-size: 32px;
                    border-radius: 12px;
                    border: 2px solid #d77aff;
                    padding: 0px;
                    text-align: center;
                }
            """)
        btn = self.taste_buttons[idx]
        btn.setStyleSheet("""
            QPushButton {
                background-color: #d77aff;
                color: #000000;
                font-size: 32px;
                border-radius: 12px;
                border: 2px solid #d77aff;
                padding: 0px;
                text-align: center;
            }
        """)
        QTimer.singleShot(500, lambda: self._reset_taste_btn(idx))

    def _reset_taste_btn(self, idx):
        btn = self.taste_buttons[idx]
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a3d;
                color: #ffffff;
                font-size: 32px;
                border-radius: 12px;
                border: 2px solid #d77aff;
                padding: 0px;
                text-align: center;
            }
        """)

    def eventFilter(self, obj, event):
        # Ignoră click-urile pe taste
        if hasattr(self, "taste_buttons") and obj in self.taste_buttons:
            if event.type() in [QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease, QEvent.Type.MouseButtonDblClick]:
                return True
        return super().eventFilter(obj, event)


    def update_lcd_text(self):
        if not (self.serial_conn and self.serial_conn.is_open):
            self.lcd_status.setText("❌ Serială neconectată!")
            return
        text = self.lcd_text_input.text().strip()
        if not text:
            self.lcd_status.setText("Introduceti textul pentru LCD!")
            return
        try:
            cmd = {"cmd": "display_text", "text": text}
            self.serial_conn.write((json.dumps(cmd) + "\n").encode())
            self.lcd_status.setText(f"Text trimis către LCD: {text}")
        except Exception as e:
            self.lcd_status.setText(f"Eroare: {e}")

    def trimite_buzz(self):
        try:
            freq = int(self.buzz_freq.text())
            dur = int(self.buzz_dur.text())
            cmd = {"cmd": "buzz", "freq": freq, "duration": dur}
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.write((json.dumps(cmd) + "\n").encode())
                self.buzz_status.setText(f"Comandă trimisă: {cmd}")
            else:
                self.buzz_status.setText("Serială neconectată!")
        except Exception as e:
            self.buzz_status.setText(f"Eroare: {e}")

    def listeaza_sd_card(self):
        import re
        if not (self.serial_conn and self.serial_conn.is_open):
            self.lcd_status.setText("Serială neconectată!")
            if hasattr(self, 'sd_raw_output'):
                self.sd_raw_output.append("[EROARE] Serială neconectată!")
            return
        try:
            self.sd_files_combo.clear()
            self.lcd_status.setText("Aștept răspuns de la ESP32...")
            if hasattr(self, 'sd_raw_output'):
                self.sd_raw_output.clear()
                self.sd_raw_output.append("[TX] Trimis: {\"cmd\":\"list_sd\"}")
                self.sd_raw_output.append("[RX] Aștept fișiere...")
            self.serial_conn.reset_input_buffer()
            self.serial_conn.write(b'{"cmd":"list_sd"}\n')
            files = set()
            start = time.time()
            while True:
                line = self.serial_conn.readline().decode(errors="ignore").strip()
                if line:
                    if hasattr(self, 'sd_raw_output'):
                        self.sd_raw_output.append(f"[ESP] {line}")
                    # Adaugă orice linie care pare fișier imagine
                    if re.search(r"\.(raw|bmp|jpg|jpeg|png)$", line, re.IGNORECASE):
                        files.add(line)
                # Oprește dacă nu mai primești nimic 0.5s sau dacă ai depășit 5s
                if time.time() - start > 5:
                    break
                if not line:
                    idle = 0.5
                    t_idle = time.time()
                    while not line and time.time() - t_idle < idle:
                        line = self.serial_conn.readline().decode(errors="ignore").strip()
                        if line:
                            if hasattr(self, 'sd_raw_output'):
                                self.sd_raw_output.append(f"[ESP] {line}")
                            if re.search(r"\.(raw|bmp|jpg|jpeg|png)$", line, re.IGNORECASE):
                                files.add(line)
                            t_idle = time.time()  # reset idle dacă vine ceva
                    if time.time() - t_idle >= idle:
                        break
            if files:
                self.sd_files_combo.addItems(sorted(files))
                self.lcd_status.setText(f"{len(files)} fișiere imagine găsite pe SD.")
            else:
                self.lcd_status.setText("Niciun fișier imagine găsit sau timeout.")
        except Exception as e:
            self.lcd_status.setText(f"Eroare: {e}")
            if hasattr(self, 'sd_raw_output'):
                self.sd_raw_output.append(f"[EROARE] {e}")

    def afiseaza_sd_imagine(self):
        if not (self.serial_conn and self.serial_conn.is_open):
            self.lcd_status.setText("Serială neconectată!")
            return
        # Permite introducere manuală a numelui fișierului
        filename = self.lcd_text_input.text().strip()
        if not filename:
            self.lcd_status.setText("Introdu numele fișierului!")
            return
        try:
            cmd = {"cmd": "display_raw", "filename": filename}
            self.serial_conn.write((json.dumps(cmd) + "\n").encode())
            self.lcd_status.setText(f"Comandă trimisă pentru {filename}")
        except Exception as e:
            self.lcd_status.setText(f"Eroare: {e}")

    def set_ai_user(self):
        user = self.ai_user_input.text().strip()
        if user:
            self.current_ai_user = user
            self.ai_user_status.setText(f"Utilizator setat: <b>{user}</b>")
        else:
            self.ai_user_status.setText("Introduceți un nume valid!")

    def toggle_ai_collect(self):
        # Placeholder pentru logica de colectare date
        if not hasattr(self, 'ai_collecting') or not self.ai_collecting:
            self.ai_collecting = True
            self.ai_collect_btn.setText("Oprește colectarea")
            self.ai_collect_status.setText("Colectare date activă. Apasă tastele pentru a salva acțiuni cu label.")
        else:
            self.ai_collecting = False
            self.ai_collect_btn.setText("Începe colectare date")
            self.ai_collect_status.setText("Colectare oprită.")

    def train_ai_model(self):
        # Placeholder pentru antrenare model
        self.ai_train_status.setText("(WIP) Modelul va fi antrenat aici pe datele colectate.")

    def test_ai_model(self):
        # Placeholder pentru testare model
        self.ai_test_status.setText("(WIP) Modelul va face predicție pe ultimele acțiuni din sesiune.")