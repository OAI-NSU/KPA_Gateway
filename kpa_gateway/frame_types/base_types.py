from abc import ABCMeta
from enum import Enum


class FrameID(Enum):
    RECEIPT = 1
    CMD = 2
    ADDRESS_TELEMETRY = 4
    POSITION_TELEMETRY = 5
    MESSAGE = 6
    LOG_MESSAGE = 7


class FrameCMDArgType(Enum):
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


ARG_SIZES: dict[FrameCMDArgType, tuple[int, str]] = {
    FrameCMDArgType.BYTE: (1, '<B'),
    FrameCMDArgType.BYTE_SIGN: (1, '<b'),
    FrameCMDArgType.WORD: (2, '<H'),
    FrameCMDArgType.WORD_SIGN: (2, '<h'),
    FrameCMDArgType.DWORD: (4, '<I'),
    FrameCMDArgType.DWORD_SIGN: (4, '<i'),
    FrameCMDArgType.REAL: (4, '<f'),
    FrameCMDArgType.DOUBLE: (8, '<d'),
    FrameCMDArgType.STRING: (0, '<s'),
    FrameCMDArgType.MBYTE: (0, '<p'),
}


class AbstractFrame(metaclass=ABCMeta):
    frame_id: FrameID

    def to_bytes(self):
        raise NotImplementedError

    @staticmethod
    def parse(data: bytes):
        raise NotImplementedError
