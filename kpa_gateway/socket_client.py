# import time
import selectors
import socket
from threading import Thread

class SocketClient:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._read_selector = selectors.DefaultSelector()
        self._running_flag = False
        self._thread: Thread

    def _routine(self):
        try:
            while self._running_flag:
                msg = self._socket.recv(1024).decode("utf8")
                print("got from server < " + msg)
        except ConnectionResetError as err:
            print(f'\nLost connection with server: {err}')
        except ConnectionAbortedError as err:
            print(f'\nDisconnect from server: {err}')
            self.stop()

    def connect(self):
        self._socket.connect((self._host, self._port))
        self._running_flag = True
        self._thread = Thread(target=self._routine, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._running_flag:
            self._running_flag = False
            self._socket.close()

    def send(self, data: str) -> None:
        self._socket.send(data.encode('utf-8'))


if __name__ == "__main__":
    # server = SocketServer('localhost', 8083)
    # server.start_server()
    client = SocketClient("localhost", 8083)

    client.connect()
    try:
        while True:
            in_data = input('>')
            client.send(in_data)
    except KeyboardInterrupt:
        client.stop()
        # server.stop()
        print('shutdown')
