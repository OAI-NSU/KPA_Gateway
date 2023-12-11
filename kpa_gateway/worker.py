from threading import Lock, Thread
import time
from typing import Callable, Iterable

from loguru import logger


class Worker:
    def __init__(self, name: str, period_sec: float, target: Callable, args: Iterable) -> None:
        self.name: str = name
        self.period_sec: float = period_sec
        self.target: Callable = target
        self.args: Iterable = args

        self._thread: Thread
        self._running_flag: bool = False
        self._lock = Lock()

    def set_period(self, new_period_sec: float) -> None:
        self.period_sec = new_period_sec

    def start(self) -> None:
        if not self._running_flag:
            self._running_flag = True
            self._thread = Thread(name=self.name, daemon=True, target=self._routine)
            self._thread.start()
            logger.debug(f'{self.name} started')

    def stop(self) -> None:
        if self._running_flag:
            self._running_flag = False
            self._thread.join(1)

    def _routine(self) -> None:
        while self._running_flag:
            counter = 0
            while counter < self.period_sec and self._running_flag:
                time.sleep(0.005)
                counter += 0.005
            with self._lock:
                self.target(*self.args)
