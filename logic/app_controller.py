import os
import threading
import time
from dataclasses import dataclass
from typing import Optional

import mido
from PyQt6.QtCore import QObject, pyqtSignal

from logic.switcher_clients import OBSClient, SwitcherClientBase, SwitcherState, VMixClient


@dataclass
class AppRuntimeConfig:
    app_mode: str
    switcher_type: str
    host: str
    port: int
    obs_password: str
    midi_port_name: str
    channel_count: int


class AppController(QObject):
    tally_update = pyqtSignal(int, str)
    log_signal = pyqtSignal(str)
    connection_status = pyqtSignal(bool)

    def __init__(self, config: AppRuntimeConfig):
        super().__init__()
        self.config = config
        self.switcher: Optional[SwitcherClientBase] = None
        self.midi_port = None
        self.connected = False
        self.running = False
        self.poll_thread: Optional[threading.Thread] = None
        self.current_program: Optional[int] = None
        self.current_preview: Optional[int] = None

    @property
    def is_production(self) -> bool:
        return self.config.app_mode.lower() == "production"

    def list_midi_ports(self) -> list[str]:
        try:
            return mido.get_output_names()
        except Exception as exc:
            self.log_signal.emit(f"MIDI error: {exc}")
            return []

    def connect(self) -> bool:
        try:
            self.switcher = self._build_switcher()
            self.switcher.connect()
            self.log_signal.emit(f"Connected to {self.config.switcher_type.upper()} at {self.config.host}:{self.config.port}")

            if self.is_production:
                if not self._connect_midi(self.config.midi_port_name):
                    self.switcher.disconnect()
                    self.switcher = None
                    self.connection_status.emit(False)
                    return False
            else:
                self.log_signal.emit("Development mode active: MIDI hardware is optional and shortcut test is enabled")

            self.connected = True
            self.connection_status.emit(True)
            self._start_polling()
            return True
        except Exception as exc:
            self.log_signal.emit(f"Connection failed: {exc}")
            self.connection_status.emit(False)
            return False

    def _build_switcher(self) -> SwitcherClientBase:
        switcher = self.config.switcher_type.lower()
        if switcher == "vmix":
            return VMixClient(self.config.host, self.config.port)
        return OBSClient(self.config.host, self.config.port, self.config.obs_password)

    def _connect_midi(self, port_name: str) -> bool:
        try:
            ports = self.list_midi_ports()
            if port_name not in ports:
                self.log_signal.emit(f"MIDI port '{port_name}' not available")
                return False
            self.midi_port = mido.open_output(port_name)
            self.log_signal.emit(f"MIDI connected: {port_name}")
            return True
        except Exception as exc:
            self.log_signal.emit(f"MIDI connect failed: {exc}")
            return False

    def _start_polling(self) -> None:
        if self.poll_thread and self.poll_thread.is_alive():
            return
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()

    def _poll_loop(self) -> None:
        while self.running and self.switcher:
            try:
                state = self.switcher.get_state()
                self._apply_state(state)
            except Exception as exc:
                self.log_signal.emit(f"Polling error: {exc}")
            time.sleep(0.35)

    def _apply_state(self, state: SwitcherState) -> None:
        if state.program != self.current_program:
            if self.current_program:
                self._emit_camera(self.current_program, "idle")
            self.current_program = state.program
            if state.program:
                self._emit_camera(state.program, "program")

        if state.preview != self.current_preview:
            if self.current_preview and self.current_preview != self.current_program:
                self._emit_camera(self.current_preview, "idle")
            self.current_preview = state.preview
            if state.preview and state.preview != self.current_program:
                self._emit_camera(state.preview, "preview")

    def _emit_camera(self, cam_id: int, mode: str) -> None:
        if not 1 <= cam_id <= self.config.channel_count:
            return

        self.tally_update.emit(cam_id, mode)

        if self.is_production and self.midi_port:
            try:
                if mode == "program":
                    self.midi_port.send(mido.Message("note_on", note=cam_id, velocity=127))
                elif mode == "preview":
                    self.midi_port.send(mido.Message("note_on", note=cam_id + 10, velocity=127))
                elif mode == "idle":
                    self.midi_port.send(mido.Message("note_off", note=cam_id, velocity=0))
                    self.midi_port.send(mido.Message("note_off", note=cam_id + 10, velocity=0))
            except Exception as exc:
                self.log_signal.emit(f"MIDI send failed: {exc}")

    def trigger_dev_shortcut(self, cam_id: int, mode: str) -> None:
        if self.is_production:
            self.log_signal.emit("Dev shortcut ignored in production mode")
            return

        if mode not in {"program", "preview", "idle"}:
            return

        self._emit_camera(cam_id, mode)
        self.log_signal.emit(f"Shortcut trigger CAM {cam_id}: {mode.upper()}")

    def disconnect(self) -> None:
        self.running = False
        self.connected = False

        if self.switcher:
            try:
                self.switcher.disconnect()
            except Exception:
                pass
            self.switcher = None

        if self.midi_port:
            try:
                self.midi_port.close()
            except Exception:
                pass
            self.midi_port = None

        self.connection_status.emit(False)
        self.log_signal.emit("Disconnected")


def load_runtime_config() -> AppRuntimeConfig:
    switcher_type = os.getenv("SWITCHER_TYPE", "obs").lower()
    host = os.getenv("OBS_HOST", "localhost") if switcher_type == "obs" else os.getenv("VMIX_HOST", "localhost")
    default_port = 4455 if switcher_type == "obs" else 8088
    port = int(os.getenv("OBS_PORT", default_port)) if switcher_type == "obs" else int(os.getenv("VMIX_PORT", default_port))

    return AppRuntimeConfig(
        app_mode=os.getenv("APP_MODE", "development"),
        switcher_type=switcher_type,
        host=host,
        port=port,
        obs_password=os.getenv("OBS_PASSWORD", ""),
        midi_port_name=os.getenv("MIDI_PORT_NAME", "Arduino MIDI"),
        channel_count=int(os.getenv("CHANNEL_COUNT", "8")),
    )
