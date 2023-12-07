import struct

from kpa_gateway.frame_types.base_types import AbstractFrame, FrameID

# from kpa_gateway.frame_types.base_types import FameAddrTelArgType


class AddrTelParameter:
    def __init__(self, arg_num: int, telemetry_type: int, value: bytes):
        self.arg_num: int = arg_num
        self.telemetry_type: int = telemetry_type
        self.value: bytes = value
        self.arg_size: int = len(self.value)

    @staticmethod
    def parse(data: bytes) -> 'AddrTelParameter':
        fields = struct.unpack('<HHB', data[:5])
        telemetry_type: int = fields[0]
        arg_num: int = fields[1]
        arg_size: int = fields[2]
        value: bytes = data[5:5 + arg_size]
        return AddrTelParameter(arg_num, telemetry_type, value)

    def to_bytes(self) -> bytes:
        return struct.pack('<HHHB', self.telemetry_type, self.arg_num, self.arg_size) + self.value

    def __str__(self) -> str:
        return f'Type: {self.telemetry_type}\nArg num: {self.arg_num}\nArg size: {self.arg_size}\n'\
               f'Value: {self.value.hex(" ").upper()}'


class FrameAddrTel(AbstractFrame):
    frame_id: FrameID = FrameID.ADDRESS_TELEMETRY

    def __init__(self, *args: AddrTelParameter):
        self.args: list[AddrTelParameter] = [*args]
        self.arg_amount: int = len(self.args)

    def to_bytes(self) -> bytes:
        return struct.pack('<HH', self.frame_id.value, self.arg_amount) + b''.join([arg.to_bytes()
                                                                                    for arg in self.args])

    @staticmethod
    def parse(data: bytes) -> 'FrameAddrTel':
        arg_amount: int = struct.unpack('<H', data[:2])[0]
        args: list[AddrTelParameter] = [arg for arg in FrameAddrTel._parse_args(data[2:])]
        if arg_amount != len(args):
            raise ValueError(f'Incorrect FrameAddrTel arguments amount. Got {len(args)} but should be {arg_amount}')
        return FrameAddrTel(*args)

    @staticmethod
    def _parse_args(data: bytes):
        ptr = 0
        while ptr < len(data):
            arg: AddrTelParameter = AddrTelParameter.parse(data[ptr:])
            ptr += arg.arg_size + 5
            yield arg

    def __str__(self) -> str:
        return f'ID: {self.frame_id}\nArg amount: {self.arg_amount}\nArgs: {[arg.value for arg in self.args]}'
