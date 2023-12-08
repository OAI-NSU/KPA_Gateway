from typing import Callable, Iterable
from loguru import logger
from kpa_gateway.frame_parser import GatewayFrame
from kpa_gateway.frame_types.base_types import FrameID
from kpa_gateway.frame_types.control_command import GatewayCMD
from kpa_gateway.frame_types.position_telemetry import GatewayPosTel
from kpa_gateway.frame_types.receipt import GatewayReceipt
from kpa_gateway.socket_server import SocketServer
from kpa_gateway.worker import Worker


class API_Gateway:
    def __init__(self, port: int = 4000) -> None:
        self.port: int = port
        self.server = SocketServer("0.0.0.0", self.port)
        self.server.received.connect(self.route)
        self.workers: dict[str, Worker] = {}

    def route(self, data: bytes) -> None:
        try:
            transport_frame: GatewayFrame = GatewayFrame.parse(data)
            logger.info(transport_frame)
            if transport_frame.frame.frame_id == FrameID.CMD:
                cmd_frame: GatewayCMD = transport_frame.frame  # type: ignore
                func: Callable | None = cmd_frame.route(cmd_frame.cmd_type, cmd_frame.cmd_code)
                if func:
                    result: bool = func(*cmd_frame.args)
                    response = GatewayFrame(GatewayReceipt(GatewayCMD.frame_id.value, not result))
                    self.server.send(response.to_bytes())
            elif transport_frame.frame.frame_id == FrameID.POSITION_TELEMETRY:
                pos_tel_frame: GatewayPosTel = transport_frame.frame  # type: ignore
                func: Callable | None = pos_tel_frame.route(pos_tel_frame.telemetry_type)
                if func:
                    func(pos_tel_frame.tmi_data)

        except ValueError as err:
            logger.error(err)

    def add_worker(self, target: Callable, name: str | None = None, period_sec: float = 5, args: Iterable = []) -> None:
        worker_name = f'{target.__name__}_worker' if not name else name
        self.workers.update({worker_name: Worker(name=worker_name, period_sec=period_sec, target=target, args=args)})

    def get_worker(self, name: str) -> Worker | None:
        return self.workers.get(name, None)

    def start(self) -> None:
        self.server.start_server()
        [worker.start() for worker in self.workers.values()]

    def stop(self) -> None:
        self.server.stop()
        [worker.stop() for worker in self.workers.values()]

    def position_telemetry(self, telemetry_type: int) -> Callable:
        def decorator(func: Callable) -> Callable:
            GatewayPosTel.listen(telemetry_type, func)
            return func
        return decorator

    def control_command(self, cmd_type: int, cmd_code: int) -> Callable:
        def decorator(func: Callable) -> Callable:
            GatewayCMD.listen(cmd_type, cmd_code, func)
            return func
        return decorator

    def send(self, frame: GatewayFrame) -> None:
        self.server.send(frame.to_bytes())

    def send_ack(self, receipt_num: int) -> None:
        self.server.send(GatewayFrame(GatewayReceipt(receipt_num, 0)).to_bytes())

    def send_nack(self, receipt_num: int) -> None:
        self.server.send(GatewayFrame(GatewayReceipt(receipt_num, 1)).to_bytes())
