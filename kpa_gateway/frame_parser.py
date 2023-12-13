from datetime import datetime
from typing import Union
import struct
from kpa_gateway.frame_types.address_telemetry import GatewayAddrTel
from kpa_gateway.frame_types.base_types import FrameCMDArgType, FrameID
from kpa_gateway.frame_types.control_command import GatewayCMD
from kpa_gateway.frame_types.message import GatewayLogMessage, GatewayMessage
from kpa_gateway.frame_types.position_telemetry import GatewayPosTel
from kpa_gateway.frame_types.receipt import GatewayReceipt
from kpa_gateway.utils import dt_to_filetime, filetime_to_dt


FRAME_TYPES = Union[
    GatewayReceipt,
    GatewayLogMessage,
    GatewayMessage,
    GatewayPosTel,
    GatewayAddrTel,
    GatewayCMD
]


class GatewayFrame:
    def __init__(self, frame: FRAME_TYPES, timestamp: datetime | None = None):
        self.frame = frame
        self.timestamp: datetime = timestamp if timestamp else datetime.now()
        self.frame_length: int = len(frame.to_bytes()) + 8

    @staticmethod
    def parse(data: bytes) -> 'GatewayFrame':
        header_fields = struct.unpack('<HQH', data[:12])
        handlers: dict = {
            FrameID.RECEIPT.value: GatewayReceipt,
            FrameID.CMD.value: GatewayCMD,
            FrameID.ADDRESS_TELEMETRY.value: GatewayAddrTel,
            FrameID.POSITION_TELEMETRY.value: GatewayPosTel,
            FrameID.MESSAGE.value: GatewayMessage,
            FrameID.LOG_MESSAGE.value: GatewayLogMessage
        }
        parameters: bytes = data[12:]
        frame_length: int = header_fields[0]
        timestamp: datetime = filetime_to_dt(header_fields[1])
        frame_id: FrameID = FrameID(header_fields[2])
        frame: FRAME_TYPES = handlers[frame_id.value].parse(parameters)
        got_len: int = len(frame.to_bytes()) + 8
        if frame_length != got_len:
            raise ValueError(f'Incorrect base frame length. Got {got_len} but should be {frame_length}')
        return GatewayFrame(frame, timestamp)

    def to_bytes(self) -> bytes:
        return struct.pack('<HQ', self.frame_length, dt_to_filetime(self.timestamp)) + self.frame.to_bytes()

    def __str__(self) -> str:
        split_line = '=' * 30
        return f"{split_line}\nLength: {self.frame_length}\nTime: {self.timestamp.isoformat(' ', 'seconds')}\n"\
               f"{self.frame}\nRawData: 0x{self.to_bytes().hex(' ').upper()}"

if __name__ == '__main__':
    frame = GatewayFrame(GatewayCMD(1, 1, (FrameCMDArgType.WORD, 77)))
    data = frame.to_bytes()
    print(data.hex(' ').upper())
    print(GatewayFrame.parse(data))