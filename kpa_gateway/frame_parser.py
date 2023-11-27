from datetime import datetime
from enum import Enum
import struct
from kpa_gateway.utils import filetime_to_dt


class FrameID(Enum):
    RECEIPT = 1
    CMD = 2
    ADDRESS_TELEMETRY = 4
    CONSTANT_TELEMETRY = 5
    MESSAGE = 6
    LOG_MESSAGE = 7


class FrameArgTypes(Enum):
    BYTE = 1
    BYTE_SIGN = 2
    WORD = 3
    WORD_SIGN = 4
    DWORD = 5
    DWORD_SIGN = 6
    REAL = 7
    DOUBLE = 8
    STRING = 9
    MBYTE = 10


class FrameCMD:
    def __init__(self, data: bytes) -> None:
        fields = struct.unpack('<HIH', data[:8])
        self.cmd_type: int = fields[0]
        self.cmd_code: int = fields[1]
        self.arg_amount: int = fields[2]
        self.args: list[int] = [arg for arg in self.parse_args(data[8:])]

    def parse_args(self, data: bytes):
        ptr = 0
        while ptr < len(data):
            arg_size: int = struct.unpack('<H', data[ptr:ptr + 2])[0]
            ptr += 2 + arg_size
            yield int.from_bytes(data[ptr - arg_size: ptr], 'little')

    def __str__(self) -> str:
        return f'Type: {self.cmd_type}\nCode: {self.cmd_code}\nArg amount: {self.arg_amount}\nArgs: {self.args}'


class FrameReceipt:
    def __init__(self, data: bytes) -> None:
        fields = struct.unpack('<HHH', data[:6])
        self.receipt_num: int = fields[0]
        self.return_code: int = fields[1]
        self.arg_amount: int = fields[2]
        self.strings: list[str] = [arg.decode('utf-8') for arg in data[6:].split(b'\x00')]

    def __str__(self) -> str:
        return f'Receipt num: {self.receipt_num}\nReturn code: {self.return_code}\nArg amount: {self.arg_amount}\n'\
               f'Strings: {self.strings}'


class AddrTelParameter:
    def __init__(self, data: bytes) -> None:
        fields = struct.unpack('<HHB', data[:5])
        self.telemetry_type: int = fields[0]
        self.arg_num: int = fields[1]
        self.arg_size: int = fields[2]
        self.value: int = int.from_bytes(data[5:5 + self.arg_size], 'little')

    def __str__(self) -> str:
        return f'Type: {self.telemetry_type}\nArg num: {self.arg_num}\nArg size: {self.arg_size}\nValue: {self.value}'


class FrameAddrTel:
    def __init__(self, data: bytes) -> None:
        self.arg_amount: int = struct.unpack('<H', data[:2])[0]
        self.args: list[AddrTelParameter] = [arg for arg in self.parse_args(data[2:])]

    def parse_args(self, data: bytes):
        ptr = 0
        while ptr < len(data):
            arg = AddrTelParameter(data[ptr:])
            ptr += arg.arg_size + 5
            yield arg

    def __str__(self) -> str:
        return f'Arg amount: {self.arg_amount}\nArgs: {[arg.value for arg in self.args]}'


class FramePosTel:
    def __init__(self, data: bytes) -> None:
        fields = struct.unpack('<HH', data[:4])
        self.telemetry_type: int = fields[0]
        self.size: int = fields[1]
        self.data: bytes = data[4:]

    def __str__(self) -> str:
        return f'Type: {self.telemetry_type}\nSize: {self.size}\nData: {self.data.hex(" ").upper()}'


class FrameMessage:
    def __init__(self, data: bytes) -> None:
        self.str_amount: int = struct.unpack('<H', data[:2])[0]
        self.strings: list[str] = [msg.decode('utf-8') for msg in data[2:].split(b'\x00')]

    def __str__(self) -> str:
        return f'Amount: {self.str_amount}\n' + '\n'.join(self.strings)


class FrameLogMessage:
    def __init__(self, data: bytes) -> None:
        self.message_type: int = struct.unpack('<H', data[:2])[0]
        self.message: str = data[2:].decode('utf-8')

    def __str__(self) -> str:
        return f'Type: {self.message_type}\nMsg: {self.message}'


class Frame:
    def __init__(self, data: bytes) -> None:
        header_fields = struct.unpack('<HQH', data[:12])
        handlers: dict = {
            FrameID.RECEIPT.value: FrameReceipt,
            FrameID.CMD.value: FrameCMD,
            FrameID.ADDRESS_TELEMETRY.value: FrameAddrTel,
            FrameID.CONSTANT_TELEMETRY.value: FramePosTel,
            FrameID.MESSAGE.value: FrameMessage,
            FrameID.LOG_MESSAGE.value: FrameLogMessage
        }
        self.parameters: bytes = data[12:]
        self.frame_length: int = header_fields[0]
        self.timestamp: datetime = filetime_to_dt(header_fields[1])
        self.frame_id = FrameID(header_fields[2])
        self.params = handlers[self.frame_id.value](self.parameters)

    def __str__(self) -> str:
        return f"Length: {self.frame_length}\nTime: {self.timestamp.isoformat(' ', 'seconds')}\nID: {self.frame_id}\n"\
               f"{self.params}"
