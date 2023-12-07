from datetime import datetime
from typing import Union
import struct
from kpa_gateway.frame_types.address_telemetry import FrameAddrTel
from kpa_gateway.frame_types.base_types import FrameCMDArgType, FrameID
from kpa_gateway.frame_types.control_command import FrameCMD
from kpa_gateway.frame_types.message import FrameLogMessage, FrameMessage
from kpa_gateway.frame_types.position_telemetry import FramePosTel
from kpa_gateway.frame_types.receipt import FrameReceipt
from kpa_gateway.utils import dt_to_filetime, filetime_to_dt


FRAME_TYPES = Union[
    FrameReceipt,
    FrameLogMessage,
    FrameMessage,
    FramePosTel,
    FrameAddrTel,
    FrameReceipt,
    FrameCMD
]


class Frame:
    def __init__(self, frame: FRAME_TYPES, timestamp: datetime | None = None):
        self.frame = frame
        self.timestamp: datetime = timestamp if timestamp else datetime.utcnow()
        self.frame_length: int = len(frame.to_bytes()) + 8

    @staticmethod
    def parse(data: bytes) -> 'Frame':
        header_fields = struct.unpack('<HQH', data[:12])
        handlers: dict = {
            FrameID.RECEIPT.value: FrameReceipt,
            FrameID.CMD.value: FrameCMD,
            FrameID.ADDRESS_TELEMETRY.value: FrameAddrTel,
            FrameID.POSITION_TELEMETRY.value: FramePosTel,
            FrameID.MESSAGE.value: FrameMessage,
            FrameID.LOG_MESSAGE.value: FrameLogMessage
        }
        parameters: bytes = data[12:]
        frame_length: int = header_fields[0]
        timestamp: datetime = filetime_to_dt(header_fields[1])
        frame_id: FrameID = FrameID(header_fields[2])
        frame: FRAME_TYPES = handlers[frame_id.value].parse(parameters)
        got_len: int = len(frame.to_bytes()) + 8
        if frame_length != got_len:
            raise ValueError(f'Incorrect base frame length. Got {got_len} but should be {frame_length}')
        return Frame(frame, timestamp)

    def to_bytes(self) -> bytes:
        return struct.pack('<HQ', self.frame_length, dt_to_filetime(self.timestamp)) + self.frame.to_bytes()

    def __str__(self) -> str:
        return f"Length: {self.frame_length}\nTime: {self.timestamp.isoformat(' ', 'seconds')}\n{self.frame}"

if __name__ == '__main__':
    frame = Frame(FrameCMD(1, 1, (FrameCMDArgType.WORD, 77)))
    data = frame.to_bytes()
    print(data.hex(' ').upper())
    print(Frame.parse(data))