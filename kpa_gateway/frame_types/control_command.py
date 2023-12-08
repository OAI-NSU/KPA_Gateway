


import struct
from typing import Any, Callable, Generator
from kpa_gateway.frame_types.base_types import ARG_SIZES, AbstractFrame, FrameCMDArgType, FrameID


class GatewayCMD(AbstractFrame):
    frame_id: FrameID = FrameID.CMD
    _registered: dict[int, dict[int, Callable]] = {}
    def __init__(self, cmd_type: int, cmd_code: int, *args: tuple[FrameCMDArgType, Any]) -> None:
        self.cmd_type: int = cmd_type
        self.cmd_code: int = cmd_code
        self.args: list[tuple[FrameCMDArgType, Any]] = [*args]
        self.arg_amount: int = len(self.args)

    @staticmethod
    def listen(cmd_type: int, cmd_code: int, callback: Callable) -> None:
        GatewayCMD._registered.update({cmd_type: {cmd_code: callback}})

    @staticmethod
    def route(cmd_type: int, cmd_code: int) -> Callable | None:
        return GatewayCMD._registered.get(cmd_type, {}).get(cmd_code, None)

    @staticmethod
    def parse(data: bytes) -> 'GatewayCMD':
        fields = struct.unpack('<HIH', data[:8])
        cmd_type: int = fields[0]
        cmd_code: int = fields[1]
        arg_amount: int = fields[2]
        args: list[tuple[FrameCMDArgType, Any]] = [arg for arg in GatewayCMD._parse_args(data[8:])]
        if arg_amount != len(args):
            raise ValueError(f'Incorrect FrameCMD arguments amount. Got {len(args)} but should be {arg_amount}')
        return GatewayCMD(cmd_type, cmd_code, *args)

    def to_bytes(self) -> bytes:
        data: bytes = struct.pack('<HHIH', self.frame_id.value, self.cmd_type, self.cmd_code, self.arg_amount)
        return data + self._args_to_bytes()

    def _args_to_bytes(self) -> bytes:
        result: bytes = b''
        for (arg_type, arg) in self.args:
            result += struct.pack('<H', arg_type.value)
            pack_label: str = ARG_SIZES[arg_type][1]
            if arg_type == FrameCMDArgType.STRING:
                result += struct.pack(pack_label, arg.encode('utf-8'))
            else:
                result += struct.pack(pack_label, arg)
        return result

    @staticmethod
    def _parse_args(data: bytes) -> Generator[tuple[FrameCMDArgType, Any], Any, None]:
        ptr = 0
        while ptr < len(data):
            arg_type: FrameCMDArgType = FrameCMDArgType(struct.unpack('<H', data[ptr:ptr + 2])[0])
            arg_size, pack_label = ARG_SIZES[arg_type]
            ptr += 2 + arg_size
            if arg_type == FrameCMDArgType.STRING:
                result = data[ptr:].split(b'\x00')[0].decode('utf-8')
                ptr += len(result) + 1
            elif arg_type == FrameCMDArgType.MBYTE:
                array_size: int = struct.unpack('<H', data[ptr:ptr + 2])[0]
                result = data[ptr + 2: ptr + array_size]
            else:
                val = data[ptr - arg_size: ptr]
                result = struct.unpack(pack_label, val)[0]
            yield arg_type, result

    def __str__(self) -> str:
        return f'ID: {self.frame_id}\nType: {self.cmd_type}\nCode: {self.cmd_code}\nArg amount: {self.arg_amount}\n'\
               f'Args: {self.args}'
