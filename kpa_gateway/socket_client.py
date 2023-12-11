# import time
import selectors
import socket
from threading import Thread
import time

from loguru import logger

class SocketClient:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._socket: socket.socket
        self._running_flag = False
        self._thread: Thread

    def _routine(self):
        try:
            while self._running_flag:
                msg = self._socket.recv(1024).decode("utf8")
                if not msg:
                    break
                print("got from server < " + msg)
                time.sleep(0.1)
        except ConnectionResetError as err:
            logger.error(f'Lost connection with server: {err}')
        except ConnectionAbortedError:
            logger.info(f'Disconnected from server')
            return None
        logger.info('Lost connection with server. Trying to reconnect.')
        self.disconnect()
        self.connect()

    def _connect_routine(self) -> bool:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect((self._host, self._port))
            logger.success(f'Connected to server {self._host}:{self._port}')
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

    def connect(self):
        while not self._connect_routine():
            time.sleep(1)

    def disconnect(self) -> None:
        if self._running_flag:
            self._running_flag = False
            time.sleep(0.2)
            self._socket.close()

    def send(self, data: bytes) -> None:
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
