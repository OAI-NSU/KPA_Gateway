from ast import literal_eval
from pathlib import Path
import struct
from typing import Any
from PyQt6 import QtWidgets
from PyQt6.uic.load_ui import loadUi
from kpa_gateway.ats_emulator.args_widgets import ATM_Arg, CMD_Arg, MsgArg, _add_arg
from kpa_gateway.ats_emulator.widgets import _Widgets
from kpa_gateway.frame_parser import GatewayFrame
from kpa_gateway.frame_types.address_telemetry import AddrTelParameter, GatewayAddrTel
from kpa_gateway.frame_types.base_types import FrameCMDArgType, FrameID
from kpa_gateway.frame_types.control_command import GatewayCMD
from kpa_gateway.frame_types.message import GatewayLogMessage, GatewayMessage
from kpa_gateway.frame_types.position_telemetry import GatewayPosTel
from kpa_gateway.frame_types.receipt import GatewayReceipt

from python_tcp.client import SocketClient


class ATS_Emulator(QtWidgets.QWidget, _Widgets):
    def __init__(self) -> None:
        super().__init__()
        # self.setupUi(self)
        loadUi(Path(__file__).parent.joinpath('frontend.ui'), self)
        self.setWindowTitle('Имитатор АИК')
        self.client = SocketClient(self.ip_line_edit.text(),
                                   self.port_spin_box.value())
        self.client.received.subscribe(self.on_received)
        self.client.disconnected.subscribe(lambda: self.log_text_browser.append('Disconnected from server'))
        self.client.connected.subscribe(self.on_connected)
        self.receipt_arg_len_spin_box.valueChanged.connect(self.set_receipt_args)
        self.cmd_arg_len_spin_box.valueChanged.connect(self.set_cmd_args)
        self.atm_arg_len_spin_box.valueChanged.connect(self.set_atm_args)
        self.msg_amount_spin_box.valueChanged.connect(self.set_msg_args)
        self.receipt_args: list[MsgArg] = []
        self.cmd_args: list[CMD_Arg] = []
        self.atm_args: list[ATM_Arg] = []
        self.msg_args: list[MsgArg] = []

    def on_received(self, data: bytes) -> None:
        frame: GatewayFrame = GatewayFrame.parse(data)
        self.log_text_browser.append(str(frame))
        is_autorecipe: bool = self.auto_receipt_check_box.isChecked()
        if frame.frame.frame_id == FrameID.CMD and is_autorecipe:
            answer = GatewayFrame(GatewayReceipt(frame.frame.cmd_code, 0))  # type: ignore
            self.log_text_browser.append(str(answer))
            self.client.send(answer.to_bytes())

    def set_msg_args(self, new_value: int) -> None:
        _add_arg(new_value, MsgArg, self.messages_v_layout, self.msg_args)

    def set_atm_args(self, new_value: int) -> None:
        _add_arg(new_value, ATM_Arg, self.atm_v_layout, self.atm_args)

    def set_cmd_args(self, new_value: int) -> None:
        _add_arg(new_value, CMD_Arg, self.cmd_v_layout, self.cmd_args)

    def set_receipt_args(self, new_value: int) -> None:
        _add_arg(new_value, MsgArg, self.receipt_args_v_layout, self.receipt_args)

    def on_receipt_btn_pressed(self) -> None:
        receipt_num: int = self.receipt_type_spin_box.value()
        return_code: int = self.receipt_return_code_spin_box.value()
        args: list[str] = [arg.line_edit.text() for arg in self.receipt_args]
        data = GatewayFrame(GatewayReceipt(receipt_num, return_code, *args))
        self.log_text_browser.append(str(data))
        self.client.send(data.to_bytes())

    def on_cmd_btn_pressed(self) -> None:
        cmd_type: int = self.cmd_type_spin_box.value()
        cmd_code: int  = self.cmd_code_spin_box.value()
        args: list[tuple[FrameCMDArgType, Any]] = [(FrameCMDArgType(arg.arg_type.currentIndex() + 1),
                                                    literal_eval(arg.line_edit.text()))
                                                   for arg in self.cmd_args]
        data = GatewayFrame(GatewayCMD(cmd_type, cmd_code, *args))
        self.log_text_browser.append(str(data))
        self.client.send(data.to_bytes())

    def on_atm_btn_pressed(self) -> None:
        args: list[AddrTelParameter] = [AddrTelParameter(arg.atm_type.value(), arg.arg_num.value(),
                                                         b''.join([struct.pack('<B', literal_eval(val))
                                                                   for val in arg.line_edit.text()]),
                                                         arg.arg_size.value())
                                        for arg in self.atm_args]
        data = GatewayFrame(GatewayAddrTel(*args))
        self.log_text_browser.append(str(data))
        self.client.send(data.to_bytes())

    def on_ptm_btn_pressed(self) -> None:
        text: bytes = self.ptm_plain_text.toPlainText().encode('utf-8')
        data = GatewayFrame(GatewayPosTel(self.ptm_type_spin_box.value(), text))
        self.log_text_browser.append(str(data))
        self.client.send(data.to_bytes())

    def on_msg_btn_pressed(self) -> None:
        args: list[str] = [arg.line_edit.text() for arg in self.msg_args]
        data = GatewayFrame(GatewayMessage(*args))
        self.log_text_browser.append(str(data))
        self.client.send(data.to_bytes())

    def on_log_btn_pressed(self) -> None:
        data = GatewayFrame(GatewayLogMessage(self.log_type_spin_box.value(), self.log_line_edit.text()))
        self.log_text_browser.append(str(data))
        self.client.send(data.to_bytes())

    def on_connect_btn_pressed(self) -> None:
        if self.connect_btn.text() == 'Подключиться':
            if not len(self.ip_line_edit.text()):
                return
            self.client._host = self.ip_line_edit.text()
            self.client.connect()
            self.connect_btn.setText('Отключиться')
        elif self.connect_btn.text() == 'Отключиться':
            self.connect_btn.setText('Подключиться')
            self.client.disconnect()

    def on_connected(self) -> None:
        ip: str = self.ip_line_edit.text()
        port: int = self.port_spin_box.value()
        self.log_text_browser.append(f'Connected to server {ip}:{port}')


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = ATS_Emulator()
    w.show()
    app.exec()