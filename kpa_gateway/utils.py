from calendar import timegm
from datetime import UTC, datetime
from threading import RLock
from typing import Callable, Type



EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as MS file time
HUNDREDS_OF_NANOSECONDS = 10000000

def dt_to_filetime(dt: datetime) -> int:
    if (dt.tzinfo is None) or (dt.tzinfo.utcoffset(dt) is None):
        dt = dt.replace(tzinfo=UTC)
    return EPOCH_AS_FILETIME + (timegm(dt.timetuple()) * HUNDREDS_OF_NANOSECONDS)


def filetime_to_dt(filetime_timestamp: int) -> datetime:
    return datetime.fromtimestamp((filetime_timestamp - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS)

class Signal:

    lock: RLock = RLock()
    def __init__(self, *args: Type) -> None:
        self.listeners: list[Callable] = []
        self.args: tuple[Type, ...] = args

    def connect(self, func: Callable) -> None:
        if func not in self.listeners:
            self.listeners.append(func)

    def disconnect(self, func: Callable) -> None:
        if func in self.listeners:
            self.listeners.remove(func)

    def emit(self, *args) -> None:
        with self.lock:
            if len(args) == len(self.args):
                if any(not isinstance(arg, self_arg) for arg, self_arg in zip(args, self.args)):
                    raise TypeError(f'This signal should emit next types: {self.args}, but you try to emit {args}.')
            else:
                raise TypeError(f'This signal should emit next types: {self.args}, but you try to emit {args}.')
            _ = [callback(*args) for callback in self.listeners]
