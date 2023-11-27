from kpa_gateway.socket_server import SocketServer


if __name__ == "__main__":
    cs = SocketServer("0.0.0.0", 4000)
    cs.start_server()
    try:
        in_data = input('>')
    except KeyboardInterrupt:
        print('shutdown')