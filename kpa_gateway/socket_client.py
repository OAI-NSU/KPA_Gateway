# import time
import socket
from threading import Thread
import time

from loguru import logger

from kpa_gateway.utils import Signal

class SocketClient:
    received = Signal(bytes)
    transmited = Signal(bytes)
    disconnected = Signal()
    connected = Signal()
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._socket: socket.socket
        self._running_flag = False
        self._thread: Thread
        self._connection_status: bool = False

    def _routine(self):
        try:
            while self._running_flag:
                msg: bytes = self._socket.recv(1024)
                if not msg:
                    break
                print("got from server < ", msg)
                time.sleep(0.1)
        except ConnectionResetError as err:
            logger.error(f'Lost connection with server: {err}')
        except ConnectionAbortedError:
            logger.info('Disconnected from server')
            return None
        logger.info('Lost connection with server. Trying to reconnect.')
        self.disconnect()
        self.connect()

    def _connect_routine(self) -> bool:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect((self._host, self._port))
            self._connection_status = True
            logger.success(f'Connected to server {self._host}:{self._port}')
            self.connected.emit()
        except ConnectionRefusedError:
            logger.error(f'Can not connect to {self._host}:{self._port}. Trying to reconect')
            return False
        except ConnectionResetError as err:
            logger.error(f'\nLost connection with server: {err}')
            self.disconnect()
            return False

        self._running_flag = True
        self._thread = Thread(target=self._routine, daemon=True)
        self._thread.start()
        return True

    def connect(self) -> bool:
        while not self._connect_routine():
            time.sleep(1)
        return True

    def disconnect(self) -> None:
        if self._running_flag:
            self._connection_status = False
            self._running_flag = False
            time.sleep(0.2)
            self._socket.close()
            self.disconnected.emit()

    def send(self, data: bytes) -> None:
        if self._connection_status:
            self._socket.send(data)


if __name__ == "__main__":
    # server = SocketServer('localhost', 8083)
    # server.start_server()
    client = SocketClient("localhost", 4000)
    try:
        client.connect()
        while True:
            in_data = input('>')
            client.send(in_data.encode('utf-8'))
    except KeyboardInterrupt:
        client.disconnect()
        # server.stop()
        print('shutdown')
