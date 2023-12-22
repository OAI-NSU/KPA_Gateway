import struct
from typing import Callable

from kpa_gateway.frame_types.base_types import AbstractFrame, FrameID


class GatewayPosTel(AbstractFrame):
    frame_id: FrameID = FrameID.POSITION_TELEMETRY
    _registered: dict[int, Callable] = {}
    def __init__(self, telemetry_type: int, tmi_data: bytes) -> None:
        self.telemetry_type: int = telemetry_type
        self.tmi_data: bytes = tmi_data
        self.size: int = len(self.tmi_data)

    def to_bytes(self) -> bytes:
        return struct.pack('<HHH', self.frame_id.value, self.telemetry_type, self.size) + self.tmi_data

    @staticmethod
    def listen(telemetry_type: int, callback: Callable, *args) -> None:
        GatewayPosTel._registered.update({telemetry_type: callback, 'args': [*args]})

    @staticmethod
    def route(telemetry_type: int) -> Callable | None:
        return GatewayPosTel._registered.get(telemetry_type, None)

    @staticmethod
    def parse(data: bytes) -> 'GatewayPosTel':
        fields = struct.unpack('<HH', data[:4])
        telemetry_type: int = fields[0]
        size: int = fields[1]
        tmi_data: bytes = data[4:]
        if size != len(tmi_data):
            raise ValueError(f'Incorrect FramePosTel data length. Got {len(tmi_data)} but should be {size}')
        return GatewayPosTel(telemetry_type, tmi_data)

    def __str__(self) -> str:
        return f'ID: {self.frame_id}\nType: {self.telemetry_type}\nSize: {self.size}\n'\
               f'Data: {self.tmi_data.hex(" ").upper()}'
