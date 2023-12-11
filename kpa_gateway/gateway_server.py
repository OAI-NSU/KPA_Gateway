

import socket

from loguru import logger
from kpa_gateway.socket_server import SocketServer


class GatewayServer(SocketServer):
    def __init__(self, port: int, main_client_ip: str = '') -> None:
        super().__init__(port)
        self.clients: dict[str, list[socket.socket]] = {}
        self.connected.connect(self.on_connected)
        self.main_client_ip: str = main_client_ip

    def on_connected(self, client: dict[str, socket.socket]):
        ip: str = list(client)[0]
        self.clients.setdefault(ip, []).append(client[ip])

    def send_to_client(self, client_ip: str, data: bytes) -> None:
        client_socks: list[socket.socket] | None = self.clients.get(client_ip, None)
        if client_socks:
            [sock.send(data) for sock in client_socks]
        else:
            logger.error(f'Client {client_ip} not connected')

    def is_running(self) -> bool:
        return self._run_status

if __name__ == '__main__':
    server = GatewayServer(4000)
    server.start_server()
    try:
        while True:
            in_data: list[str] = input('<').split(' ')
            ip = list(server.clients)[0]
            if '1' in in_data:
                server.clients[ip][0].send(in_data[1].encode('utf-8'))
            elif '2' in in_data:
                server.clients[ip][1].send(in_data[1].encode('utf-8'))
    except KeyboardInterrupt:
        server.stop()
        print('shutdown')
