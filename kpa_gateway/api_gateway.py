from typing import Callable, Iterable
from kpa_gateway.socket_server import ReceivedData, SocketServer
from loguru import logger
from kpa_gateway.frame_parser import GatewayFrame
from kpa_gateway.frame_types.base_types import FrameID
from kpa_gateway.frame_types.control_command import GatewayCMD
from kpa_gateway.frame_types.position_telemetry import GatewayPosTel
from kpa_gateway.frame_types.receipt import GatewayReceipt
from kpa_gateway.worker import Worker


class API_Gateway:
    def __init__(self, port: int = 4000, ats_ip: str = '', feeder_module_ip: str = '') -> None:
        self.port: int = port
        self.server = SocketServer(self.port)
        self.server.received.connect(self.route)
        self.workers: dict[str, Worker] = {}
        self.ats_ip: str = ats_ip
        self.feeder_module_ip: str = feeder_module_ip

    def route(self, data: ReceivedData) -> None:
        try:
            transport_frame: GatewayFrame = GatewayFrame.parse(data.msg)
            logger.info(transport_frame)
            if transport_frame.frame.frame_id == FrameID.CMD:
                cmd_frame: GatewayCMD = transport_frame.frame  # type: ignore
                func: Callable | None = cmd_frame.route(cmd_frame.cmd_type, cmd_frame.cmd_code)
                if func:
                    result: bool = func(self, *cmd_frame.args)
                    response = GatewayFrame(GatewayReceipt(GatewayCMD.frame_id.value, not result))
                    data.sock.send(response.to_bytes())
            elif transport_frame.frame.frame_id == FrameID.POSITION_TELEMETRY:
                pos_tel_frame: GatewayPosTel = transport_frame.frame  # type: ignore
                func: Callable | None = pos_tel_frame.route(pos_tel_frame.telemetry_type)
                if func:
                    func(self, pos_tel_frame.tmi_data)

        except ValueError as err:
            logger.error(err)

    def add_worker(self, target: Callable, name: str | None = None, period_sec: float = 5, args: Iterable = []) -> None:
        worker_name = f'{target.__name__}_worker' if not name else name
        self.workers.update({worker_name: Worker(name=worker_name, period_sec=period_sec, target=target, args=args)})

    def get_worker(self, name: str) -> Worker | None:
        return self.workers.get(name, None)

    def start(self) -> None:
        self.server.start_server()
        # [worker.start() for worker in self.workers.values()]

    def stop(self) -> None:
        self.server.stop()
        [worker.stop() for worker in self.workers.values()]

    def position_telemetry(self, telemetry_type: int) -> Callable:
        def decorator(func: Callable) -> None:
            GatewayPosTel.listen(telemetry_type, func)
        return decorator

    def control_command(self, cmd_type: int, cmd_code: int) -> Callable:
        def wrapper(func: Callable) -> None:
            GatewayCMD.listen(cmd_type, cmd_code, func)
        return wrapper

    def send_ats(self, frame: GatewayFrame) -> None:
        self.server.send_to_client(self.ats_ip, frame.to_bytes())

    def send_feeder(self, frame: GatewayFrame) -> None:
        self.server.send_to_client(self.feeder_module_ip, frame.to_bytes())

    # def send(self, frame: GatewayFrame) -> None:
    #     self.server.send(frame.to_bytes())

    # def send_ack(self, receipt_num: int) -> None:
    #     self.server.send(GatewayFrame(GatewayReceipt(receipt_num, 0)).to_bytes())

    # def send_nack(self, receipt_num: int) -> None:
    #     self.server.send(GatewayFrame(GatewayReceipt(receipt_num, 1)).to_bytes())

if __name__ == '__main__':
    gateway = API_Gateway()
    class DecoratorTest:

        @gateway.control_command(cmd_type=1, cmd_code=1)
        def check_cmd(self):
            print('check_cmd')
            return True

        @gateway.control_command(cmd_type=1, cmd_code=2)
        def check_cmd2(self):
            print('check_cmd2')
            return True

    test = DecoratorTest()
    # gateway.route(GatewayFrame(GatewayCMD(1, 1)).to_bytes())
    # gateway.route(GatewayFrame(GatewayCMD(1, 2)).to_bytes())
