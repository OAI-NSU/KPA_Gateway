


import ctypes
from threading import Lock, Thread
import time
from typing import Callable, Iterable

from loguru import logger


def terminate_thread(thread, exception) -> None:
    """Terminates a python thread from another thread.

    :param thread: a threading.Thread instance
    """
    if not thread.is_alive():
        return

    res: int = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), ctypes.py_object(exception))
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class Worker:
    def __init__(self, name: str, period_sec: float, target: Callable, args: Iterable) -> None:
        self.name = name
        self.period_sec = period_sec
        self.target = target
        self.args = args
        self._thread: Thread
        self._running_flag: bool = False
        self._lock = Lock()

    def start(self) -> None:
        if not self._running_flag:
            self._running_flag = True
            self._thread = Thread(name=self.name, daemon=True, target=self._routine)
            self._thread.start()
            logger.debug(f'{self.name} started')

    def stop(self) -> None:
        if self._running_flag:
            self._running_flag = False
            terminate_thread(self._thread, TimeoutError)

    def _routine(self) -> None:
        try:
            while self._running_flag:
                time.sleep(self.period_sec)
                with self._lock:
                    self.target(*self.args)
        except TimeoutError:
            logger.debug(f'{self.name} finished')
