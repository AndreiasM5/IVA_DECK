import json
import math
import time
from pathlib import Path
import serial
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QVariantAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIntValidator, QIcon, QPainter, QColor, QPen
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QComboBox, QLineEdit, QSlider,
    QStackedWidget, QScrollArea, QDialog, QDialogButtonBox, QMessageBox, QKeySequenceEdit)
from PyQt6.QtWidgets import QSizePolicy
from pynput.keyboard import Controller
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import comtypes
from .device_backend import MainWindow as DeviceBackend

STYLE = '''
QWidget { background: #15121e; color: #eee9f6; font-family: 'Segoe UI'; font-size: 14px; }
QFrame#sidebar { background: #1c1728; border-right: 1px solid #30263e; }
QLabel { background: transparent; }
QLabel#brand { font-size: 25px; font-weight: 800; color: #f2d6ff; }
QLabel#muted { color: #a99bb8; }
QLabel#title { font-size: 30px; font-weight: 700; }
QLabel#section { font-size: 18px; font-weight: 600; }
QLabel#eyebrow { color: #cc9cff; font-size: 11px; font-weight: 700; }
QLabel#badge { color: #dfb6fb; background: #30213f; border-radius: 12px; padding: 7px 12px; }
QFrame#card { background: #211a2d; border: 1px solid #372a47; border-radius: 16px; }
QFrame#bar { background: #211a2d; border: 1px solid #372a47; border-radius: 12px; }
QPushButton { background: #30253f; border: 1px solid #493657; border-radius: 9px; padding: 10px 16px; font-weight: 600; }
QPushButton:hover { background: #453055; border-color: #b77de0; }
QPushButton:pressed { background: #624076; }
QPushButton:disabled { color: #73667f; border-color: #30283a; background: #241e2e; }
QPushButton#primary { background: #ca96f4; color: #22132f; border: 0; }
QPushButton#primary:hover { background: #e4b3ff; }
QPushButton#nav { text-align: left; border: 0; background: transparent; padding: 13px 16px; color: #b9abc8; }
QPushButton#nav:checked { color: #f5d9ff; background: #39254d; border-left: 3px solid #e6a5e1; }
QPushButton#key { background: #2b2139; border: 1px solid #614175; border-bottom: 4px solid #493052; font-size: 15px; text-align: left; padding: 18px; }
QPushButton#key:hover { background: #3a294a; border-color: #d4a0f6; }
QPushButton#key[active="true"] { background: #d49bf0; color: #24132d; border-color: #fac2e4; }
QLineEdit, QComboBox, QKeySequenceEdit { background: #181320; border: 1px solid #493657; border-radius: 8px; padding: 10px; min-height: 22px; }
QLineEdit:focus, QComboBox:focus, QKeySequenceEdit:focus { border-color: #d29cf4; }
QComboBox::drop-down { border: 0; width: 24px; }
QComboBox QAbstractItemView { background: #2b2139; selection-background-color: #614175; padding: 6px; }
QScrollArea { border: 0; background: transparent; }
QScrollBar:vertical { background: #1b1625; width: 8px; }
QScrollBar::handle:vertical { background: #614175; min-height: 30px; border-radius: 4px; }
QSlider::groove:horizontal { height: 7px; background: #382944; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #c790eb; border-radius: 3px; }
QSlider::handle:horizontal { background: #f2c0e6; width: 18px; margin: -6px 0; border-radius: 9px; }
'''

class PotentiometerView(QWidget):
    """Read-only animated view of the physical potentiometer."""
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.value = None
        self.position = 0.0
        self.setFixedSize(100, 100)
        self.setToolTip('Se actualizează când rotești potențiometrul fizic.')
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(110)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.valueChanged.connect(self.animate_position)

    def animate_position(self, value):
        self.position = float(value)
        self.update()

    def set_value(self, value):
        self.animation.stop()
        first = self.value is None
        self.value = value
        if value is None:
            self.update()
            return
        if first:
            self.position = float(value)
            self.update()
        else:
            self.animation.setStartValue(self.position)
            self.animation.setEndValue(float(value))
            self.animation.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        arc = QRectF(9, 9, 82, 82)
        pen = QPen(QColor('#44334f'), 5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(arc, 225*16, -270*16)
        if self.value is not None:
            pen.setColor(self.color)
            p.setPen(pen)
            p.drawArc(arc, 225*16, int(-270*16*self.position/100))
        p.setPen(QPen(QColor('#634576'), 1))
        p.setBrush(QColor('#30203e'))
        p.drawEllipse(QRectF(20, 20, 60, 60))
        if self.value is not None:
            angle = math.radians(135+270*self.position/100)
            p.setPen(QPen(self.color, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(QPointF(50+22*math.cos(angle), 50+22*math.sin(angle)),
                       QPointF(50+27*math.cos(angle), 50+27*math.sin(angle)))
        p.setPen(QColor('#f5e8fb'))
        p.setFont(QFont('Segoe UI', 11, QFont.Weight.DemiBold))
        p.drawText(QRectF(20, 34, 60, 32), Qt.AlignmentFlag.AlignCenter,
                   '—' if self.value is None else f'{self.value}%')
        p.end()

class MainWindow(DeviceBackend):
    KEY_MAP = {'49': 3, '50': 2, '51': 1, '52': 6, '53': 5, '54': 4, '55': 9, '56': 8, '57': 7}

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('IVA DECK · V5.0.0')
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parents[1] / 'assets' / 'iva-deck.ico')))
        self.resize(1180, 810)
        self.setMinimumSize(1000, 720)
        QApplication.instance().setFont(QFont('Segoe UI', 10))
        self.setStyleSheet(STYLE)
        self.closing = False
        self.preferences = self.read_preferences()
        self.keyboard = Controller()
        self.macros = self.load_macros()
        self.taste_macro_map = self.load_taste_macro_map()
        self.serial_conn = None
        self.available_ports = {}
        self.receive_buffer = bytearray()
        self.press_count = 0
        self.last_event = 'Apasă o tastă pe dispozitiv pentru a vedea activitatea.'
        self.last_rx = None
        self.device_controls = []
        self.setup_ui()
        self.update_serial_ports()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_serial)
        self.timer.start(25)
        self.health_timer = QTimer(self)
        self.health_timer.timeout.connect(self.update_health)
        self.health_timer.start(1000)
        self.update_health()
        self.navigate(0)

    def label(self, text, role=None):
        w = QLabel(text)
        w.setTextFormat(Qt.TextFormat.PlainText)
        if role: w.setObjectName(role)
        w.setWordWrap(True)
        return w

    def button(self, text, callback, primary=False):
        w = QPushButton(text)
        if primary: w.setObjectName('primary')
        w.clicked.connect(callback)
        w.setCursor(Qt.CursorShape.PointingHandCursor)
        return w

    def card(self, title=None, subtitle=None):
        frame = QFrame()
        frame.setObjectName('card')
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)
        if title: layout.addWidget(self.label(title, 'section'))
        if subtitle: layout.addWidget(self.label(subtitle, 'muted'))
        return frame, layout

    def setup_ui(self):
        root = QWidget()
        row = QHBoxLayout(root)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        side = QFrame()
        side.setObjectName('sidebar')
        side.setFixedWidth(210)
        nav = QVBoxLayout(side)
        nav.setContentsMargins(20, 30, 20, 24)
        nav.setSpacing(8)
        nav.addWidget(self.label('IVA DECK', 'brand'))

        nav.addSpacing(34)
        self.nav_buttons = []
        self.page_info = [
            ('Taste & macro-uri', '', ''),
            ('Bibliotecă macro', 'Bibliotecă macro', 'Creează combinații și atribuie-le tastelor din spațiul de lucru.'),
            ('Volum', 'Sunetul, la îndemână', 'Alege ce controlează fiecare potențiometru.'),
            ('Dispozitiv', 'Mai mult decât taste', ''),
            ('Conexiune', 'Conectează-ți deck-ul', '')]
        for i, (name, _, _) in enumerate(self.page_info):
            btn = self.button(name.replace('&', '&&'), lambda checked=False, n=i: self.navigate(n))
            btn.setObjectName('nav')
            btn.setCheckable(True)
            nav.addWidget(btn)
            self.nav_buttons.append(btn)
        nav.addStretch()
        nav.addWidget(self.label('V5  /  PERSONAL MACRO PAD', 'eyebrow'))

        row.addWidget(side)
        body = QVBoxLayout()
        body.setContentsMargins(30, 18, 30, 24)
        body.setSpacing(14)
        top = QHBoxLayout()

        top.addStretch()
        self.connection_badge = self.label('Deconectat', 'badge')
        self.connection_badge.setWordWrap(False)
        top.addWidget(self.connection_badge)
        body.addLayout(top)
        self.page_title = self.label('', 'title')
        self.page_subtitle = self.label('', 'muted')
        body.addWidget(self.page_title)
        body.addWidget(self.page_subtitle)
        self.pages = QStackedWidget()
        self.pages.addWidget(self.build_keys())
        self.pages.addWidget(self.build_library())
        self.pages.addWidget(self.build_volume())
        self.pages.addWidget(self.build_device())
        self.pages.addWidget(self.build_connection())
        body.addWidget(self.pages, 1)
        bar = QFrame()
        bar.setObjectName('bar')
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(15, 10, 15, 10)
        self.activity_label = self.label(self.last_event, 'muted')
        bl.addWidget(self.activity_label, 1)
        bl.addWidget(self.button('Conexiune', lambda: self.navigate(4)))
        body.addWidget(bar)
        row.addLayout(body, 1)
        self.setCentralWidget(root)

    def navigate(self, index):
        self.pages.setCurrentIndex(index)
        self.page_title.setText(self.page_info[index][1])
        self.page_title.setVisible(bool(self.page_info[index][1]))
        self.page_subtitle.setText(self.page_info[index][2])
        self.page_subtitle.setVisible(bool(self.page_info[index][2]))
        for i, btn in enumerate(self.nav_buttons): btn.setChecked(i == index)
        if index == 1: self.refresh_library()
        if index == 4: self.update_serial_ports()

    def build_keys(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        knobs_row = QHBoxLayout()
        knobs_row.setSpacing(14)
        self.potentiometers = {}
        self.knob_targets = {}
        for i, color in enumerate(['#c696f5', '#f0a1d3', '#d9bcff']):
            key = str(i)
            card, column = self.card()
            column.setContentsMargins(12, 10, 16, 10)
            row = QHBoxLayout()
            knob = PotentiometerView(color)
            self.potentiometers[key] = knob
            row.addWidget(knob)
            info = QVBoxLayout()
            info.setSpacing(6)
            info.addWidget(self.label(f'POTENȚIOMETRU {i+1}', 'eyebrow'))
            target = self.label('Master Volume', 'muted')
            target.setToolTip('Ținta se configurează în tabul Volum.')
            self.knob_targets[key] = target
            info.addWidget(target)
            info.addStretch()
            row.addLayout(info, 1)
            column.addLayout(row)
            knobs_row.addWidget(card, 1)
        layout.addLayout(knobs_row)
        frame, contents = self.card(None, 'Click pe o tastă pentru a schimba macro-ul. Apăsările fizice se aprind aici.')
        grid = QGridLayout()
        grid.setSpacing(14)
        self.taste_buttons = []
        for i in range(9):
            btn = self.button('', lambda checked=False, n=i: self.edit_assignment(n))
            btn.setObjectName('key')
            btn.setMinimumHeight(108)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setProperty('active', False)
            grid.addWidget(btn, i // 3, i % 3)
            self.taste_buttons.append(btn)
        for n in range(3):
            grid.setRowStretch(n, 1)
            grid.setColumnStretch(n, 1)
        contents.addLayout(grid, 1)
        layout.addWidget(frame, 1)
        self.key_summary = self.label('', 'muted')
        layout.addWidget(self.key_summary)
        self.refresh_keys()
        return page

    def refresh_keys(self):
        for i, btn in enumerate(self.taste_buttons):
            name = self.taste_macro_map.get(f'T{i+1}', '')
            assigned = name in self.macros
            btn.setText(f'{i+1:02d}     {name if assigned else "Alege un macro"}\n\n{self.macros.get(name, "Click pentru configurare")}')
            btn.setToolTip(f'Tasta {i+1} · {name if assigned else "Fără macro"}')
        count = sum(name in self.macros for name in self.taste_macro_map.values())
        self.key_summary.setText(f'{count}/9 taste configurate   ·   Salvare automată   ·   {self.press_count} apăsări în această sesiune')

    def edit_assignment(self, index):
        dlg = QDialog(self)
        dlg.setWindowTitle(f'Configurează tasta {index+1}')
        dlg.setMinimumWidth(420)
        layout = QVBoxLayout(dlg)
        layout.addWidget(self.label(f'Tasta {index+1}', 'section'))
        layout.addWidget(self.label('Alege acțiunea pe care vrei să o execuți.', 'muted'))
        combo = QComboBox()
        combo.addItem('Fără macro', '--Niciun macro--')
        for name in self.macros: combo.addItem(f'{name}  ·  {self.macros[name]}', name)
        combo.setCurrentIndex(max(0, combo.findData(self.taste_macro_map.get(f'T{index+1}'))))
        layout.addWidget(combo)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText('Salvează')
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText('Renunță')
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)
        if dlg.exec():
            self.save_taste_macro(index, combo.currentData())
            self.refresh_keys()

    def build_library(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        top = QHBoxLayout()
        top.addStretch()
        top.addWidget(self.button('+  Macro nou', lambda: self.edit_macro(), True))
        layout.addLayout(top)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        host = QWidget()
        self.library_layout = QVBoxLayout(host)
        self.library_layout.setContentsMargins(0, 8, 8, 0)
        self.library_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(host)
        layout.addWidget(scroll)
        return page

    def refresh_library(self):
        while self.library_layout.count():
            item = self.library_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for name, keys in self.macros.items():
            card, col = self.card()
            row = QHBoxLayout()
            info = QVBoxLayout()
            info.addWidget(self.label(name, 'section'))
            info.addWidget(self.label(keys, 'muted'))
            row.addLayout(info, 1)
            row.addWidget(self.button('Editează', lambda checked=False, n=name: self.edit_macro(n)))
            row.addWidget(self.button('Șterge', lambda checked=False, n=name: self.delete_macro(n)))
            col.addLayout(row)
            self.library_layout.addWidget(card)

    def edit_macro(self, original=None):
        dlg = QDialog(self)
        dlg.setWindowTitle('Editează macro' if original else 'Macro nou')
        dlg.setMinimumWidth(470)
        layout = QVBoxLayout(dlg)
        layout.addWidget(self.label('Nume macro', 'muted'))
        name = QLineEdit(original or '')
        name.setPlaceholderText('Ex.: Copiază')
        layout.addWidget(name)
        layout.addWidget(self.label('Combinație de taste', 'muted'))
        keys = QLineEdit(self.macros.get(original, ''))
        keys.setPlaceholderText('Ctrl+C sau MEDIA_PLAY_PAUSE')
        layout.addWidget(keys)
        layout.addWidget(self.label('Sau apasă combinația în câmpul de mai jos:', 'muted'))
        recorder = QKeySequenceEdit()
        recorder.keySequenceChanged.connect(lambda seq: keys.setText(seq.toString()))
        layout.addWidget(recorder)
        hint = self.label('Media: MEDIA_PLAY_PAUSE · MEDIA_NEXT · MEDIA_PREVIOUS', 'muted')
        layout.addWidget(hint)
        error = self.label('')
        layout.addWidget(error)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText('Salvează macro')
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText('Renunță')
        def save():
            n, k = name.text().strip(), keys.text().strip()
            if not n or not k:
                error.setText('Completează numele și combinația.'); return
            if n != original and n in self.macros:
                error.setText('Există deja un macro cu acest nume.'); return
            if ',' in k:
                error.setText('Folosește o singură combinație, de exemplu Ctrl+Shift+S.'); return
            if original and original != n:
                del self.macros[original]
                for key in self.taste_macro_map:
                    if self.taste_macro_map[key] == original: self.taste_macro_map[key] = n
            self.macros[n] = k
            self.write_macros()
            self.persist_assignments()
            dlg.accept()
        buttons.accepted.connect(save)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)
        if dlg.exec():
            self.refresh_library()
            self.refresh_keys()

    def load_macros(self):
        path = Path('keybinds.json')
        return json.loads(path.read_text(encoding='utf-8')).get('macros', {}) if path.exists() else {}

    def load_taste_macro_map(self):
        path = Path('settings.json')
        return json.loads(path.read_text(encoding='utf-8')).get('taste_macro_map', {}) if path.exists() else {}

    def write_macros(self):
        path = Path('keybinds.json')
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        data['macros'] = self.macros
        temp = path.with_suffix('.json.tmp')
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding='utf-8')
        temp.replace(path)

    def persist_assignments(self):
        path = Path('settings.json')
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        data['taste_macro_map'] = self.taste_macro_map
        temp = path.with_suffix('.json.tmp')
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding='utf-8')
        temp.replace(path)

    def save_taste_macro(self, index, name):
        self.taste_macro_map[f'T{index+1}'] = name
        self.persist_assignments()

    def delete_macro(self, name):
        reply = QMessageBox.question(self, 'Șterge macro', f'Ștergi „{name}”? Tastele care îl folosesc vor rămâne fără macro.')
        if reply != QMessageBox.StandardButton.Yes: return
        del self.macros[name]
        self.taste_macro_map = {k: ('--Niciun macro--' if v == name else v) for k, v in self.taste_macro_map.items()}
        self.write_macros()
        self.persist_assignments()
        self.refresh_library()
        self.refresh_keys()

    def build_volume(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        self.volume_sliders, self.volume_combo = {}, {}
        try: apps = self.get_audio_sessions_list()
        except Exception: apps = []
        for i in range(3):
            key = str(i)
            card, col = self.card(f'Potențiometru {i+1}')
            combo = QComboBox()
            combo.addItems(['Master Volume'] + apps)
            combo.setToolTip('Aplicația al cărei volum este controlat de acest potențiometru')
            self.volume_combo[key] = combo
            saved_target = self.preferences.get('audio_targets', {}).get(key, 'Master Volume')
            if combo.findText(saved_target) < 0: combo.addItem(saved_target)
            combo.setCurrentText(saved_target)
            self.knob_targets[key].setText(saved_target)
            combo.currentTextChanged.connect(lambda text, k=key: self.audio_target_changed(k, text))
            col.addWidget(combo)
            line = QHBoxLayout()
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            slider.setEnabled(False)
            value = self.label('— %', 'section')
            slider.valueChanged.connect(lambda n, label=value: label.setText(f'{n} %'))
            line.addWidget(slider, 1)
            line.addWidget(value)
            col.addLayout(line)
            self.volume_sliders[key] = slider
            layout.addWidget(card)
        layout.addWidget(self.button('Reîmprospătează aplicațiile audio', self.refresh_audio))
        layout.addStretch()
        return page

    def read_preferences(self):
        path = Path('settings.json')
        return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {}

    def save_preference(self, key, value):
        data = self.read_preferences()
        data[key] = value
        path = Path('settings.json')
        temp = path.with_suffix('.json.tmp')
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding='utf-8')
        temp.replace(path)
        self.preferences = data

    def audio_target_changed(self, key, text):
        self.knob_targets[key].setText(text)
        targets = dict(self.preferences.get('audio_targets', {}))
        targets[key] = text
        self.save_preference('audio_targets', targets)

    def reconnect_saved(self):
        saved = self.preferences.get('connection', {})
        source = saved.get('source')
        if source not in ('bt', 'usb'): return
        selector = self.port_selector_bt if source == 'bt' else self.port_selector_usb
        index = selector.findData(saved.get('port'))
        if index >= 0:
            selector.setCurrentIndex(index)
            self.reconecteaza_serial(source)

    def refresh_audio(self):
        try: apps = self.get_audio_sessions_list()
        except Exception as exc:
            self.activity_label.setText(f'Nu pot citi aplicațiile audio: {exc}'); return
        for combo in self.volume_combo.values():
            old = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(['Master Volume'] + apps)
            if combo.findText(old) < 0: combo.addItem(old)
            combo.setCurrentText(old)
            combo.blockSignals(False)

    def build_device(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 8, 0)
        card, col = self.card('Proximitate', 'Distanța măsurată de senzor, în timp real.')
        self.proxy_distance_label = self.label('Distanță: — mm', 'title')
        col.addWidget(self.proxy_distance_label)
        layout.addWidget(card)
        card, col = self.card('Buzzer', 'Un sunet scurt pentru feedback.')
        row = QHBoxLayout()
        self.buzz_freq = QLineEdit('1500')
        self.buzz_freq.setValidator(QIntValidator(20, 20000, self))
        self.buzz_dur = QLineEdit('400')
        self.buzz_dur.setValidator(QIntValidator(1, 5000, self))
        for title, field in [('Frecvență · Hz', self.buzz_freq), ('Durată · ms', self.buzz_dur)]:
            column = QVBoxLayout()
            column.addWidget(self.label(title, 'muted'))
            column.addWidget(field)
            row.addLayout(column)
        col.addLayout(row)
        buzz = self.button('Redă sunet', self.send_buzz, True)
        col.addWidget(buzz)
        self.device_controls.append(buzz)
        self.buzz_status = self.label('', 'muted')
        col.addWidget(self.buzz_status)
        layout.addWidget(card)
        card, col = self.card('Afișaj LCD', 'Textul poate fi trimis direct. Imaginile de pe SD vor fi revizuite ulterior.')
        self.lcd_text_input = QLineEdit()
        self.lcd_text_input.setPlaceholderText('Scrie un mesaj pentru deck…')
        col.addWidget(self.lcd_text_input)
        send = self.button('Trimite text', self.update_lcd_text)
        col.addWidget(send)
        self.device_controls.append(send)
        self.lcd_status = self.label('', 'muted')
        col.addWidget(self.lcd_status)
        layout.addWidget(card)
        layout.addStretch()
        scroll.setWidget(host)
        return scroll

    def send_buzz(self):
        if not self.buzz_freq.hasAcceptableInput() or not self.buzz_dur.hasAcceptableInput():
            self.buzz_status.setText('Alege 20–20000 Hz și o durată de 1–5000 ms.'); return
        self.trimite_buzz()

    def build_connection(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        card, col = self.card('Bluetooth', 'Asociază IVA_Deck_FINAL în Windows, apoi alege portul serial de ieșire.')
        self.port_selector_bt = QComboBox()
        col.addWidget(self.port_selector_bt)
        col.addWidget(self.button('Conectează Bluetooth', lambda: self.reconecteaza_serial('bt'), True))
        layout.addWidget(card)
        card, col = self.card('Cablu USB', 'Conectează dispozitivul prin cablu și selectează portul.')
        self.port_selector_usb = QComboBox()
        col.addWidget(self.port_selector_usb)
        col.addWidget(self.button('Conectează USB', lambda: self.reconecteaza_serial('usb')))
        layout.addWidget(card)
        self.status_label = self.label('Nicio conexiune activă', 'muted')
        layout.addWidget(self.status_label)
        row = QHBoxLayout()
        row.addWidget(self.button('Caută din nou porturile', self.update_serial_ports))
        row.addWidget(self.button('Deconectează', self.disconnect))
        row.addStretch()
        layout.addLayout(row)
        layout.addStretch()
        return page

    def update_serial_ports(self):
        previous = {source: selector.currentData() for source, selector in [('bt', self.port_selector_bt), ('usb', self.port_selector_usb)]}
        self.available_ports = {}
        self.port_selector_bt.clear()
        self.port_selector_usb.clear()
        from serial_comm.serial_manager import get_serial_ports
        for port in get_serial_ports():
            label, device = port['label'], port['device']
            selector = self.port_selector_bt if 'bluetooth' in label.lower() else self.port_selector_usb
            selector.addItem(label, device)
            self.available_ports[label] = device
        for source, selector in [('bt', self.port_selector_bt), ('usb', self.port_selector_usb)]:
            idx = selector.findData(previous[source])
            if idx >= 0: selector.setCurrentIndex(idx)

    def reconecteaza_serial(self, source):
        if getattr(self, 'connecting', False):
            self.status_label.setText('Conectarea este deja în curs…')
            return
        selector = self.port_selector_bt if source == 'bt' else self.port_selector_usb
        port = selector.currentData()
        if not port:
            self.status_label.setText('Niciun port disponibil. Conectează dispozitivul și caută din nou.'); return
        self.disconnect()
        self.status_label.setText(f'Se conectează la {port}…')
        # Windows opens Bluetooth ports asynchronously so navigation stays responsive.
        import threading
        self.pending_connection = None
        self.connection_error = None
        self.connecting = True
        self.connection_source = source
        def open_port():
            try:
                connection = serial.Serial(port, 9600 if source == 'bt' else 115200, timeout=0, write_timeout=1)
                if self.closing: connection.close()
                else: self.pending_connection = connection
            except Exception as exc: self.connection_error = str(exc)
            finally: self.connecting = False
        self.open_thread = threading.Thread(target=open_port, daemon=True)
        self.open_thread.start()

    def disconnect(self):
        if getattr(self, 'connecting', False): return
        if self.serial_conn:
            self.serial_conn.close()
        self.serial_conn = None
        self.receive_buffer.clear()
        self.last_rx = None
        for knob in self.potentiometers.values(): knob.set_value(None)
        self.status_label.setText('Deconectat. Macro-urile tale sunt salvate.')
        self.update_health()

    def poll_serial(self):
        if getattr(self, 'connection_error', None):
            self.status_label.setText(f'Conexiunea nu a reușit: {self.connection_error}')
            self.connection_error = None
        if getattr(self, 'pending_connection', None):
            self.serial_conn = self.pending_connection
            print(f'IVA V5 connected: {self.serial_conn.port}', flush=True)
            self.pending_connection = None
            self.save_preference('connection', {'source': self.connection_source, 'port': self.serial_conn.port})
            self.status_label.setText(f'Conectat prin {self.connection_source.upper()} la {self.serial_conn.port}')
            self.update_health()
        if not self.serial_conn or not self.serial_conn.is_open: return
        try:
            waiting = self.serial_conn.in_waiting
            if waiting: self.receive_buffer.extend(self.serial_conn.read(min(waiting, 16384)))
            for _ in range(100):
                if b'\n' not in self.receive_buffer: break
                raw, _, rest = self.receive_buffer.partition(b'\n')
                self.receive_buffer = bytearray(rest)
                try: data = json.loads(raw.decode('utf-8'))
                except (ValueError, UnicodeError): continue
                if isinstance(data, dict):
                    if self.last_rx is None:
                        print('IVA V5 first event: ' + json.dumps(data), flush=True)
                    self.last_rx = time.monotonic()
                    self.handle_uart_message(data)
            if len(self.receive_buffer) > 65536: self.receive_buffer.clear()
        except Exception as exc:
            self.disconnect()
            self.status_label.setText(f'Conexiune întreruptă: {exc}')

    def handle_uart_message(self, data):
        kind = data.get('type')
        if kind == 'key' and data.get('key') == 'pressed':
            index = self.KEY_MAP.get(str(data.get('value')))
            if index:
                self.press_count += 1
                self._highlight_taste_btn(index-1)
                name = self.taste_macro_map.get(f'T{index}', '')
                self.last_event = f'Tasta {index}  ·  {name if name in self.macros else "Fără macro"}'
                self.activity_label.setText(self.last_event)
                self.refresh_keys()
                if name in self.macros: self.simuleaza_macro(name)
        elif kind == 'volume':
            key = str(data.get('key'))
            if key in self.volume_sliders:
                try: percent = max(0, min(100, round((4095-float(data.get('value', 0)))/4095*100)))
                except (TypeError, ValueError): return
                self.volume_sliders[key].setValue(percent)
                self.potentiometers[key].set_value(percent)
                try: self.set_windows_volume(self.volume_combo[key].currentText(), percent)
                except Exception as exc: self.activity_label.setText(f'Audio: {exc}')
        elif kind == 'proxy' and data.get('key') == 'distance':
            self.proxy_distance_label.setText(f'Distanță: {data.get("value", "—")} mm')

    def set_windows_volume(self, app_name, percent):
        if app_name == 'Master Volume':
            device = AudioUtilities.GetSpeakers()
            if hasattr(device, 'EndpointVolume'):
                device.EndpointVolume.SetMasterVolumeLevelScalar(percent / 100, None)
            else:
                interface = device.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
                comtypes.cast(interface, comtypes.POINTER(IAudioEndpointVolume)).SetMasterVolumeLevelScalar(percent / 100, None)
        else: super().set_windows_volume(app_name, percent)

    def _highlight_taste_btn(self, index):
        btn = self.taste_buttons[index]
        btn.setProperty('active', True)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        QTimer.singleShot(250, lambda: self._reset_taste_btn(index))

    def _reset_taste_btn(self, index):
        btn = self.taste_buttons[index]
        btn.setProperty('active', False)
        btn.style().unpolish(btn)
        btn.style().polish(btn)

    def update_health(self):
        connected = bool(self.serial_conn and self.serial_conn.is_open)
        if connected:
            suffix = ' · date primite' if self.last_rx and time.monotonic()-self.last_rx < 10 else ' · aștept activitate'
            self.connection_badge.setText(f'● {self.serial_conn.port}{suffix}')
        elif getattr(self, 'connecting', False): self.connection_badge.setText('○ Se conectează…')
        else: self.connection_badge.setText('○ Deconectat')
        for control in self.device_controls: control.setEnabled(connected)

    def closeEvent(self, event):
        self.closing = True
        self.timer.stop()
        self.health_timer.stop()
        self.disconnect()
        pending = getattr(self, 'pending_connection', None)
        if pending: pending.close()
        event.accept()
