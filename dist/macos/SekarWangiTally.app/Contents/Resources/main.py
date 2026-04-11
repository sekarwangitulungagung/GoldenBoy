import os
import sys
import time
from pathlib import Path
from typing import Dict

import qtawesome as qta
from dotenv import load_dotenv
from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QSequentialAnimationGroup, Qt, QTimer
from PyQt6.QtGui import QColor, QKeySequence, QShortcut
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from logic.app_controller import AppController, AppRuntimeConfig, load_runtime_config
from logic.config_store import ConfigStore
from styles.modern_styles import APP_QSS


try:
    import qdarktheme
except ImportError:
    qdarktheme = None
    import qdarkstyle


load_dotenv()
LOGO_PATH = Path(__file__).parent / "res" / "logo_swm.svg"


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(720, 420)
        self._build_ui()
        self._start_animation()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)

        shell = QFrame()
        shell.setObjectName("SplashShell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(32, 28, 32, 28)
        shell_layout.setSpacing(14)
        shell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo = QSvgWidget(str(LOGO_PATH))
        self.logo.setFixedSize(250, 112)

        self.boot_title = QLabel("GOLDENBOY Control Suite")
        self.boot_title.setObjectName("SplashTitle")
        self.boot_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.boot_subtitle = QLabel("Booting native control interface")
        self.boot_subtitle.setObjectName("SplashSubtitle")
        self.boot_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_frame = QFrame()
        self.progress_frame.setObjectName("ProgressTrack")
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        self.progress_bar = QFrame()
        self.progress_bar.setObjectName("ProgressBar")
        self.progress_bar.setMaximumWidth(0)
        progress_layout.addWidget(self.progress_bar)

        self.status = QLabel("Initializing switcher runtime")
        self.status.setObjectName("SplashStatus")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        shell_layout.addStretch(1)
        shell_layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)
        shell_layout.addWidget(self.boot_title)
        shell_layout.addWidget(self.boot_subtitle)
        shell_layout.addSpacing(8)
        shell_layout.addWidget(self.progress_frame)
        shell_layout.addWidget(self.status)
        shell_layout.addStretch(1)

        outer.addWidget(shell)

        self.setWindowOpacity(0.0)

    def _start_animation(self) -> None:
        self.fade = QPropertyAnimation(self, b"windowOpacity", self)
        self.fade.setDuration(320)
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(1.0)
        self.fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade.start()

        self.progress_anim = QPropertyAnimation(self.progress_bar, b"maximumWidth", self)
        self.progress_anim.setDuration(1800)
        self.progress_anim.setStartValue(0)
        self.progress_anim.setEndValue(430)
        self.progress_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.progress_anim.start()

        messages = [
            "Initializing switcher runtime",
            "Loading SQLite configuration store",
            "Preparing scene and transition panels",
            "Ready to open configuration phase",
        ]
        for index, message in enumerate(messages, start=1):
            QTimer.singleShot(index * 420, lambda text=message: self.status.setText(text))


class AnimatedCard(QFrame):
    def __init__(self, icon_name: str, title: str, subtitle: str):
        super().__init__()
        self.setObjectName("ConfigCard")
        self.effect = QGraphicsOpacityEffect(self)
        self.effect.setOpacity(0.0)
        self.setGraphicsEffect(self.effect)
        self._build_ui(icon_name, title, subtitle)

    def _build_ui(self, icon_name: str, title: str, subtitle: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        icon = QLabel()
        icon.setPixmap(qta.icon(icon_name, color=QColor("#d9efff")).pixmap(22, 22))

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("CardSubtitle")
        subtitle_label.setWordWrap(True)

        layout.addWidget(icon)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addStretch(1)


class SceneCard(QPushButton):
    def __init__(self, scene_id: int):
        super().__init__()
        self.scene_id = scene_id
        self.scene_state = "idle"
        self.setObjectName("SceneCard")
        self.setProperty("state", "idle")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build_text()

    def _build_text(self) -> None:
        state_text = {
            "idle": "STANDBY",
            "preview": "PREVIEW",
            "program": "PROGRAM",
        }.get(self.scene_state, "STANDBY")
        self.setText(f"SCENE {self.scene_id}\n{state_text}")

    def set_state(self, state: str) -> None:
        self.scene_state = state
        self.setProperty("state", state)
        self._build_text()
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class TransitionCard(QPushButton):
    def __init__(self, name: str, icon_name: str, description: str):
        super().__init__()
        self.transition_name = name
        self.setObjectName("TransitionCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        icon = QLabel()
        icon.setPixmap(qta.icon(icon_name, color=QColor("#f4f8ff")).pixmap(20, 20))
        title = QLabel(name)
        title.setObjectName("TransitionTitle")
        detail = QLabel(description)
        detail.setObjectName("TransitionSubtitle")
        detail.setWordWrap(True)

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(detail)
        layout.addStretch(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.runtime_config = load_runtime_config()
        self.config_store = ConfigStore()
        self.runtime_config = self._hydrate_runtime_config(self.runtime_config)
        self.controller = AppController(self.runtime_config)
        self.controller.tally_update.connect(self.update_scene_state)
        self.controller.log_signal.connect(self.add_log)
        self.controller.connection_status.connect(self.on_connection_change)

        self.scene_cards: Dict[int, SceneCard] = {}
        self.transition_cards: list[TransitionCard] = []
        self.config_cards: list[AnimatedCard] = []
        self.config_card_animations: list[QPropertyAnimation] = []
        self.connected = False
        self.log_open = False

        self.setWindowTitle(os.getenv("APP_NAME", "GOLDENBOY"))
        self.resize(1360, 860)
        self._build_ui()
        self._bind_shortcuts()
        self._load_saved_values_into_fields()
        self._load_midi_ports()
        self._render_scene_cards()
        self._render_transition_cards()
        self._animate_window_entry()
        self._animate_config_phase()

        self.add_log("GoldenBoy initialized")
        self.add_log(f"Mode {self.runtime_config.app_mode.upper()} ready")

    def _hydrate_runtime_config(self, runtime: AppRuntimeConfig) -> AppRuntimeConfig:
        defaults = {
            "switcher_type": runtime.switcher_type,
            "host": runtime.host,
            "port": runtime.port,
            "midi_port_name": runtime.midi_port_name,
            "channel_count": runtime.channel_count,
            "obs_password": runtime.obs_password,
        }
        data = self.config_store.get_many(defaults)
        return AppRuntimeConfig(
            app_mode=runtime.app_mode,
            switcher_type=str(data["switcher_type"]),
            host=str(data["host"]),
            port=int(data["port"]),
            obs_password=str(data["obs_password"]),
            midi_port_name=str(data["midi_port_name"]),
            channel_count=int(data["channel_count"]),
        )

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        self.top_bar = QFrame()
        self.top_bar.setObjectName("TopBar")
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(20, 18, 20, 18)

        brand_layout = QVBoxLayout()
        brand_title = QLabel("GoldenBoy Pro")
        brand_title.setObjectName("Title")
        brand_subtitle = QLabel("Native Broadcast Control")
        brand_subtitle.setObjectName("Subtitle")
        brand_layout.addWidget(brand_title)
        brand_layout.addWidget(brand_subtitle)

        self.status_badge = QLabel("STANDBY")
        self.status_badge.setObjectName("StatusBadge")
        self.mode_badge = QLabel(self.runtime_config.app_mode.upper())
        self.mode_badge.setObjectName("ModeBadge")

        self.top_reconnect = QPushButton("Reconnect")
        self.top_reconnect.setObjectName("GhostBtn")
        self.top_reconnect.setIcon(qta.icon("fa5s.sync-alt", color="#dbe8ff"))
        self.top_reconnect.clicked.connect(self.toggle_connection)

        top_layout.addLayout(brand_layout)
        top_layout.addStretch(1)
        top_layout.addWidget(self.mode_badge)
        top_layout.addWidget(self.status_badge)
        top_layout.addWidget(self.top_reconnect)

        self.stack = QStackedWidget()
        self.config_page = self._build_config_page()
        self.dashboard_page = self._build_dashboard_page()
        self.stack.addWidget(self.config_page)
        self.stack.addWidget(self.dashboard_page)
        self.stack.setCurrentWidget(self.config_page)

        layout.addWidget(self.top_bar)
        layout.addWidget(self.stack, stretch=1)

        self.setStyleSheet(APP_QSS)

    def _build_config_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(14)

        hero = QFrame()
        hero.setObjectName("Panel")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(18)

        hero_text = QVBoxLayout()
        title = QLabel("Configuration Phase")
        title.setObjectName("SectionTitle")
        subtitle = QLabel(
            "Set switcher, MIDI routing, and scene grid first. Each block is animated to guide the boot sequence before the main control screen opens."
        )
        subtitle.setObjectName("SectionSubtitle")
        subtitle.setWordWrap(True)
        hero_text.addWidget(title)
        hero_text.addWidget(subtitle)
        hero_text.addStretch(1)

        hero_logo = QSvgWidget(str(LOGO_PATH))
        hero_logo.setFixedSize(220, 100)

        hero_layout.addLayout(hero_text, stretch=1)
        hero_layout.addWidget(hero_logo, alignment=Qt.AlignmentFlag.AlignCenter)

        cards_wrapper = QWidget()
        cards_layout = QGridLayout(cards_wrapper)
        cards_layout.setHorizontalSpacing(14)
        cards_layout.setVerticalSpacing(14)

        switcher_card = AnimatedCard("fa5s.broadcast-tower", "Switcher Source", "Choose OBS Studio or vMix and set the correct host endpoint.")
        midi_card = AnimatedCard("fa5s.sliders-h", "Hardware Routing", "Use Arduino MIDI in production or shortcut simulation in development mode.")
        layout_card = AnimatedCard("fa5s.th-large", "Interface Layout", "Select the scene grid size before moving into the main dashboard.")
        self.config_cards = [switcher_card, midi_card, layout_card]

        cards_layout.addWidget(switcher_card, 0, 0)
        cards_layout.addWidget(midi_card, 0, 1)
        cards_layout.addWidget(layout_card, 0, 2)

        form_shell = QFrame()
        form_shell.setObjectName("Panel")
        form_layout = QGridLayout(form_shell)
        form_layout.setContentsMargins(22, 22, 22, 22)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(12)

        self.switcher_type = QComboBox()
        self.switcher_type.addItems(["obs", "vmix"])
        self.switcher_type.currentTextChanged.connect(self._on_switcher_changed)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Switcher host")

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("OBS WebSocket password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.midi_selector = QComboBox()
        self.channel_selector = QComboBox()
        self.channel_selector.addItems(["4", "8", "12"])
        self.channel_selector.currentTextChanged.connect(self._on_channel_changed)

        labels = [
            QLabel("Switcher Type"),
            QLabel("Host"),
            QLabel("Port"),
            QLabel("OBS Password"),
            QLabel("MIDI Port"),
            QLabel("Scene Grid"),
        ]
        for label in labels:
            label.setObjectName("FieldLabel")

        form_layout.addWidget(labels[0], 0, 0)
        form_layout.addWidget(self.switcher_type, 1, 0)
        form_layout.addWidget(labels[1], 0, 1)
        form_layout.addWidget(self.host_input, 1, 1)
        form_layout.addWidget(labels[2], 0, 2)
        form_layout.addWidget(self.port_input, 1, 2)
        form_layout.addWidget(labels[3], 2, 0)
        form_layout.addWidget(self.password_input, 3, 0)
        form_layout.addWidget(labels[4], 2, 1)
        form_layout.addWidget(self.midi_selector, 3, 1)
        form_layout.addWidget(labels[5], 2, 2)
        form_layout.addWidget(self.channel_selector, 3, 2)

        footer = QHBoxLayout()
        footer.setSpacing(10)
        self.config_mode_note = QLabel("Development mode enables keyboard test trigger without physical Arduino.")
        self.config_mode_note.setObjectName("HintText")
        self.open_dashboard_btn = QPushButton("Open Main Dashboard")
        self.open_dashboard_btn.setObjectName("PrimaryBtn")
        self.open_dashboard_btn.setIcon(qta.icon("fa5s.rocket", color="#f8fbff"))
        self.open_dashboard_btn.clicked.connect(self.enter_dashboard)
        footer.addWidget(self.config_mode_note)
        footer.addStretch(1)
        footer.addWidget(self.open_dashboard_btn)

        page_layout.addWidget(hero)
        page_layout.addWidget(cards_wrapper)
        page_layout.addWidget(form_shell)
        page_layout.addLayout(footer)
        page_layout.addStretch(1)
        return page

    def _build_dashboard_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(14)

        scene_section = QFrame()
        scene_section.setObjectName("Panel")
        scene_layout = QVBoxLayout(scene_section)
        scene_layout.setContentsMargins(22, 22, 22, 22)
        scene_layout.setSpacing(14)

        scene_header = QHBoxLayout()
        scene_title = QLabel("Row 1 · Scene Control")
        scene_title.setObjectName("SectionTitle")
        scene_subtitle = QLabel("Program and preview status for each scene. In development mode, click or use shortcuts to simulate Arduino MIDI tally.")
        scene_subtitle.setObjectName("SectionSubtitle")
        scene_subtitle.setWordWrap(True)
        back_to_config = QPushButton("Config")
        back_to_config.setObjectName("GhostBtn")
        back_to_config.setIcon(qta.icon("fa5s.cog", color="#d8e5ff"))
        back_to_config.clicked.connect(self.back_to_config)
        self.connect_btn = QPushButton("Connect Switcher")
        self.connect_btn.setObjectName("PrimaryBtn")
        self.connect_btn.setIcon(qta.icon("fa5s.plug", color="#f8fbff"))
        self.connect_btn.clicked.connect(self.toggle_connection)

        title_col = QVBoxLayout()
        title_col.addWidget(scene_title)
        title_col.addWidget(scene_subtitle)
        scene_header.addLayout(title_col, stretch=1)
        scene_header.addWidget(back_to_config)
        scene_header.addWidget(self.connect_btn)

        self.scene_grid_shell = QWidget()
        self.scene_grid = QGridLayout(self.scene_grid_shell)
        self.scene_grid.setHorizontalSpacing(14)
        self.scene_grid.setVerticalSpacing(14)

        scene_layout.addLayout(scene_header)
        scene_layout.addWidget(self.scene_grid_shell)

        transition_section = QFrame()
        transition_section.setObjectName("Panel")
        transition_layout = QVBoxLayout(transition_section)
        transition_layout.setContentsMargins(22, 22, 22, 22)
        transition_layout.setSpacing(14)

        transition_header = QHBoxLayout()
        transition_title = QLabel("Row 2 · Transition Control")
        transition_title.setObjectName("SectionTitle")
        transition_subtitle = QLabel("Trigger cut, fade, mix, or stinger transition presets. These are visual presets for test mode and operator workflow guidance.")
        transition_subtitle.setObjectName("SectionSubtitle")
        transition_subtitle.setWordWrap(True)

        title_col_2 = QVBoxLayout()
        title_col_2.addWidget(transition_title)
        title_col_2.addWidget(transition_subtitle)
        transition_header.addLayout(title_col_2, stretch=1)

        self.transition_grid_shell = QWidget()
        self.transition_grid = QGridLayout(self.transition_grid_shell)
        self.transition_grid.setHorizontalSpacing(14)
        self.transition_grid.setVerticalSpacing(14)

        transition_layout.addLayout(transition_header)
        transition_layout.addWidget(self.transition_grid_shell)

        self.log_drawer = QFrame()
        self.log_drawer.setObjectName("LogDrawer")
        self.log_drawer.setMaximumHeight(0)
        self.log_drawer_layout = QVBoxLayout(self.log_drawer)
        self.log_drawer_layout.setContentsMargins(18, 16, 18, 16)
        self.log_drawer_layout.setSpacing(12)

        log_header = QHBoxLayout()
        log_title = QLabel("System Log")
        log_title.setObjectName("SectionTitle")
        self.toggle_log_btn = QPushButton("Show Log")
        self.toggle_log_btn.setObjectName("GhostBtn")
        self.toggle_log_btn.setIcon(qta.icon("fa5s.chevron-up", color="#dce9ff"))
        self.toggle_log_btn.clicked.connect(self.toggle_log_drawer)
        self.clear_log_btn = QPushButton("Clear")
        self.clear_log_btn.setObjectName("GhostBtn")
        self.clear_log_btn.setIcon(qta.icon("fa5s.trash-alt", color="#dce9ff"))
        self.clear_log_btn.clicked.connect(lambda: self.log_area.clear())
        log_header.addWidget(log_title)
        log_header.addStretch(1)
        log_header.addWidget(self.clear_log_btn)
        log_header.addWidget(self.toggle_log_btn)

        self.log_area = QTextEdit()
        self.log_area.setObjectName("LogArea")
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(180)

        self.log_launch_btn = QPushButton("Show Log Panel")
        self.log_launch_btn.setObjectName("GhostBtn")
        self.log_launch_btn.setIcon(qta.icon("fa5s.terminal", color="#dce9ff"))
        self.log_launch_btn.clicked.connect(self.toggle_log_drawer)

        self.log_drawer_layout.addLayout(log_header)
        self.log_drawer_layout.addWidget(self.log_area)

        page_layout.addWidget(scene_section)
        page_layout.addWidget(transition_section)
        page_layout.addWidget(self.log_launch_btn, alignment=Qt.AlignmentFlag.AlignRight)
        page_layout.addWidget(self.log_drawer)
        return page

    def _load_saved_values_into_fields(self) -> None:
        self.switcher_type.setCurrentText(self.runtime_config.switcher_type)
        self.host_input.setText(self.runtime_config.host)
        self.port_input.setText(str(self.runtime_config.port))
        self.password_input.setText(self.runtime_config.obs_password)
        self.channel_selector.setCurrentText(str(self.runtime_config.channel_count))
        self._on_switcher_changed(self.runtime_config.switcher_type)

    def _bind_shortcuts(self) -> None:
        for scene_id in range(1, 9):
            QShortcut(QKeySequence(str(scene_id)), self, activated=lambda scene=scene_id: self.controller.trigger_dev_shortcut(scene, "program"))
            QShortcut(QKeySequence(f"Ctrl+{scene_id}"), self, activated=lambda scene=scene_id: self.controller.trigger_dev_shortcut(scene, "preview"))
            QShortcut(QKeySequence(f"Shift+{scene_id}"), self, activated=lambda scene=scene_id: self.controller.trigger_dev_shortcut(scene, "idle"))

    def _load_midi_ports(self) -> None:
        self.midi_selector.clear()
        ports = self.controller.list_midi_ports()
        if not ports:
            self.midi_selector.addItem("No MIDI ports detected")
            return
        self.midi_selector.addItems(ports)
        match = self.midi_selector.findText(self.runtime_config.midi_port_name)
        if match >= 0:
            self.midi_selector.setCurrentIndex(match)

    def _render_scene_cards(self) -> None:
        while self.scene_grid.count():
            item = self.scene_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.scene_cards.clear()

        count = int(self.channel_selector.currentText())
        columns = 2 if count <= 4 else 4 if count <= 8 else 6
        for scene_id in range(1, count + 1):
            card = SceneCard(scene_id)
            card.clicked.connect(lambda _=False, scene=scene_id: self._cycle_scene(scene))
            row = (scene_id - 1) // columns
            column = (scene_id - 1) % columns
            self.scene_grid.addWidget(card, row, column)
            self.scene_cards[scene_id] = card

    def _render_transition_cards(self) -> None:
        while self.transition_grid.count():
            item = self.transition_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.transition_cards.clear()

        presets = [
            ("Cut", "fa5s.bolt", "Instant transition for fast tally switching."),
            ("Fade", "fa5s.adjust", "Soft dissolve transition with balanced timing."),
            ("Mix", "fa5s.layer-group", "Operator mix preset for multi-camera rehearsal."),
            ("Stinger", "fa5s.magic", "Graphic driven transition reference preset."),
        ]
        for index, (name, icon_name, description) in enumerate(presets):
            card = TransitionCard(name, icon_name, description)
            card.clicked.connect(lambda checked=False, transition=name: self.set_active_transition(transition))
            self.transition_grid.addWidget(card, 0, index)
            self.transition_cards.append(card)
        if self.transition_cards:
            self.transition_cards[0].setChecked(True)

    def _animate_window_entry(self) -> None:
        self.setWindowOpacity(0.0)
        self.window_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self.window_anim.setDuration(380)
        self.window_anim.setStartValue(0.0)
        self.window_anim.setEndValue(1.0)
        self.window_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.window_anim.start()

    def _animate_config_phase(self) -> None:
        self.config_card_animations = []
        for index, card in enumerate(self.config_cards):
            card.effect.setOpacity(0.0)
            anim = QPropertyAnimation(card.effect, b"opacity", self)
            anim.setDuration(360)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.config_card_animations.append(anim)
            QTimer.singleShot(index * 170, anim.start)

    def _animate_stack_change(self) -> None:
        current = self.stack.currentWidget()
        effect = QGraphicsOpacityEffect(current)
        current.setGraphicsEffect(effect)
        effect.setOpacity(0.0)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(280)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self.page_anim = anim

    def _cycle_scene(self, scene_id: int) -> None:
        if self.runtime_config.app_mode.lower() != "development":
            return
        card = self.scene_cards.get(scene_id)
        if not card:
            return
        next_state = "preview"
        if card.scene_state == "preview":
            next_state = "program"
        elif card.scene_state == "program":
            next_state = "idle"
        self.controller.trigger_dev_shortcut(scene_id, next_state)

    def _save_config(self) -> None:
        self.config_store.set_value("switcher_type", self.switcher_type.currentText())
        self.config_store.set_value("host", self.host_input.text().strip())
        self.config_store.set_value("port", int(self.port_input.text().strip() or "0"))
        self.config_store.set_value("obs_password", self.password_input.text())
        self.config_store.set_value("midi_port_name", self.midi_selector.currentText())
        self.config_store.set_value("channel_count", int(self.channel_selector.currentText()))

    def _sync_runtime_config(self) -> bool:
        try:
            port = int(self.port_input.text().strip())
        except ValueError:
            self.add_log("Invalid port configuration")
            return False
        self.runtime_config.switcher_type = self.switcher_type.currentText().lower()
        self.runtime_config.host = self.host_input.text().strip()
        self.runtime_config.port = port
        self.runtime_config.obs_password = self.password_input.text()
        self.runtime_config.midi_port_name = self.midi_selector.currentText()
        self.runtime_config.channel_count = int(self.channel_selector.currentText())
        self.controller.config = self.runtime_config
        self._save_config()
        return True

    def enter_dashboard(self) -> None:
        if not self._sync_runtime_config():
            return
        self.stack.setCurrentWidget(self.dashboard_page)
        self._animate_stack_change()
        self._render_scene_cards()
        self.add_log("Configuration phase completed")

    def back_to_config(self) -> None:
        self.stack.setCurrentWidget(self.config_page)
        self._animate_stack_change()
        self._animate_config_phase()

    def _on_switcher_changed(self, switcher: str) -> None:
        is_obs = switcher == "obs"
        self.password_input.setVisible(is_obs)
        self.password_input.setEnabled(is_obs)
        if is_obs and self.port_input.text().strip() == "8088":
            self.port_input.setText("4455")
        if not is_obs and self.port_input.text().strip() == "4455":
            self.port_input.setText("8088")

    def _on_channel_changed(self, value: str) -> None:
        self.runtime_config.channel_count = int(value)
        self.controller.config.channel_count = self.runtime_config.channel_count
        self._render_scene_cards()

    def toggle_connection(self) -> None:
        if not self._sync_runtime_config():
            return
        if self.connected:
            self.controller.disconnect()
            return
        if self.controller.connect():
            self.add_log(f"Connected to {self.runtime_config.switcher_type.upper()} at {self.runtime_config.host}:{self.runtime_config.port}")
        else:
            self.add_log("Connection attempt failed")

    def set_active_transition(self, transition_name: str) -> None:
        for card in self.transition_cards:
            card.setChecked(card.transition_name == transition_name)
        self.add_log(f"Transition preset selected: {transition_name}")

    def update_scene_state(self, scene_id: int, state: str) -> None:
        card = self.scene_cards.get(scene_id)
        if card:
            card.set_state(state)

    def on_connection_change(self, connected: bool) -> None:
        self.connected = connected
        if connected:
            self.status_badge.setText("CONNECTED")
            self.status_badge.setProperty("kind", "success")
            self.connect_btn.setText("Disconnect Switcher")
            self.connect_btn.setObjectName("DangerBtn")
            self.connect_btn.setIcon(qta.icon("fa5s.power-off", color="#fff4f5"))
            self.top_reconnect.setText("Disconnect")
            self.top_reconnect.setIcon(qta.icon("fa5s.power-off", color="#dbe8ff"))
        else:
            self.status_badge.setText("STANDBY")
            self.status_badge.setProperty("kind", "idle")
            self.connect_btn.setText("Connect Switcher")
            self.connect_btn.setObjectName("PrimaryBtn")
            self.connect_btn.setIcon(qta.icon("fa5s.plug", color="#f8fbff"))
            self.top_reconnect.setText("Reconnect")
            self.top_reconnect.setIcon(qta.icon("fa5s.sync-alt", color="#dbe8ff"))
            for card in self.scene_cards.values():
                card.set_state("idle")
        for widget in [self.status_badge, self.connect_btn]:
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

    def toggle_log_drawer(self) -> None:
        self.log_open = not self.log_open
        end_height = 276 if self.log_open else 0
        self.log_anim = QPropertyAnimation(self.log_drawer, b"maximumHeight", self)
        self.log_anim.setDuration(280)
        self.log_anim.setStartValue(self.log_drawer.maximumHeight())
        self.log_anim.setEndValue(end_height)
        self.log_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.log_anim.start()
        self.toggle_log_btn.setText("Hide Log" if self.log_open else "Show Log")
        icon_name = "fa5s.chevron-down" if self.log_open else "fa5s.chevron-up"
        self.toggle_log_btn.setIcon(qta.icon(icon_name, color="#dce9ff"))
        self.log_launch_btn.setText("Hide Log Panel" if self.log_open else "Show Log Panel")

    def add_log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")

    def closeEvent(self, event) -> None:
        self.controller.disconnect()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if qdarktheme:
        qdarktheme.setup_theme("dark")
    else:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())

    splash = SplashScreen()
    splash.show()

    window = MainWindow()

    def reveal_main_window() -> None:
        splash.close()
        window.show()

    QTimer.singleShot(2200, reveal_main_window)
    sys.exit(app.exec())
