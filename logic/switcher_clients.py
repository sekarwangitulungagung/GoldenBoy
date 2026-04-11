import re
from dataclasses import dataclass, field
from typing import Optional
from xml.etree import ElementTree

import requests
from obsws_python import ReqClient


CAMERA_REGEX = re.compile(r"(?:cam(?:era)?|kamera)\s*(\d+)", re.IGNORECASE)


@dataclass
class SwitcherState:
    program: Optional[int] = None
    preview: Optional[int] = None
    program_name: str = ""
    preview_name: str = ""


class SwitcherClientBase:
    def connect(self) -> None:
        raise NotImplementedError

    def disconnect(self) -> None:
        raise NotImplementedError

    def get_state(self) -> SwitcherState:
        raise NotImplementedError

    def get_scenes(self) -> list[str]:
        return []

    def set_program_scene(self, scene_name: str) -> None:
        pass

    def set_preview_scene(self, scene_name: str) -> None:
        pass

    def trigger_transition(self) -> None:
        pass

    def set_transition_type(self, transition_name: str) -> None:
        pass

    def get_transition_list(self) -> list[str]:
        return []


def parse_camera_id(name: str) -> Optional[int]:
    if not name:
        return None
    match = CAMERA_REGEX.search(name)
    if not match:
        return None
    cam_id = int(match.group(1))
    return cam_id if cam_id > 0 else None


class OBSClient(SwitcherClientBase):
    def __init__(self, host: str, port: int, password: str) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.client: Optional[ReqClient] = None

    def connect(self) -> None:
        self.client = ReqClient(
            host=self.host, port=self.port, password=self.password, timeout=3
        )

    def disconnect(self) -> None:
        if self.client:
            try:
                self.client.disconnect()
            except Exception:
                pass
            self.client = None

    def get_state(self) -> SwitcherState:
        if not self.client:
            raise RuntimeError("OBS client not connected")
        program_name = self.client.get_current_program_scene().current_program_scene_name
        try:
            preview_name = self.client.get_current_preview_scene().current_preview_scene_name
        except Exception:
            preview_name = ""
        return SwitcherState(
            program=parse_camera_id(program_name),
            preview=parse_camera_id(preview_name),
            program_name=program_name or "",
            preview_name=preview_name or "",
        )

    def get_scenes(self) -> list[str]:
        if not self.client:
            return []
        try:
            response = self.client.get_scene_list()
            scenes = response.scenes or []
            # OBS returns newest-first; reverse for logical order
            names = [s["sceneName"] for s in scenes]
            names.reverse()
            return names
        except Exception:
            return []

    def set_program_scene(self, scene_name: str) -> None:
        if not self.client or not scene_name:
            return
        try:
            self.client.set_current_program_scene(scene_name)
        except Exception:
            pass

    def set_preview_scene(self, scene_name: str) -> None:
        if not self.client or not scene_name:
            return
        try:
            self.client.set_current_preview_scene(scene_name)
        except Exception:
            pass

    def trigger_transition(self) -> None:
        """Trigger the studio mode transition (preview → program)."""
        if not self.client:
            return
        try:
            self.client.trigger_studio_mode_transition()
        except Exception:
            pass

    def set_transition_type(self, transition_name: str) -> None:
        """Set the active OBS scene transition by name."""
        if not self.client or not transition_name:
            return
        try:
            self.client.set_current_scene_transition({"transitionName": transition_name})
        except Exception:
            pass

    def get_transition_list(self) -> list[str]:
        if not self.client:
            return []
        try:
            resp = self.client.get_scene_transition_list()
            return [t["transitionName"] for t in (resp.transitions or [])]
        except Exception:
            return []


class VMixClient(SwitcherClientBase):
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.session = requests.Session()
        self.timeout = 3

    @property
    def api_url(self) -> str:
        return f"http://{self.host}:{self.port}/api"

    def connect(self) -> None:
        response = self.session.get(self.api_url, timeout=self.timeout)
        response.raise_for_status()

    def disconnect(self) -> None:
        self.session.close()

    def get_state(self) -> SwitcherState:
        response = self.session.get(self.api_url, timeout=self.timeout)
        response.raise_for_status()
        root = ElementTree.fromstring(response.text)
        active = root.find("active")
        preview = root.find("preview")
        active_name = active.text if active is not None else ""
        preview_name = preview.text if preview is not None else ""
        return SwitcherState(
            program=parse_camera_id(active_name or ""),
            preview=parse_camera_id(preview_name or ""),
            program_name=active_name or "",
            preview_name=preview_name or "",
        )

    def get_scenes(self) -> list[str]:
        """Return vMix input names as scene list."""
        try:
            response = self.session.get(self.api_url, timeout=self.timeout)
            root = ElementTree.fromstring(response.text)
            inputs = root.find("inputs")
            if inputs is None:
                return []
            return [inp.get("title", inp.get("shortTitle", "")) for inp in inputs]
        except Exception:
            return []

    def trigger_transition(self) -> None:
        try:
            self.session.get(f"http://{self.host}:{self.port}/api?Function=Transition1", timeout=self.timeout)
        except Exception:
            pass

    def set_program_scene(self, scene_name: str) -> None:
        try:
            self.session.get(
                f"http://{self.host}:{self.port}/api?Function=ActiveInput&Input={requests.utils.quote(scene_name)}",
                timeout=self.timeout,
            )
        except Exception:
            pass

    def set_preview_scene(self, scene_name: str) -> None:
        try:
            self.session.get(
                f"http://{self.host}:{self.port}/api?Function=PreviewInput&Input={requests.utils.quote(scene_name)}",
                timeout=self.timeout,
            )
        except Exception:
            pass
