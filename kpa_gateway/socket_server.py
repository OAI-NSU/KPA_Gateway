import selectors
import socket
from threading import Thread

from loguru import logger

from kpa_gateway.frame_parser import Frame



class SocketServer:
    def __init__(self, host, port) -> None:
        """Initialise the server attributes."""
        self._host = host
        self._port = port
        self._socket = None
        self._read_selector = selectors.DefaultSelector()
        self._write_selector = selectors.DefaultSelector()
        self._thread: Thread
        self._running_flag = False

    def _read_handler(self, sock, addr) -> bool:
        try:
            data: bytes = sock.recv(1024)
            logger.debug(data.hex(' ').upper())
            print(Frame(data))
            for key, _ in self._write_selector.select(0):
                key.fileobj.send(data)  # type: ignore
        except ConnectionError:
            logger.debug("Client suddenly closed while receiving")
            return False
        if not data:
            logger.debug("Disconnected by", addr)
            return False
        return True

    def _accept_connection(self, sel, serv_sock, mask) -> None:
        """Callback function for when the server is ready to accept a connection."""
        client_sock, addr = serv_sock.accept()
        logger.debug(f"Connected client {addr}")
        sel.register(client_sock, selectors.EVENT_READ, self._on_read_ready)
        self._write_selector.register(client_sock, selectors.EVENT_WRITE)

    def _on_read_ready(self, sel, sock, mask) -> None:
        addr = sock.getpeername()
        if not self._read_handler(sock, addr):
            logger.debug(f'Client {addr} disconnected')
            sel.unregister(sock)
            self._write_selector.unregister(sock)
            sock.close()

    def _run(self) -> None:
        """Starts the server and accepts connections indefinitely."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._host, self._port))
        self._socket.listen()
        # Put the socket in the selector "bag":
        self._read_selector.register(self._socket, selectors.EVENT_READ, self._accept_connection)
        logger.info("Running server...")
        while self._running_flag:
            events = self._read_selector.select()
            for key, mask in events:
                callback = key.data
                callback(self._read_selector, key.fileobj, mask)

    def start_server(self) -> None:
        if not self._running_flag:
            self._thread = Thread(name='server thread', target=self._run, daemon=True)
            self._running_flag = True
            self._thread.start()
        else:
            logger.error('Server is alreay running')

    def stop(self) -> None:
        if self._running_flag:
            self._running_flag = False
            self._thread.join(1)
        else:
            logger.error('Server is not running')


if __name__ == "__main__":
    cs = SocketServer("0.0.0.0", 4000)
    cs.start_server()
    try:
        in_data = input('>')
    except KeyboardInterrupt:
        print('shutdown')