from queue import Empty, Queue
import selectors
import socket
from threading import Thread
from loguru import logger
from kpa_gateway.utils import Signal


class SocketServer:
    received: Signal = Signal(bytes)
    transmited: Signal = Signal(bytes)
    connected: Signal = Signal(dict)
    disconnected: Signal = Signal(tuple)
    def __init__(self, port: int) -> None:
        """Initialise the server attributes."""
        self._host: str = '0.0.0.0'
        self._port: int = port
        self._socket: socket.socket | None = None
        self._selector = selectors.DefaultSelector()
        self._thread: Thread
        self._handler_thread: Thread
        self._running_flag = False
        self._tx_queue = Queue()
        self._rx_queue = Queue()
        self._run_status: bool = False
        self._handlers: dict = {selectors.EVENT_READ: self._read_handler, selectors.EVENT_WRITE: self._write_handler}

    def send(self, data: bytes) -> None:
        self._tx_queue.put(data)

    def _rx_routine(self) -> None:
        while self._running_flag:
            data: bytes = self._rx_queue.get()
            self.received.emit(data)

    def _read_handler(self, sock: socket.socket) -> bool:
        try:
            data: bytes = sock.recv(1024)
            if not data:
                logger.debug("Disconnected by", sock.getpeername())
                return False
            self._rx_queue.put_nowait(data)
            logger.debug(f'received: {data.hex(" ").upper()}')
        except ConnectionError:
            logger.debug("Client suddenly closed while receiving")
            return False
        return True

    def _write_handler(self, sock) -> bool:
        try:
            data: bytes = self._tx_queue.get_nowait()
            sock.send(data)
            logger.debug(f'sended: {data.hex(" ").upper()}')
        except Empty:
            pass
        except ConnectionError:
            logger.debug("Client suddenly closed while receiving")
            return False
        return True

    def _accept_connection(self, sel: selectors.SelectSelector, serv_sock: socket.socket, mask: int) -> None:
        """Callback function for when the server is ready to accept a connection."""
        client: tuple[socket.socket, tuple[str, int]] = serv_sock.accept()
        client_sock: socket.socket = client[0]
        addr: tuple[str, int] = client[1]
        logger.debug(f"Connected client {addr}")
        sel.register(client_sock, selectors.EVENT_READ | selectors.EVENT_WRITE, self._selector_ready)
        self.connected.emit({addr[0]: client_sock})

    def _selector_ready(self, sel: selectors.SelectSelector, sock: socket.socket, mask: int) -> None:
        def lost_connection_handler(sock: socket.socket) -> None:
            addr = sock.getpeername()
            logger.debug(f'Client { addr } disconnected')
            sel.unregister(sock)
            sock.close()
            self.disconnected.emit(addr)

        self._handlers.get(mask, lost_connection_handler)(sock)


    def _run(self) -> None:
        """Starts the server and accepts connections indefinitely."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._host, self._port))
        self._socket.listen()
        # Put the socket in the selector "bag":
        self._selector.register(self._socket, selectors.EVENT_READ, self._accept_connection)
        logger.info(f'Starting KPA_Gateway server at {self._host}:{self._port}')
        while self._running_flag:
            events: list[tuple[selectors.SelectorKey, int]] = self._selector.select()
            for key, mask in events:
                callback = key.data
                callback(self._selector, key.fileobj, mask)

    def start_server(self) -> None:
        if not self._running_flag:
            self._thread = Thread(name='server thread', target=self._run, daemon=True)
            self._handler_thread = Thread(name='rx_handler_thread', target=self._rx_routine, daemon=True)
            self._running_flag = True
            self._thread.start()
            self._handler_thread.start()
        else:
            logger.warning('Server is already running')
        self._run_status = True

    def stop(self) -> None:
        if self._running_flag:
            self._running_flag = False
            self._thread.join(1)
            self._handler_thread.join(1)
        else:
            logger.error('Server is not running')
        self._run_status = False


if __name__ == "__main__":
    cs = SocketServer(4000)
    cs.start_server()
    cs.received.connect(lambda data: logger.info(data.hex(' ').upper()))
    try:
        while True:
            in_data = input('<')
            cs.send(in_data.encode('utf-8'))
    except KeyboardInterrupt:
        cs.stop()
        print('shutdown')
