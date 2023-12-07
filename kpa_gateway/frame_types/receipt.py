
import struct

from kpa_gateway.frame_types.base_types import AbstractFrame, FrameID


class FrameReceipt(AbstractFrame):
    frame_id: FrameID = FrameID.RECEIPT
    def __init__(self, receipt_num: int, return_code: int, *strings: str) -> None:
        self.return_code: int = return_code
        self.receipt_num: int = receipt_num
        self.arg_amount: int = len(strings)
        self.strings: list[str] = [*strings]

    def to_bytes(self) -> bytes:
        data: bytes = struct.pack('<HHHH', self.frame_id.value, self.receipt_num, self.return_code, self.arg_amount)
        return data + b''.join(msg.encode('utf-8') for msg in self.strings)

    @staticmethod
    def parse(data: bytes) -> 'FrameReceipt':
        fields = struct.unpack('<HHH', data[:6])
        receipt_num: int = fields[0]
        return_code: int = fields[1]
        arg_amount: int = fields[2]
        strings: list[str] = [arg.decode('utf-8') for arg in data[6:].split(b'\x00') if len(arg)]
        if arg_amount != len(strings):
            raise ValueError(f'Incorrect FrameReceipt arguments amount. Got {len(strings)} but should be {arg_amount}')
        return FrameReceipt(receipt_num, return_code, *strings)

    def __str__(self) -> str:
        return f'ID: {self.frame_id}\nReceipt num: {self.receipt_num}\nReturn code: {self.return_code}\n'\
               f'Arg amount: {self.arg_amount}\nStrings: {self.strings}'
