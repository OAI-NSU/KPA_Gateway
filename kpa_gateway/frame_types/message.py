import struct

from kpa_gateway.frame_types.base_types import AbstractFrame, FrameID


class GatewayMessage(AbstractFrame):
    frame_id: FrameID = FrameID.MESSAGE

    def __init__(self, *strings: str) -> None:
        self.strings: list[str] = [*strings]
        self.str_amount: int = len(self.strings)

    def to_bytes(self) -> bytes:
        return struct.pack('<HH', self.frame_id.value, self.str_amount) + b''.join([arg.encode('utf-8')
                                                                                    for arg in self.strings])

    @staticmethod
    def parse(data: bytes) -> 'GatewayMessage':
        str_amount: int = struct.unpack('<H', data[:2])[0]
        strings: list[str] = [msg.decode('utf-8') for msg in data[2:].split(b'\x00')]
        if str_amount != len(strings):
            raise ValueError(f'Incorrect FrameMessage arguments amount. Got {len(strings)} but should be {str_amount}')
        return GatewayMessage(*strings)

    def __str__(self) -> str:
        return f'ID: {self.frame_id}\nAmount: {self.str_amount}\n' + '\n'.join(self.strings)


class GatewayLogMessage(AbstractFrame):
    frame_id: FrameID = FrameID.LOG_MESSAGE

    def __init__(self, message_type: int, msg: str) -> None:
        self.message_type: int = message_type
        self.message: str = msg

    def to_bytes(self) -> bytes:
        return struct.pack('<HH', self.frame_id.value, self.message_type) + self.message.encode('utf-8')

    @staticmethod
    def parse(data: bytes) -> 'GatewayLogMessage':
        message_type: int = struct.unpack('<H', data[:2])[0]
        message: str = data[2:].decode('utf-8')
        return GatewayLogMessage(message_type, message)

    def __str__(self) -> str:
        return f'ID: {self.frame_id}\nType: {self.message_type}\nMsg: {self.message}'
