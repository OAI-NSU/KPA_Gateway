

from typing import Callable
from loguru import logger
from kpa_gateway.frame_parser import Frame
from kpa_gateway.frame_types.base_types import FrameID
from kpa_gateway.frame_types.control_command import FrameCMD
from kpa_gateway.frame_types.position_telemetry import FramePosTel
from kpa_gateway.frame_types.receipt import FrameReceipt
from kpa_gateway.socket_server import SocketServer


class API_Gateway:
    def __init__(self) -> None:
        self.server = SocketServer("0.0.0.0", 4000)
        self.server.received.connect(self.route)

    def route(self, data: bytes):
        try:
            transport_frame: Frame = Frame.parse(data)
            logger.info(transport_frame)
            if transport_frame.frame.frame_id == FrameID.CMD:
                cmd_frame: FrameCMD = transport_frame.frame  # type: ignore
                func: Callable | None = cmd_frame.route(cmd_frame.cmd_type, cmd_frame.cmd_code)
                if func:
                    result: bool = func(*cmd_frame.args)
                    response = Frame(FrameReceipt(1, not result))
                    self.server.send(response.to_bytes())
            elif transport_frame.frame.frame_id == FrameID.POSITION_TELEMETRY:
                pos_tel_frame: FramePosTel = transport_frame.frame  # type: ignore
                func: Callable | None = pos_tel_frame.route(pos_tel_frame.telemetry_type)
                if func:
                    result: bool = func(pos_tel_frame.tmi_data)

        except ValueError as err:
            logger.error(err)

    def start(self):
        self.server.start_server()

    def position_telemetry(self, telemetry_type: int) -> Callable:
        def decorator(func: Callable) -> Callable:
            FramePosTel.listen(telemetry_type, func)
            return func
        return decorator

    def control_command(self, cmd_type: int, cmd_code: int) -> Callable:
        def decorator(func: Callable) -> Callable:
            FrameCMD.listen(cmd_type, cmd_code, func)
            return func
        return decorator

    def send(self, frame: Frame) -> None:
        self.server.send(frame.to_bytes())

    def send_ack(self, receipt_num: int) -> None:
        self.server.send(Frame(FrameReceipt(receipt_num, 0)).to_bytes())

    def send_nack(self, receipt_num: int) -> None:
        self.server.send(Frame(FrameReceipt(receipt_num, 1)).to_bytes())