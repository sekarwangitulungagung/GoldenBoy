"""Dynamic stylesheet generator for GoldenBoy. Supports dark and light system themes."""

_DARK = dict(
    win_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #09111d,stop:0.45 #111b2d,stop:1 #182338)",
    panel_bg="rgba(15,24,41,0.82)",
    panel_border="rgba(220,234,255,0.08)",
    card_bg="rgba(12,19,33,0.90)",
    card_border="rgba(212,226,255,0.08)",
    splash_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(13,22,38,240),stop:1 rgba(29,48,79,240))",
    splash_border="rgba(204,228,255,0.16)",
    input_bg="rgba(9,16,29,0.84)",
    input_border="rgba(173,193,225,0.14)",
    log_bg="rgba(6,11,20,0.92)",
    log_border="rgba(193,213,245,0.08)",
    text_base="#e6eefb",
    text_title="#f5f9ff",
    text_subtitle="#72a4e5",
    text_section="#f3f7ff",
    text_section_sub="#9db1d5",
    text_card="#f7fbff",
    text_card_sub="#98aaca",
    text_field="#9eb3d6",
    text_hint="#98aaca",
    text_mode_badge="#d4e7ff",
    text_status_badge="#dfe9fb",
    text_status_ok="#dcffe8",
    text_input="#eff5ff",
    text_log="#dfebff",
    text_splash_title="#f3f7ff",
    text_splash_sub="#93b5df",
    text_splash_status="#d2def4",
    mode_badge_bg="rgba(57,110,175,0.20)",
    mode_badge_border="rgba(124,180,246,0.22)",
    status_idle_bg="rgba(97,111,139,0.18)",
    status_idle_border="rgba(178,193,217,0.16)",
    status_ok_bg="rgba(34,197,94,0.18)",
    status_ok_border="rgba(95,225,146,0.22)",
    primary_btn="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #228dff,stop:1 #45c7ff)",
    primary_btn_hover="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #35a0ff,stop:1 #5ad2ff)",
    primary_btn_text="#f7fbff",
    danger_btn="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #c5304f,stop:1 #ff6b7a)",
    danger_btn_text="#fff5f6",
    ghost_btn_bg="rgba(229,240,255,0.06)",
    ghost_btn_border="rgba(225,237,255,0.11)",
    ghost_btn_text="#e6eefb",
    ghost_btn_hover="rgba(229,240,255,0.10)",
    scene_idle_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(19,30,51,0.95),stop:1 rgba(11,18,31,0.95))",
    scene_idle_border="rgba(128,150,184,0.16)",
    scene_idle_text="#a7bbdd",
    scene_preview_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(17,101,54,0.97),stop:1 rgba(12,58,34,0.97))",
    scene_preview_border="rgba(87,222,139,0.24)",
    scene_preview_text="#f0fff5",
    scene_program_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(184,34,54,0.96),stop:1 rgba(96,15,24,0.96))",
    scene_program_border="rgba(255,122,135,0.26)",
    scene_program_text="#fff7f8",
    hover_border="rgba(126,190,255,0.22)",
    transition_checked_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(46,121,221,0.42),stop:1 rgba(22,49,104,0.92))",
    transition_checked_border="rgba(106,180,255,0.30)",
    track_bg="rgba(241,248,255,0.08)",
    track_border="rgba(235,243,255,0.06)",
    bar_gradient="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #47d0ff,stop:1 #6ef2c3)",
    menu_bg="#0d1626",
    menu_border="#1e2e48",
    menu_text="#dce9ff",
    menu_selected_bg="#1a3057",
    menu_selected_text="#ffffff",
    obs_scene_bg="rgba(14,22,38,0.82)",
    obs_scene_border="rgba(200,220,255,0.10)",
    obs_scene_text="#cfe0fb",
    obs_scene_active="#47d0ff",
)

_LIGHT = dict(
    win_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #eef3fb,stop:0.5 #dce8f7,stop:1 #cdd8ef)",
    panel_bg="rgba(255,255,255,0.92)",
    panel_border="rgba(90,130,195,0.14)",
    card_bg="rgba(245,249,255,0.96)",
    card_border="rgba(80,120,190,0.12)",
    splash_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(220,232,255,240),stop:1 rgba(180,210,250,240))",
    splash_border="rgba(80,120,200,0.22)",
    input_bg="rgba(240,246,255,0.90)",
    input_border="rgba(110,150,210,0.28)",
    log_bg="rgba(235,242,255,0.94)",
    log_border="rgba(100,140,200,0.14)",
    text_base="#1a2540",
    text_title="#0f1c36",
    text_subtitle="#2a5ca8",
    text_section="#0e1a35",
    text_section_sub="#3b5e9a",
    text_card="#0e1a35",
    text_card_sub="#4a6690",
    text_field="#3a567a",
    text_hint="#4a6690",
    text_mode_badge="#1a4080",
    text_status_badge="#1a3060",
    text_status_ok="#0a4a2a",
    text_input="#0f1a30",
    text_log="#162038",
    text_splash_title="#0e1e36",
    text_splash_sub="#2c5490",
    text_splash_status="#344d7a",
    mode_badge_bg="rgba(30,90,200,0.12)",
    mode_badge_border="rgba(50,120,230,0.22)",
    status_idle_bg="rgba(80,100,140,0.12)",
    status_idle_border="rgba(100,130,180,0.18)",
    status_ok_bg="rgba(20,160,80,0.14)",
    status_ok_border="rgba(30,180,90,0.24)",
    primary_btn="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1a7de8,stop:1 #22aff0)",
    primary_btn_hover="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #2a8ff8,stop:1 #30beff)",
    primary_btn_text="#ffffff",
    danger_btn="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #c52040,stop:1 #f04060)",
    danger_btn_text="#ffffff",
    ghost_btn_bg="rgba(20,60,130,0.07)",
    ghost_btn_border="rgba(30,70,160,0.18)",
    ghost_btn_text="#1a3060",
    ghost_btn_hover="rgba(20,60,130,0.13)",
    scene_idle_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(220,230,248,0.95),stop:1 rgba(200,215,240,0.95))",
    scene_idle_border="rgba(90,120,180,0.18)",
    scene_idle_text="#2a4070",
    scene_preview_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(30,140,80,0.92),stop:1 rgba(20,100,55,0.92))",
    scene_preview_border="rgba(50,210,120,0.30)",
    scene_preview_text="#f0fff5",
    scene_program_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(200,35,55,0.92),stop:1 rgba(140,15,30,0.92))",
    scene_program_border="rgba(255,100,115,0.32)",
    scene_program_text="#fff6f7",
    hover_border="rgba(40,130,240,0.28)",
    transition_checked_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(26,100,220,0.25),stop:1 rgba(10,60,160,0.55))",
    transition_checked_border="rgba(40,140,250,0.36)",
    track_bg="rgba(30,80,180,0.10)",
    track_border="rgba(40,100,200,0.08)",
    bar_gradient="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1a90ff,stop:1 #22d4c0)",
    menu_bg="#f0f5ff",
    menu_border="#c0d0e8",
    menu_text="#162040",
    menu_selected_bg="#2060c8",
    menu_selected_text="#ffffff",
    obs_scene_bg="rgba(230,240,255,0.92)",
    obs_scene_border="rgba(60,110,200,0.14)",
    obs_scene_text="#1a3060",
    obs_scene_active="#0a70e0",
)


def _build_qss(c: dict) -> str:
    return f"""
QMainWindow, QDialog {{
    background: {c["win_bg"]};
}}

QWidget {{
    color: {c["text_base"]};
    font-family: "SF Pro Display", "Neue Haas Grotesk", "Helvetica Neue", "Segoe UI", Arial, sans-serif;
}}

QMenuBar {{
    background: {c["menu_bg"]};
    color: {c["menu_text"]};
    border-bottom: 1px solid {c["menu_border"]};
    padding: 2px 4px;
    font-size: 13px;
}}

QMenuBar::item {{
    background: transparent;
    padding: 6px 12px;
    border-radius: 6px;
    color: {c["menu_text"]};
}}

QMenuBar::item:selected {{
    background: {c["menu_selected_bg"]};
    color: {c["menu_selected_text"]};
}}

QMenu {{
    background: {c["menu_bg"]};
    border: 1px solid {c["menu_border"]};
    border-radius: 10px;
    padding: 4px 0;
    color: {c["menu_text"]};
    font-size: 13px;
}}

QMenu::item {{
    padding: 7px 28px 7px 18px;
    border-radius: 6px;
    margin: 1px 4px;
}}

QMenu::item:selected {{
    background: {c["menu_selected_bg"]};
    color: {c["menu_selected_text"]};
}}

QMenu::separator {{
    height: 1px;
    background: {c["menu_border"]};
    margin: 4px 10px;
}}

QMenu::indicator {{
    width: 14px;
    height: 14px;
    margin-left: 6px;
}}

QFrame#SplashShell {{
    background: {c["splash_bg"]};
    border: 1px solid {c["splash_border"]};
    border-radius: 28px;
}}

QLabel#SplashTitle {{
    font-size: 30px;
    font-weight: 800;
    color: {c["text_splash_title"]};
    letter-spacing: 4px;
    font-family: "SF Pro Display", "Neue Haas Grotesk", "Helvetica Neue", "Segoe UI", Arial, sans-serif;
}}

QFrame#SplashDivider {{
    background: {c["bar_gradient"]};
    border: none;
    border-radius: 1px;
    min-height: 2px;
    max-height: 2px;
    margin: 2px 60px;
}}

QLabel#SplashSubtitle {{
    font-size: 13px;
    color: {c["text_splash_sub"]};
    letter-spacing: 0.4px;
}}

QLabel#SplashStatus {{
    font-size: 12px;
    color: {c["text_splash_status"]};
    letter-spacing: 0.5px;
}}

QFrame#ProgressTrack {{
    background: {c["track_bg"]};
    border: 1px solid {c["track_border"]};
    border-radius: 10px;
    min-height: 12px;
    max-height: 12px;
}}

QFrame#ProgressBar {{
    background: {c["bar_gradient"]};
    border-radius: 10px;
    min-height: 12px;
    max-height: 12px;
}}

QFrame#TopBar,
QFrame#Panel,
QFrame#LogDrawer,
QFrame#ConfigCard,
QFrame#OBSScenesPanel {{
    background: {c["panel_bg"]};
    border: 1px solid {c["panel_border"]};
    border-radius: 20px;
}}

QLabel#Title {{
    font-size: 22px;
    font-weight: 800;
    color: {c["text_title"]};
}}

QLabel#Subtitle {{
    font-size: 11px;
    font-weight: 700;
    color: {c["text_subtitle"]};
    letter-spacing: 1.2px;
    text-transform: uppercase;
}}

QLabel#SectionTitle {{
    font-size: 18px;
    font-weight: 800;
    color: {c["text_section"]};
}}

QLabel#SectionSubtitle {{
    font-size: 12px;
    color: {c["text_section_sub"]};
    line-height: 1.4em;
}}

QLabel#CardTitle,
QLabel#TransitionTitle {{
    font-size: 15px;
    font-weight: 750;
    color: {c["text_card"]};
}}

QLabel#CardSubtitle,
QLabel#TransitionSubtitle,
QLabel#HintText {{
    font-size: 12px;
    color: {c["text_card_sub"]};
    line-height: 1.45em;
}}

QLabel#FieldLabel {{
    font-size: 11px;
    font-weight: 700;
    color: {c["text_field"]};
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}

QLabel#ModeBadge,
QLabel#StatusBadge {{
    border-radius: 12px;
    padding: 9px 14px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.7px;
}}

QLabel#ModeBadge {{
    background: {c["mode_badge_bg"]};
    border: 1px solid {c["mode_badge_border"]};
    color: {c["text_mode_badge"]};
}}

QLabel#StatusBadge {{
    background: {c["status_idle_bg"]};
    border: 1px solid {c["status_idle_border"]};
    color: {c["text_status_badge"]};
}}

QLabel#StatusBadge[kind="success"] {{
    background: {c["status_ok_bg"]};
    border: 1px solid {c["status_ok_border"]};
    color: {c["text_status_ok"]};
}}

QLabel#OBSSceneLabel {{
    font-size: 13px;
    color: {c["obs_scene_text"]};
    padding: 6px 10px;
    border-radius: 8px;
    border: 1px solid {c["obs_scene_border"]};
    background: {c["obs_scene_bg"]};
}}

QLabel#OBSSceneLabel[active="true"] {{
    color: {c["obs_scene_active"]};
    border: 1px solid {c["obs_scene_active"]};
    font-weight: 700;
}}

QPushButton#PrimaryBtn,
QPushButton#DangerBtn,
QPushButton#GhostBtn {{
    border-radius: 12px;
    font-size: 12px;
    font-weight: 800;
    padding: 10px 16px;
    min-height: 36px;
}}

QPushButton#PrimaryBtn {{
    background: {c["primary_btn"]};
    color: {c["primary_btn_text"]};
    border: none;
}}

QPushButton#PrimaryBtn:hover {{
    background: {c["primary_btn_hover"]};
}}

QPushButton#DangerBtn {{
    background: {c["danger_btn"]};
    color: {c["danger_btn_text"]};
    border: none;
}}

QPushButton#GhostBtn {{
    background: {c["ghost_btn_bg"]};
    border: 1px solid {c["ghost_btn_border"]};
    color: {c["ghost_btn_text"]};
}}

QPushButton#GhostBtn:hover {{
    background: {c["ghost_btn_hover"]};
}}

QComboBox,
QLineEdit {{
    background: {c["input_bg"]};
    border: 1px solid {c["input_border"]};
    border-radius: 12px;
    padding: 10px 12px;
    font-size: 13px;
    color: {c["text_input"]};
    min-height: 36px;
}}

QComboBox::drop-down {{
    border: none;
    width: 26px;
}}

QComboBox QAbstractItemView {{
    background: {c["menu_bg"]};
    color: {c["menu_text"]};
    border: 1px solid {c["menu_border"]};
    border-radius: 8px;
    selection-background-color: {c["menu_selected_bg"]};
    selection-color: {c["menu_selected_text"]};
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {c["ghost_btn_border"]};
    border-radius: 4px;
    min-height: 28px;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QPushButton#SceneCard,
QPushButton#TransitionCard {{
    background: {c["card_bg"]};
    border: 1px solid {c["card_border"]};
    border-radius: 16px;
    text-align: left;
}}

QPushButton#SceneCard {{
    min-height: 100px;
    padding: 16px;
    font-size: 18px;
    font-weight: 850;
    color: {c["text_card"]};
}}

QPushButton#SceneCard[state="idle"] {{
    background: {c["scene_idle_bg"]};
    border: 1px solid {c["scene_idle_border"]};
    color: {c["scene_idle_text"]};
}}

QPushButton#SceneCard[state="preview"] {{
    background: {c["scene_preview_bg"]};
    border: 1px solid {c["scene_preview_border"]};
    color: {c["scene_preview_text"]};
}}

QPushButton#SceneCard[state="program"] {{
    background: {c["scene_program_bg"]};
    border: 1px solid {c["scene_program_border"]};
    color: {c["scene_program_text"]};
}}

QPushButton#SceneCard:hover,
QPushButton#TransitionCard:hover,
QFrame#ConfigCard:hover {{
    border: 1px solid {c["hover_border"]};
}}

QPushButton#TransitionCard {{
    min-height: 130px;
}}

QPushButton#TransitionCard:checked {{
    background: {c["transition_checked_bg"]};
    border: 1px solid {c["transition_checked_border"]};
}}

QTextEdit#LogArea {{
    background: {c["log_bg"]};
    border: 1px solid {c["log_border"]};
    border-radius: 14px;
    padding: 10px;
    font-family: "SF Mono", Menlo, Consolas, "Courier New", monospace;
    font-size: 11px;
    color: {c["text_log"]};
}}
"""


def get_dynamic_qss(is_dark: bool = True) -> str:
    """Return full application QSS for the given theme."""
    return _build_qss(_DARK if is_dark else _LIGHT)


# Backwards-compatible alias (dark theme)
APP_QSS = get_dynamic_qss(is_dark=True)

