from queue import Empty, Queue
import selectors
import socket
from threading import Thread
import time
from loguru import logger
from kpa_gateway.utils import Signal


class SocketServer:
    received: Signal = Signal(bytes)
    def __init__(self, host, port) -> None:
        """Initialise the server attributes."""
        self._host = host
        self._port = port
        self._socket: socket.socket | None = None
        self._read_selector = selectors.DefaultSelector()
        self._write_selector = selectors.DefaultSelector()
        self._thread: Thread
        self._handler_thread: Thread
        self._running_flag = False
        self._tx_queue = Queue()
        self._rx_queue = Queue()

    def send(self, data: bytes) -> None:
        self._tx_queue.put(data, timeout=1)

    def _rx_routine(self) -> None:
        while self._running_flag:
            try:
                data: bytes = self._rx_queue.get(timeout=0.1)
                self.received.emit(data)
            except Empty:
                time.sleep(0.01)

    def _read_handler(self, sock, addr) -> bool:
        try:
            data: bytes = sock.recv(1024)
            self._rx_queue.put_nowait(data)
            logger.debug(f'received: {data.hex(" ").upper()}')
            try:
                send_data: bytes = self._tx_queue.get(timeout=0.5)
                for key, _ in self._write_selector.select(0):
                    key.fileobj.send(send_data)  # type: ignore
                    logger.debug(f'sended: {send_data.hex(" ").upper()}')
            except Empty:
                time.sleep(0.001)
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
        self._socket.setblocking(False)
        self._socket.settimeout(1)
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
            self._handler_thread = Thread(name='rx_handler_thread', target=self._rx_routine, daemon=True)
            self._running_flag = True
            self._thread.start()
            self._handler_thread.start()
        else:
            logger.error('Server is alreay running')

    def stop(self) -> None:
        if self._running_flag:
            self._running_flag = False
            self._thread.join(1)
            self._handler_thread.join(1)
        else:
            logger.error('Server is not running')


if __name__ == "__main__":
    cs = SocketServer("0.0.0.0", 4000)
    cs.received.connect(lambda data: logger.info(data.hex(' ').upper()))
    try:
        in_data = input('<')
    except KeyboardInterrupt:
        cs.stop()
        print('shutdown')
