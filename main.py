import sys
import os
import time
import mido
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QFrame, QTextEdit)
from PyQt6.QtCore import Qt, QTimer
from dotenv import load_dotenv

# Import dari modul lokal
from styles.ui_styles import BLACKMAGIC_STYLE
from logic.obs_midi_handler import OBSWorker
from logic.ui_components import TallyBox

# Load environment variables
load_dotenv()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.obs_worker = OBSWorker()
        self.obs_worker.tally_update.connect(self.update_tally_display)
        self.obs_worker.log_signal.connect(self.add_log)
        self.obs_worker.connection_status.connect(self.update_connection_status)

        self.setWindowTitle(os.getenv('APP_NAME', 'Sekar Wangi Tally Pro Control'))
        self.resize(600, 650)
        self.init_ui()

        # Auto-populate MIDI ports
        self.refresh_midi_ports()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- HEADER ---
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(70)
        header_layout = QHBoxLayout(header)

        logo_label = QLabel("SEKAR WANGI")
        logo_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        version_label = QLabel(f"ULTRA PRO {os.getenv('APP_VERSION', '4.1')}")
        version_label.setStyleSheet("color: #0078D4; font-size: 11px; margin-top: 5px;")

        header_layout.addWidget(logo_label)
        header_layout.addWidget(version_label)
        header_layout.addStretch()

        main_layout.addWidget(header)

        # --- CONTENT AREA ---
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Config Section
        config_box = QFrame()
        config_box.setStyleSheet("background-color: #1E1E1E; border-radius: 4px;")
        config_layout = QHBoxLayout(config_box)

        self.midi_selector = QComboBox()
        self.midi_selector.addItem("Mencari Hardware...")

        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("Password WebSocket")
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setText(os.getenv('OBS_PASSWORD', ''))

        self.conn_btn = QPushButton("HUBUNGKAN")
        self.conn_btn.setObjectName("ConnectBtn")
        self.conn_btn.setFixedWidth(120)
        self.conn_btn.clicked.connect(self.connect_systems)

        config_layout.addWidget(QLabel("MIDI:"))
        config_layout.addWidget(self.midi_selector)
        config_layout.addWidget(QLabel("WS:"))
        config_layout.addWidget(self.pwd_input)
        config_layout.addWidget(self.conn_btn)

        content_layout.addWidget(config_box)

        # Multiview Tally Grid
        grid_container = QWidget()
        grid_layout = QHBoxLayout(grid_container)

        self.tally_boxes = {}
        # Kita bagi jadi 2 baris
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()

        for i in range(1, 9):
            box = TallyBox(i)
            self.tally_boxes[i] = box
            if i <= 4:
                row1.addWidget(box)
            else:
                row2.addWidget(box)

        v_grid = QVBoxLayout()
        v_grid.addLayout(row1)
        v_grid.addLayout(row2)
        content_layout.addLayout(v_grid)

        # Log Area
        content_layout.addWidget(QLabel("LOG AKTIVITAS"))
        self.log_area = QTextEdit()
        self.log_area.setObjectName("LogArea")
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(150)
        content_layout.addWidget(self.log_area)

        main_layout.addWidget(content)

        self.setStyleSheet(BLACKMAGIC_STYLE)

    def refresh_midi_ports(self):
        self.midi_selector.clear()
        try:
            ports = mido.get_output_names()
            if ports:
                self.midi_selector.addItems(ports)
                # Auto-select configured port
                default_port = os.getenv('MIDI_PORT_NAME', '')
                if default_port in ports:
                    self.midi_selector.setCurrentText(default_port)
            else:
                self.midi_selector.addItem("No MIDI ports found")
        except Exception as e:
            self.add_log(f"MIDI port detection error: {str(e)}")

    def connect_systems(self):
        midi_port = self.midi_selector.currentText()
        obs_password = self.pwd_input.text()

        obs_host = os.getenv('OBS_HOST', 'localhost')
        obs_port = int(os.getenv('OBS_PORT', '4455'))

        success = True

        # Connect MIDI
        if not self.obs_worker.connect_midi(midi_port):
            success = False

        # Connect OBS
        if not self.obs_worker.connect_obs(obs_host, obs_port, obs_password):
            success = False

        if success:
            self.conn_btn.setText("TERHUBUNG")
            self.conn_btn.setStyleSheet("background-color: #00AA00;")
        else:
            self.conn_btn.setText("GAGAL")
            self.conn_btn.setStyleSheet("background-color: #AA0000;")

    def update_tally_display(self, cam_id, state):
        if cam_id in self.tally_boxes:
            self.tally_boxes[cam_id].set_state(state)

    def update_connection_status(self, connected):
        if connected:
            self.conn_btn.setText("TERHUBUNG")
            self.conn_btn.setStyleSheet("background-color: #00AA00;")
        else:
            self.conn_btn.setText("HUBUNGKAN")
            self.conn_btn.setStyleSheet("")

    def add_log(self, text):
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {text}")

    def closeEvent(self, event):
        self.obs_worker.disconnect()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())