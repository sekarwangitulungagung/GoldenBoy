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