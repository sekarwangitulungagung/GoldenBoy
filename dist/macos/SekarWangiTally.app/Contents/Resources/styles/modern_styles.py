APP_QSS = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #09111d, stop:0.45 #111b2d, stop:1 #182338);
}

QWidget {
    color: #e6eefb;
    font-family: "Avenir Next", "Segoe UI", sans-serif;
}

QFrame#SplashShell {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(13, 22, 38, 240),
                                stop:1 rgba(29, 48, 79, 240));
    border: 1px solid rgba(204, 228, 255, 0.16);
    border-radius: 28px;
}

QLabel#SplashTitle {
    font-size: 28px;
    font-weight: 800;
    color: #f3f7ff;
    letter-spacing: 0.8px;
}

QLabel#SplashSubtitle {
    font-size: 13px;
    color: #93b5df;
}

QLabel#SplashStatus {
    font-size: 12px;
    color: #d2def4;
    letter-spacing: 0.5px;
}

QFrame#ProgressTrack {
    background: rgba(241, 248, 255, 0.08);
    border: 1px solid rgba(235, 243, 255, 0.06);
    border-radius: 10px;
    min-height: 12px;
    max-height: 12px;
}

QFrame#ProgressBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #47d0ff,
                                stop:1 #6ef2c3);
    border-radius: 10px;
    min-height: 12px;
    max-height: 12px;
}

QFrame#TopBar,
QFrame#Panel,
QFrame#LogDrawer,
QFrame#ConfigCard {
    background: rgba(15, 24, 41, 0.76);
    border: 1px solid rgba(220, 234, 255, 0.08);
    border-radius: 22px;
}

QLabel#Title {
    font-size: 22px;
    font-weight: 800;
    color: #f5f9ff;
}

QLabel#Subtitle {
    font-size: 11px;
    font-weight: 700;
    color: #72a4e5;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}

QLabel#SectionTitle {
    font-size: 20px;
    font-weight: 800;
    color: #f3f7ff;
}

QLabel#SectionSubtitle {
    font-size: 12px;
    color: #9db1d5;
    line-height: 1.4em;
}

QLabel#CardTitle,
QLabel#TransitionTitle {
    font-size: 16px;
    font-weight: 750;
    color: #f7fbff;
}

QLabel#CardSubtitle,
QLabel#TransitionSubtitle,
QLabel#HintText {
    font-size: 12px;
    color: #98aaca;
    line-height: 1.45em;
}

QLabel#FieldLabel {
    font-size: 11px;
    font-weight: 700;
    color: #9eb3d6;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

QLabel#ModeBadge,
QLabel#StatusBadge {
    border-radius: 12px;
    padding: 9px 14px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.7px;
}

QLabel#ModeBadge {
    background: rgba(57, 110, 175, 0.2);
    border: 1px solid rgba(124, 180, 246, 0.22);
    color: #d4e7ff;
}

QLabel#StatusBadge {
    background: rgba(97, 111, 139, 0.18);
    border: 1px solid rgba(178, 193, 217, 0.16);
    color: #dfe9fb;
}

QLabel#StatusBadge[kind="success"] {
    background: rgba(34, 197, 94, 0.18);
    border: 1px solid rgba(95, 225, 146, 0.22);
    color: #dcffe8;
}

QPushButton#PrimaryBtn,
QPushButton#DangerBtn,
QPushButton#GhostBtn {
    border-radius: 14px;
    font-size: 12px;
    font-weight: 800;
    padding: 12px 18px;
}

QPushButton#PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #228dff,
                                stop:1 #45c7ff);
    color: #f7fbff;
    border: none;
}

QPushButton#PrimaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #35a0ff,
                                stop:1 #5ad2ff);
}

QPushButton#DangerBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #c5304f,
                                stop:1 #ff6b7a);
    color: #fff5f6;
    border: none;
}

QPushButton#GhostBtn {
    background: rgba(229, 240, 255, 0.06);
    border: 1px solid rgba(225, 237, 255, 0.11);
    color: #e6eefb;
}

QPushButton#GhostBtn:hover {
    background: rgba(229, 240, 255, 0.1);
}

QComboBox,
QLineEdit {
    background: rgba(9, 16, 29, 0.84);
    border: 1px solid rgba(173, 193, 225, 0.14);
    border-radius: 14px;
    padding: 11px 12px;
    font-size: 13px;
    color: #eff5ff;
}

QComboBox::drop-down {
    border: none;
    width: 26px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QPushButton#SceneCard,
QPushButton#TransitionCard {
    background: rgba(12, 19, 33, 0.9);
    border: 1px solid rgba(212, 226, 255, 0.08);
    border-radius: 18px;
    text-align: left;
}

QPushButton#SceneCard {
    min-height: 116px;
    padding: 18px;
    font-size: 20px;
    font-weight: 850;
    color: #d4e3fb;
}

QPushButton#SceneCard[state="idle"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(19, 30, 51, 0.95),
                                stop:1 rgba(11, 18, 31, 0.95));
    border: 1px solid rgba(128, 150, 184, 0.16);
    color: #a7bbdd;
}

QPushButton#SceneCard[state="preview"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(17, 101, 54, 0.97),
                                stop:1 rgba(12, 58, 34, 0.97));
    border: 1px solid rgba(87, 222, 139, 0.24);
    color: #f0fff5;
}

QPushButton#SceneCard[state="program"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(184, 34, 54, 0.96),
                                stop:1 rgba(96, 15, 24, 0.96));
    border: 1px solid rgba(255, 122, 135, 0.26);
    color: #fff7f8;
}

QPushButton#SceneCard:hover,
QPushButton#TransitionCard:hover,
QFrame#ConfigCard:hover {
    border: 1px solid rgba(126, 190, 255, 0.22);
}

QPushButton#TransitionCard {
    min-height: 146px;
}

QPushButton#TransitionCard:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(46, 121, 221, 0.42),
                                stop:1 rgba(22, 49, 104, 0.92));
    border: 1px solid rgba(106, 180, 255, 0.3);
}

QTextEdit#LogArea {
    background: rgba(6, 11, 20, 0.92);
    border: 1px solid rgba(193, 213, 245, 0.08);
    border-radius: 16px;
    padding: 10px;
    font-family: "SF Mono", Menlo, Consolas, monospace;
    font-size: 11px;
    color: #dfebff;
}
"""
