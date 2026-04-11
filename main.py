import os
import sys
import time
from pathlib import Path
from typing import Dict

import qtawesome as qta
from dotenv import load_dotenv
from PyQt6.QtGui import (
    QAction,
    QActionGroup,
    QColor,
    QDesktopServices,
    QFont,
    QKeySequence,
    QShortcut,
)
from PyQt6.QtCore import (
    QEasingCurve, QPoint, QPropertyAnimation,
    QSequentialAnimationGroup, QSize, Qt, QTimer, QUrl, pyqtSignal,
)
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from logic.app_controller import AppController, AppRuntimeConfig, load_runtime_config
from logic.config_store import ConfigStore
from styles.modern_styles import get_dynamic_qss


load_dotenv()
LOGO_PATH = Path(__file__).parent / "res" / "logo_swm.svg"


def _is_dark_mode() -> bool:
    """Detect OS color scheme. Returns True for Dark, False for Light/Unknown."""
    try:
        hints = QApplication.styleHints()
        scheme = hints.colorScheme()
        return scheme == Qt.ColorScheme.Dark
    except AttributeError:
        palette = QApplication.palette()
        return palette.window().color().lightness() < 128


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
        shell_layout.setContentsMargins(40, 32, 40, 32)
        shell_layout.setSpacing(10)
        shell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo with drop-shadow glow
        logo_wrap = QWidget()
        logo_wrap_layout = QHBoxLayout(logo_wrap)
        logo_wrap_layout.setContentsMargins(0, 0, 0, 0)
        self.logo = QSvgWidget(str(LOGO_PATH))
        self.logo.setFixedSize(260, 116)
        glow = QGraphicsDropShadowEffect(self.logo)
        glow.setBlurRadius(36)
        glow.setColor(QColor("#47d0ff"))
        glow.setOffset(0, 0)
        self.logo.setGraphicsEffect(glow)
        logo_wrap_layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)

        self.boot_title = QLabel("GOLDENBOY")
        self.boot_title.setObjectName("SplashTitle")
        self.boot_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.boot_divider = QFrame()
        self.boot_divider.setObjectName("SplashDivider")
        self.boot_divider.setFixedHeight(2)

        self.boot_subtitle = QLabel("Professional Broadcast Control Suite")
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

        # Opacity effects for fade-in elements
        self._title_effect = QGraphicsOpacityEffect(self.boot_title)
        self._title_effect.setOpacity(0.0)
        self.boot_title.setGraphicsEffect(self._title_effect)

        self._sub_effect = QGraphicsOpacityEffect(self.boot_subtitle)
        self._sub_effect.setOpacity(0.0)
        self.boot_subtitle.setGraphicsEffect(self._sub_effect)

        self._status_effect = QGraphicsOpacityEffect(self.status)
        self._status_effect.setOpacity(0.0)
        self.status.setGraphicsEffect(self._status_effect)

        self._divider_effect = QGraphicsOpacityEffect(self.boot_divider)
        self._divider_effect.setOpacity(0.0)
        self.boot_divider.setGraphicsEffect(self._divider_effect)

        shell_layout.addStretch(1)
        shell_layout.addWidget(logo_wrap, alignment=Qt.AlignmentFlag.AlignCenter)
        shell_layout.addSpacing(12)
        shell_layout.addWidget(self.boot_title)
        shell_layout.addWidget(self.boot_divider)
        shell_layout.addSpacing(2)
        shell_layout.addWidget(self.boot_subtitle)
        shell_layout.addSpacing(16)
        shell_layout.addWidget(self.progress_frame)
        shell_layout.addSpacing(8)
        shell_layout.addWidget(self.status)
        shell_layout.addStretch(1)

        outer.addWidget(shell)
        self.setWindowOpacity(0.0)

    def _start_animation(self) -> None:
        # Stage 1: Window fade-in (0 → 1, 250ms)
        self.fade = QPropertyAnimation(self, b"windowOpacity", self)
        self.fade.setDuration(250)
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(1.0)
        self.fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade.start()

        # Stage 2: Title fade-in (delay 200ms)
        QTimer.singleShot(200, self._fade_in_title)

        # Stage 3: Divider fade-in (delay 350ms)
        QTimer.singleShot(350, lambda: self._fade_effect(self._divider_effect, 250))

        # Stage 4: Subtitle fade-in (delay 480ms)
        QTimer.singleShot(480, lambda: self._fade_effect(self._sub_effect, 280))

        # Stage 5: Progress bar expands (delay 600ms, duration 1600ms elastic)
        QTimer.singleShot(600, self._start_progress)

        # Stage 6: Status fade-in + messages (delay 700ms)
        QTimer.singleShot(700, lambda: self._fade_effect(self._status_effect, 220))
        messages = [
            "Initializing switcher runtime",
            "Loading SQLite configuration store",
            "Preparing scene and transition panels",
            "OBS WebSocket driver ready",
            "Launching control interface…",
        ]
        for index, message in enumerate(messages, start=1):
            QTimer.singleShot(700 + index * 290, lambda text=message: self.status.setText(text))

    def _fade_effect(self, effect: QGraphicsOpacityEffect, duration: int) -> None:
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        # keep reference so it isn't GC'd
        self._anims = getattr(self, "_anims", [])
        self._anims.append(anim)

    def _fade_in_title(self) -> None:
        self._fade_effect(self._title_effect, 300)

    def _start_progress(self) -> None:
        self.progress_anim = QPropertyAnimation(self.progress_bar, b"maximumWidth", self)
        self.progress_anim.setDuration(1600)
        self.progress_anim.setStartValue(0)
        self.progress_anim.setEndValue(500)
        self.progress_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.progress_anim.start()


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
    # Signals for context-menu actions
    set_as_program = pyqtSignal(str)   # emits scene_name
    set_as_preview = pyqtSignal(str)   # emits scene_name

    def __init__(self, scene_id: int, scene_name: str = ""):
        super().__init__()
        self.scene_id = scene_id
        self.scene_name = scene_name or f"SCENE {scene_id}"
        self.scene_state = "idle"
        self.setObjectName("SceneCard")
        self.setProperty("state", "idle")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self._build_text()

    def _build_text(self) -> None:
        state_label = {
            "idle": "STANDBY",
            "preview": "PREVIEW",
            "program": "PROGRAM",
        }.get(self.scene_state, "STANDBY")
        display_name = self.scene_name
        if len(display_name) > 16:
            display_name = display_name[:14] + "…"
        self.setText(f"{display_name}\n{state_label}")

    def set_state(self, state: str) -> None:
        self.scene_state = state
        self.setProperty("state", state)
        self._build_text()
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _show_context_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.setObjectName("SceneContextMenu")
        act_prog = menu.addAction("Set as Program")
        act_prev = menu.addAction("Set as Preview")
        menu.addSeparator()
        act_info = menu.addAction(f"Scene: {self.scene_name}")
        act_info.setEnabled(False)
        chosen = menu.exec(self.mapToGlobal(pos))
        if chosen == act_prog:
            self.set_as_program.emit(self.scene_name)
        elif chosen == act_prev:
            self.set_as_preview.emit(self.scene_name)


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
        self.controller.obs_scenes_loaded.connect(self._update_obs_scenes)
        self.controller.scene_name_update.connect(self.update_scene_by_name)

        self.scene_cards: Dict[int, SceneCard] = {}
        self.scene_cards_by_name: Dict[str, SceneCard] = {}
        self.transition_cards: list[TransitionCard] = []
        self.config_cards: list[AnimatedCard] = []
        self.config_card_animations: list[QPropertyAnimation] = []
        self.connected = False
        self.log_open = False
        self._obs_scene_labels: list[QLabel] = []
        self._theme_preference: str = "system"  # "dark" | "light" | "system"

        self.setWindowTitle(os.getenv("APP_NAME", "GOLDENBOY"))
        self.setMinimumSize(820, 580)
        self.resize(1360, 860)
        self._build_ui()
        self._build_menu_bar()
        self._setup_system_theme()
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

    # ── Theme ──────────────────────────────────────────────────────────────

    def _setup_system_theme(self) -> None:
        """Apply initial theme and wire dynamic OS theme-change signal."""
        self._apply_theme(self._theme_preference)
        try:
            QApplication.styleHints().colorSchemeChanged.connect(
                lambda _: self._apply_theme(self._theme_preference)
            )
        except AttributeError:
            pass  # Qt < 6.5 does not emit colorSchemeChanged

    def _apply_theme(self, preference: str) -> None:
        """Apply QSS at application level so menus and dialogs also receive new theme.

        preference: "dark" | "light" | "system"
        """
        self._theme_preference = preference
        if preference == "dark":
            dark = True
        elif preference == "light":
            dark = False
        else:
            dark = _is_dark_mode()
        qss = get_dynamic_qss(dark)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss)  # covers menus, dialogs, tooltips
        self.setStyleSheet(qss)     # forces window repaint
        # Re-polish icon tints to match theme luminance
        icon_col = "#dbe8ff" if dark else "#1a3060"
        if hasattr(self, "top_reconnect"):
            self.top_reconnect.setIcon(qta.icon("fa5s.sync-alt", color=icon_col))

    # ── Menu Bar ──────────────────────────────────────────────────────────

    def _build_menu_bar(self) -> None:
        """Build a full native menu bar covering File, Edit, Section, View, Log, Help."""
        bar: QMenuBar = self.menuBar()

        # ── File ──────────────────────────────────────────────────────────
        file_menu: QMenu = bar.addMenu("&File")

        new_action = QAction("&New Configuration", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Reset all fields to defaults")
        new_action.triggered.connect(self._menu_new_config)
        file_menu.addAction(new_action)

        open_action = QAction("&Open Configuration…", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Load configuration from a JSON file")
        open_action.triggered.connect(self._menu_open_config)
        file_menu.addAction(open_action)

        save_action = QAction("&Save Configuration", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip("Save current configuration to database")
        save_action.triggered.connect(self._save_config)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Configuration &As…", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.setStatusTip("Export current configuration to a JSON file")
        save_as_action.triggered.connect(self._menu_save_as_config)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        import_action = QAction("&Import Settings…", self)
        import_action.setStatusTip("Import settings from a JSON file")
        import_action.triggered.connect(self._menu_import_settings)
        file_menu.addAction(import_action)

        export_action = QAction("&Export Settings…", self)
        export_action.setStatusTip("Export all settings to a JSON file")
        export_action.triggered.connect(self._menu_export_settings)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.setStatusTip("Quit GoldenBoy")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # ── Edit ──────────────────────────────────────────────────────────
        edit_menu: QMenu = bar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.setEnabled(False)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.setEnabled(False)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(lambda: QApplication.focusWidget() and getattr(QApplication.focusWidget(), "cut", lambda: None)())
        edit_menu.addAction(cut_action)

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(lambda: QApplication.focusWidget() and getattr(QApplication.focusWidget(), "copy", lambda: None)())
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(lambda: QApplication.focusWidget() and getattr(QApplication.focusWidget(), "paste", lambda: None)())
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(lambda: QApplication.focusWidget() and getattr(QApplication.focusWidget(), "selectAll", lambda: None)())
        edit_menu.addAction(select_all_action)

        edit_menu.addSeparator()

        prefs_action = QAction("&Preferences…", self)
        prefs_action.setShortcut(QKeySequence("Ctrl+,"))
        prefs_action.setStatusTip("Open application preferences")
        prefs_action.triggered.connect(self._menu_preferences)
        edit_menu.addAction(prefs_action)

        # ── Section ───────────────────────────────────────────────────────
        section_menu: QMenu = bar.addMenu("&Section")

        config_phase_action = QAction("&Configuration Phase", self)
        config_phase_action.setShortcut(QKeySequence("Ctrl+1"))
        config_phase_action.setStatusTip("Switch to the configuration phase screen")
        config_phase_action.triggered.connect(self.back_to_config)
        section_menu.addAction(config_phase_action)

        dashboard_action = QAction("&Main Dashboard", self)
        dashboard_action.setShortcut(QKeySequence("Ctrl+2"))
        dashboard_action.setStatusTip("Switch to the main dashboard screen")
        dashboard_action.triggered.connect(self.enter_dashboard)
        section_menu.addAction(dashboard_action)

        section_menu.addSeparator()

        obs_fetch_action = QAction("&Refresh OBS Scenes", self)
        obs_fetch_action.setShortcut(QKeySequence("Ctrl+R"))
        obs_fetch_action.setStatusTip("Re-fetch the scene list from OBS WebSocket")
        obs_fetch_action.triggered.connect(lambda: self.controller.fetch_obs_scenes())
        section_menu.addAction(obs_fetch_action)

        obs_connect_action = QAction("Connect / Disconnect Switcher", self)
        obs_connect_action.setStatusTip("Toggle connection to the configured switcher")
        obs_connect_action.triggered.connect(self.toggle_connection)
        section_menu.addAction(obs_connect_action)

        section_menu.addSeparator()

        scene_grid_action = QAction("Render Scene &Grid", self)
        scene_grid_action.setStatusTip("Re-render the scene control grid")
        scene_grid_action.triggered.connect(self._render_scene_cards)
        section_menu.addAction(scene_grid_action)

        transition_action = QAction("Render &Transitions", self)
        transition_action.setStatusTip("Re-render the transition preset cards")
        transition_action.triggered.connect(self._render_transition_cards)
        section_menu.addAction(transition_action)

        # ── View ──────────────────────────────────────────────────────────
        view_menu: QMenu = bar.addMenu("&View")

        fullscreen_action = QAction("Toggle &Full Screen", self)
        fullscreen_action.setShortcut(QKeySequence.StandardKey.FullScreen)
        fullscreen_action.setStatusTip("Toggle full-screen mode")
        fullscreen_action.triggered.connect(self._menu_toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        view_menu.addSeparator()

        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(lambda: self._menu_zoom(1))
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(lambda: self._menu_zoom(-1))
        view_menu.addAction(zoom_out_action)

        zoom_reset_action = QAction("&Reset Zoom", self)
        zoom_reset_action.setShortcut(QKeySequence("Ctrl+0"))
        zoom_reset_action.triggered.connect(lambda: self._menu_zoom(0))
        view_menu.addAction(zoom_reset_action)

        view_menu.addSeparator()

        # Theme submenu
        theme_menu: QMenu = view_menu.addMenu("&Theme")
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)

        dark_theme_action = QAction("&Dark", self)
        dark_theme_action.setCheckable(True)
        dark_theme_action.triggered.connect(lambda: self._apply_theme("dark"))
        theme_group.addAction(dark_theme_action)
        theme_menu.addAction(dark_theme_action)

        light_theme_action = QAction("&Light", self)
        light_theme_action.setCheckable(True)
        light_theme_action.triggered.connect(lambda: self._apply_theme("light"))
        theme_group.addAction(light_theme_action)
        theme_menu.addAction(light_theme_action)

        system_theme_action = QAction("&Follow System", self)
        system_theme_action.setCheckable(True)
        system_theme_action.setChecked(True)
        system_theme_action.triggered.connect(lambda: self._apply_theme("system"))
        theme_group.addAction(system_theme_action)
        theme_menu.addAction(system_theme_action)

        view_menu.addSeparator()

        compact_action = QAction("&Compact View", self)
        compact_action.setStatusTip("Reduce window to minimum comfortable size")
        compact_action.triggered.connect(lambda: self.resize(900, 640))
        view_menu.addAction(compact_action)

        expanded_action = QAction("&Expanded View", self)
        expanded_action.setStatusTip("Expand window to a spacious layout")
        expanded_action.triggered.connect(lambda: self.resize(1600, 1000))
        view_menu.addAction(expanded_action)

        # ── Log ───────────────────────────────────────────────────────────
        log_menu: QMenu = bar.addMenu("&Log")

        show_log_action = QAction("&Show / Hide Log Panel", self)
        show_log_action.setShortcut(QKeySequence("Ctrl+L"))
        show_log_action.setStatusTip("Toggle the system log drawer")
        show_log_action.triggered.connect(self.toggle_log_drawer)
        log_menu.addAction(show_log_action)

        clear_log_action = QAction("&Clear Log", self)
        clear_log_action.setShortcut(QKeySequence("Ctrl+Shift+L"))
        clear_log_action.setStatusTip("Clear all log entries")
        clear_log_action.triggered.connect(lambda: self.log_area.clear())
        log_menu.addAction(clear_log_action)

        save_log_action = QAction("Save Log to &File…", self)
        save_log_action.setStatusTip("Save log contents to a text file")
        save_log_action.triggered.connect(self._menu_save_log)
        log_menu.addAction(save_log_action)

        log_menu.addSeparator()

        # Log Level submenu
        log_level_menu: QMenu = log_menu.addMenu("Log &Level")
        log_level_group = QActionGroup(self)
        log_level_group.setExclusive(True)
        for level in ("Debug", "Info", "Warning", "Error"):
            lv_action = QAction(level, self)
            lv_action.setCheckable(True)
            lv_action.setChecked(level == "Info")
            lv_action.triggered.connect(lambda checked, lv=level: self.add_log(f"Log level set to {lv}"))
            log_level_group.addAction(lv_action)
            log_level_menu.addAction(lv_action)

        log_menu.addSeparator()

        copy_log_action = QAction("&Copy All Log", self)
        copy_log_action.setStatusTip("Copy all log text to clipboard")
        copy_log_action.triggered.connect(lambda: QApplication.clipboard().setText(self.log_area.toPlainText()))
        log_menu.addAction(copy_log_action)

        export_log_action = QAction("&Export Log…", self)
        export_log_action.setStatusTip("Export log to a file")
        export_log_action.triggered.connect(self._menu_save_log)
        log_menu.addAction(export_log_action)

        # ── Help ──────────────────────────────────────────────────────────
        help_menu: QMenu = bar.addMenu("&Help")

        docs_action = QAction("&Documentation", self)
        docs_action.setStatusTip("Open GoldenBoy documentation")
        docs_action.triggered.connect(lambda: self._menu_open_url("https://github.com/", "GoldenBoy Documentation"))
        help_menu.addAction(docs_action)

        obs_guide_action = QAction("OBS &WebSocket Guide", self)
        obs_guide_action.setStatusTip("OBS WebSocket protocol documentation")
        obs_guide_action.triggered.connect(lambda: self._menu_open_url("https://github.com/obsproject/obs-websocket", "OBS WebSocket"))
        help_menu.addAction(obs_guide_action)

        help_menu.addSeparator()

        about_action = QAction("&About GoldenBoy", self)
        about_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        about_action.triggered.connect(self._menu_about)
        help_menu.addAction(about_action)

        updates_action = QAction("Check for &Updates…", self)
        updates_action.triggered.connect(lambda: self.add_log("Update check not implemented yet"))
        help_menu.addAction(updates_action)

        help_menu.addSeparator()

        report_action = QAction("&Report Issue…", self)
        report_action.triggered.connect(lambda: self._menu_open_url("https://github.com/", "Report Issue"))
        help_menu.addAction(report_action)

        github_action = QAction("&GitHub Repository…", self)
        github_action.triggered.connect(lambda: self._menu_open_url("https://github.com/", "GitHub"))
        help_menu.addAction(github_action)

    # ── Menu action handlers ──────────────────────────────────────────────

    def _menu_new_config(self) -> None:
        reply = QMessageBox.question(
            self, "New Configuration",
            "Reset all configuration fields to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.host_input.setText("localhost")
            self.port_input.setText("4455")
            self.password_input.clear()
            self.switcher_type.setCurrentText("obs")
            self.add_log("Configuration reset to defaults")

    def _menu_open_config(self) -> None:
        import json
        path, _ = QFileDialog.getOpenFileName(self, "Open Configuration", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            for key, val in data.items():
                self.config_store.set_value(key, val)
            self.add_log(f"Configuration loaded from {path}")
            self.runtime_config = self._hydrate_runtime_config(self.runtime_config)
            self._load_saved_values_into_fields()
        except Exception as exc:
            QMessageBox.critical(self, "Load Error", f"Failed to load configuration:\n{exc}")

    def _menu_save_as_config(self) -> None:
        import json as _json
        path, _ = QFileDialog.getSaveFileName(self, "Save Configuration As", "goldenboy_config.json", "JSON Files (*.json)")
        if not path:
            return
        keys = ["switcher_type", "host", "port", "obs_password", "midi_port_name", "channel_count"]
        data = self.config_store.get_many({k: "" for k in keys})
        try:
            with open(path, "w", encoding="utf-8") as fh:
                _json.dump(data, fh, indent=2)
            self.add_log(f"Configuration exported to {path}")
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", f"Failed to save configuration:\n{exc}")

    def _menu_import_settings(self) -> None:
        self._menu_open_config()

    def _menu_export_settings(self) -> None:
        self._menu_save_as_config()

    def _menu_preferences(self) -> None:
        QMessageBox.information(self, "Preferences", "Preferences panel coming soon.")

    def _menu_toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    _zoom_factor: float = 1.0

    def _menu_zoom(self, direction: int) -> None:
        """direction: 1=in, -1=out, 0=reset"""
        steps = {1: 1.15, -1: 1 / 1.15, 0: 1.0}
        factor = steps.get(direction, 1.0)
        if direction == 0:
            self._zoom_factor = 1.0
        else:
            self._zoom_factor = max(0.6, min(2.5, getattr(self, "_zoom_factor", 1.0) * factor))
        font = QApplication.font()
        base = 13
        font.setPointSizeF(base * self._zoom_factor)
        QApplication.setFont(font)

    def _menu_save_log(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Log", "goldenboy_log.txt", "Text Files (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self.log_area.toPlainText())
            self.add_log(f"Log saved to {path}")
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", f"Failed to save log:\n{exc}")

    def _menu_about(self) -> None:
        QMessageBox.about(
            self,
            "About GoldenBoy",
            "<h2>GoldenBoy Control Suite</h2>"
            "<p>Native broadcast control interface for OBS Studio and vMix.</p>"
            "<p>Version: 2.0 — OBS WebSocket Edition</p>"
            "<p>Built with PyQt6 and obsws-python.</p>",
        )

    def _menu_open_url(self, url: str, label: str) -> None:
        QDesktopServices.openUrl(QUrl(url))
        self.add_log(f"Opened {label}")

    # ── OBS Scene List ─────────────────────────────────────────────────────

    def _update_obs_scenes(self, scenes: list) -> None:
        """Rebuild the scene control grid with real OBS scene names."""
        # Update the info-panel label/badge (if the widget exists in layout)
        count = len(scenes)
        if hasattr(self, "obs_scene_count_badge"):
            self.obs_scene_count_badge.setText(f"{count} scene{'s' if count != 1 else ''}")
        if hasattr(self, "obs_scenes_hint"):
            self.obs_scenes_hint.setVisible(count == 0)

        # Rebuild the main scene control grid with real names
        self._render_scene_cards(scenes=scenes)
        self.add_log(f"Scene grid rebuilt with {count} OBS scene(s)")


    def _build_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        root = QWidget()
        scroll.setWidget(root)
        self.setCentralWidget(scroll)

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

        # ── OBS Scene List ─────────────────────────────────────────────
        self.obs_scenes_section = QFrame()
        self.obs_scenes_section.setObjectName("OBSScenesPanel")
        obs_layout = QVBoxLayout(self.obs_scenes_section)
        obs_layout.setContentsMargins(22, 18, 22, 18)
        obs_layout.setSpacing(10)

        obs_header = QHBoxLayout()
        obs_title = QLabel("OBS WebSocket · Scene Configuration")
        obs_title.setObjectName("SectionTitle")
        self.obs_scene_count_badge = QLabel("0 scenes")
        self.obs_scene_count_badge.setObjectName("ModeBadge")
        self.obs_refresh_btn = QPushButton("Refresh Scenes")
        self.obs_refresh_btn.setObjectName("GhostBtn")
        self.obs_refresh_btn.setIcon(qta.icon("fa5s.sync-alt", color="#dbe8ff"))
        self.obs_refresh_btn.clicked.connect(lambda: self.controller.fetch_obs_scenes())
        obs_header.addWidget(obs_title)
        obs_header.addStretch(1)
        obs_header.addWidget(self.obs_scene_count_badge)
        obs_header.addWidget(self.obs_refresh_btn)

        self.obs_scenes_grid = QGridLayout()
        self.obs_scenes_grid.setHorizontalSpacing(10)
        self.obs_scenes_grid.setVerticalSpacing(8)

        obs_hint = QLabel("Connect to OBS WebSocket to auto-load scene names and count.")
        obs_hint.setObjectName("HintText")
        obs_hint.setWordWrap(True)
        self.obs_scenes_hint = obs_hint

        obs_layout.addLayout(obs_header)
        obs_layout.addWidget(obs_hint)
        obs_layout.addLayout(self.obs_scenes_grid)

        page_layout.addWidget(self.obs_scenes_section)
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

    def _render_scene_cards(self, scenes: list[str] | None = None) -> None:
        """Rebuild scene control grid.

        If *scenes* is provided (real OBS names), cards are built from that
        list. Otherwise fall back to the configured numeric channel count.
        """
        while self.scene_grid.count():
            item = self.scene_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.scene_cards.clear()
        self.scene_cards_by_name.clear()

        if scenes is not None:
            count = len(scenes)
            columns = 2 if count <= 4 else 4 if count <= 8 else 6
            for idx, name in enumerate(scenes):
                scene_id = idx + 1
                card = SceneCard(scene_id, name)
                card.clicked.connect(lambda _=False, sid=scene_id: self._cycle_scene(sid))
                card.set_as_program.connect(self.controller.set_program_scene)
                card.set_as_preview.connect(self.controller.set_preview_scene)
                self.scene_grid.addWidget(card, idx // columns, idx % columns)
                self.scene_cards[scene_id] = card
                self.scene_cards_by_name[name] = card
        else:
            count = int(self.channel_selector.currentText())
            columns = 2 if count <= 4 else 4 if count <= 8 else 6
            for scene_id in range(1, count + 1):
                card = SceneCard(scene_id)
                card.clicked.connect(lambda _=False, scene=scene_id: self._cycle_scene(scene))
                card.set_as_program.connect(self.controller.set_program_scene)
                card.set_as_preview.connect(self.controller.set_preview_scene)
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
        self.controller.trigger_transition(transition_name)
        self.add_log(f"Transition preset selected: {transition_name}")

    def update_scene_state(self, scene_id: int, state: str) -> None:
        card = self.scene_cards.get(scene_id)
        if card:
            card.set_state(state)

    def update_scene_by_name(self, scene_name: str, state: str) -> None:
        """Slot for AppController.scene_name_update — updates card by real OBS name."""
        card = self.scene_cards_by_name.get(scene_name)
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
            # Auto-fetch OBS scenes shortly after connecting
            if self.runtime_config.switcher_type.lower() == "obs":
                QTimer.singleShot(600, lambda: self.controller.fetch_obs_scenes())
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

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # Reflow OBS scene labels into the optimal column count for the new width
        if self._obs_scene_labels:
            cols = max(1, min(6, self.width() // 220))
            for idx, lbl in enumerate(self._obs_scene_labels):
                self.obs_scenes_grid.addWidget(lbl, idx // cols, idx % cols)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName(os.getenv("APP_NAME", "GOLDENBOY"))
    app.setOrganizationName("GoldenBoy")

    # Apply initial system-matched stylesheet before any window is shown
    app.setStyleSheet(get_dynamic_qss(_is_dark_mode()))

    splash = SplashScreen()
    splash.show()

    window = MainWindow()

    def reveal_main_window() -> None:
        splash.close()
        window.show()

    QTimer.singleShot(2200, reveal_main_window)
    sys.exit(app.exec())
