import sys
import re
import threading
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QFrame, QTextEdit, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QFont, QIcon

# --- CUSTOM STYLESHEET (The Blackmagic Look) ---
BLACKMAGIC_STYLE = """
QMainWindow {
    background-color: #121212;
}
QWidget {
    color: #E1E1E1;
    font-family: 'Segoe UI', Arial;
}
QFrame#Header {
    background-color: #000000;
    border-bottom: 2px solid #333333;
}
QFrame#TallyBox {
    background-color: #1E1E1E;
    border: 2px solid #333333;
    border-radius: 8px;
}
QLabel#CamLabel {
    font-weight: bold;
    font-size: 16px;
    color: #666666;
}
QLineEdit {
    background-color: #2D2D2D;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 5px;
    color: white;
}
QPushButton#ConnectBtn {
    background-color: #0078D4;
    border-radius: 4px;
    font-weight: bold;
    padding: 8px;
}
QPushButton#ConnectBtn:hover {
    background-color: #0086F0;
}
QTextEdit#LogArea {
    background-color: #0A0A0A;
    border: none;
    color: #00FF00;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}
"""

class OBSWorker(QObject):
    # Signal untuk update UI dari background thread
    tally_update = pyqtSignal(int, int) # cam_id, state (0:idle, 1:live, 2:preview)
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Placeholder untuk logika OBS & MIDI

class TallyBox(QFrame):
    def __init__(self, cam_id):
        super().__init__()
        self.setObjectName("TallyBox")
        self.setFixedSize(120, 90)
        
        layout = QVBoxLayout()
        self.label = QLabel(f"CAM {cam_id}")
        self.label.setObjectName("CamLabel")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status = QLabel("IDLE")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("font-size: 10px; color: #444444;")
        
        layout.addWidget(self.label)
        layout.addWidget(self.status)
        self.setLayout(layout)

    def set_state(self, state):
        if state == 1: # LIVE
            self.setStyleSheet("QFrame#TallyBox { border: 2px solid #FF0000; background-color: #2A0000; }")
            self.label.setStyleSheet("color: #FF0000;")
            self.status.setText("● PROGRAM")
            self.status.setStyleSheet("color: #FF0000;")
        elif state == 2: # PREVIEW
            self.setStyleSheet("QFrame#TallyBox { border: 2px solid #00FF00; background-color: #002A00; }")
            self.label.setStyleSheet("color: #00FF00;")
            self.status.setText("● PREVIEW")
            self.status.setStyleSheet("color: #00FF00;")
        else: # IDLE
            self.setStyleSheet("")
            self.label.setStyleSheet("")
            self.status.setText("IDLE")
            self.status.setStyleSheet("color: #444444;")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sekar Wangi Tally Pro Control")
        self.resize(600, 650)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # --- HEADER ---
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(70)
        header_layout = QHBoxLayout(header)
        
        logo_label = QLabel("SEKAR WANGI")
        logo_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        version_label = QLabel("ULTRA PRO 4.1")
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
        
        self.conn_btn = QPushButton("HUBUNGKAN")
        self.conn_btn.setObjectName("ConnectBtn")
        self.conn_btn.setFixedWidth(120)
        
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
            if i <= 4: row1.addWidget(box)
            else: row2.addWidget(box)
            
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

    def add_log(self, text):
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())