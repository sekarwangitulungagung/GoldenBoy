from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

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
        if state == 1:  # LIVE
            self.setStyleSheet("QFrame#TallyBox { border: 2px solid #FF0000; background-color: #2A0000; }")
            self.label.setStyleSheet("color: #FF0000;")
            self.status.setText("● PROGRAM")
            self.status.setStyleSheet("color: #FF0000;")
        elif state == 2:  # PREVIEW
            self.setStyleSheet("QFrame#TallyBox { border: 2px solid #00FF00; background-color: #002A00; }")
            self.label.setStyleSheet("color: #00FF00;")
            self.status.setText("● PREVIEW")
            self.status.setStyleSheet("color: #00FF00;")
        else:  # IDLE
            self.setStyleSheet("")
            self.label.setStyleSheet("")
            self.status.setText("IDLE")
            self.status.setStyleSheet("color: #444444;")