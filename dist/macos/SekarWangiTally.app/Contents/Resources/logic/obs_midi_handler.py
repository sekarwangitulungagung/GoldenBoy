import os
import threading
import time
import logging
from PyQt6.QtCore import pyqtSignal, QObject
import mido
from obsws_python import ReqClient, events
from dotenv import load_dotenv

load_dotenv()

class OBSWorker(QObject):
    # Signal untuk update UI dari background thread
    tally_update = pyqtSignal(int, int)  # cam_id, state (0:idle, 1:live, 2:preview)
    log_signal = pyqtSignal(str)
    connection_status = pyqtSignal(bool)  # True jika connected, False jika disconnected

    def __init__(self):
        super().__init__()
        self.obs_client = None
        self.midi_port = None
        self.running = False
        self.current_program = None
        self.current_preview = None

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def connect_obs(self, host, port, password):
        try:
            self.obs_client = ReqClient(host=host, port=port, password=password)
            self.log_signal.emit("OBS WebSocket connected successfully")
            self.connection_status.emit(True)

            # Get initial scene info
            self.update_scene_info()

            # Start monitoring
            self.running = True
            threading.Thread(target=self.monitor_obs, daemon=True).start()

            return True
        except Exception as e:
            self.log_signal.emit(f"OBS connection failed: {str(e)}")
            self.connection_status.emit(False)
            return False

    def connect_midi(self, port_name):
        try:
            available_ports = mido.get_output_names()
            if port_name in available_ports:
                self.midi_port = mido.open_output(port_name)
                self.log_signal.emit(f"MIDI connected to: {port_name}")
                return True
            else:
                self.log_signal.emit(f"MIDI port '{port_name}' not found. Available: {available_ports}")
                return False
        except Exception as e:
            self.log_signal.emit(f"MIDI connection failed: {str(e)}")
            return False

    def monitor_obs(self):
        while self.running:
            try:
                # Listen for scene changes
                events_generator = self.obs_client.event_generator()
                for event in events_generator:
                    if isinstance(event, events.CurrentProgramSceneChanged):
                        self.handle_scene_change(event.scene_name, "program")
                    elif isinstance(event, events.CurrentPreviewSceneChanged):
                        self.handle_scene_change(event.scene_name, "preview")
                    time.sleep(0.1)
            except Exception as e:
                self.log_signal.emit(f"OBS monitoring error: {str(e)}")
                time.sleep(1)

    def update_scene_info(self):
        try:
            program_scene = self.obs_client.get_current_program_scene()
            preview_scene = self.obs_client.get_current_preview_scene()

            self.handle_scene_change(program_scene.scene_name, "program")
            self.handle_scene_change(preview_scene.scene_name, "preview")
        except Exception as e:
            self.log_signal.emit(f"Failed to get scene info: {str(e)}")

    def handle_scene_change(self, scene_name, scene_type):
        import re
        # Extract camera number from scene name (e.g., "CAM 1", "Kamera 2", etc.)
        match = re.search(r'(?:CAM|Kamera|Camera)\s*(\d+)', scene_name, re.IGNORECASE)
        if match:
            cam_id = int(match.group(1))
            if 1 <= cam_id <= 8:
                if scene_type == "program":
                    self.current_program = cam_id
                    self.send_midi_note(0, cam_id, 127)  # Note 1-8 for LIVE
                    self.tally_update.emit(cam_id, 1)  # LIVE
                elif scene_type == "preview":
                    self.current_preview = cam_id
                    self.send_midi_note(10, cam_id, 127)  # Note 11-18 for PREVIEW
                    self.tally_update.emit(cam_id, 2)  # PREVIEW

                self.log_signal.emit(f"Scene {scene_type}: {scene_name} -> Camera {cam_id}")

    def send_midi_note(self, base_note, cam_id, velocity):
        if self.midi_port:
            try:
                note = base_note + cam_id
                msg = mido.Message('note_on', note=note, velocity=velocity)
                self.midi_port.send(msg)
                self.log_signal.emit(f"MIDI sent: Note {note} (Camera {cam_id})")
            except Exception as e:
                self.log_signal.emit(f"MIDI send error: {str(e)}")

    def disconnect(self):
        self.running = False
        if self.obs_client:
            self.obs_client.disconnect()
        if self.midi_port:
            self.midi_port.close()
        self.connection_status.emit(False)
        self.log_signal.emit("Disconnected from OBS and MIDI")