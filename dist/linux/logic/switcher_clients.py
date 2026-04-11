import re
from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree

import requests
from obsws_python import ReqClient


CAMERA_REGEX = re.compile(r"(?:cam(?:era)?|kamera)\s*(\d+)", re.IGNORECASE)


@dataclass
class SwitcherState:
    program: Optional[int] = None
    preview: Optional[int] = None


class SwitcherClientBase:
    def connect(self) -> None:
        raise NotImplementedError

    def disconnect(self) -> None:
        raise NotImplementedError

    def get_state(self) -> SwitcherState:
        raise NotImplementedError


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
        self.client = ReqClient(host=self.host, port=self.port, password=self.password, timeout=3)

    def disconnect(self) -> None:
        if self.client:
            self.client.disconnect()
            self.client = None

    def get_state(self) -> SwitcherState:
        if not self.client:
            raise RuntimeError("OBS client not connected")

        program_name = self.client.get_current_program_scene().current_program_scene_name
        preview_name = self.client.get_current_preview_scene().current_preview_scene_name

        return SwitcherState(
            program=parse_camera_id(program_name),
            preview=parse_camera_id(preview_name),
        )


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
        )
