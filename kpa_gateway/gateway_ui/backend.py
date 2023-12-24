
from datetime import datetime
from pathlib import Path
from socket import socket
from PyQt6 import QtWidgets
from PyQt6.uic.load_ui import loadUi
from kpa_gateway.api_gateway import API_Gateway


class GatewayServer(QtWidgets.QWidget):
    port_spinbox: QtWidgets.QSpinBox
    tmi1_period_spinbox: QtWidgets.QSpinBox
    tmi2_period_spinbox: QtWidgets.QSpinBox
    tmi1_checkbox: QtWidgets.QCheckBox
    tmi2_checkbox: QtWidgets.QCheckBox
    server_log_text_browser: QtWidgets.QTextBrowser

    def __init__(self, server: API_Gateway) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('frontend.ui'), self)
        self.server: API_Gateway = server
        self.server.server.connected.connect(self.on_connected)
        self.server.server.disconnected.connect(self.on_disconnected)
        self.server.server.received.connect(self.on_received)
        self.server.server.transmited.connect(self.on_transmited)
        self.tmi1_period_spinbox.valueChanged.connect(lambda period: self.server.get_worker('tmi1').set_period(period))  # type: ignore
        self.tmi2_period_spinbox.valueChanged.connect(lambda period: self.server.get_worker('tmi2').set_period(period))  # type: ignore
        self.tmi1_checkbox.stateChanged.connect(self.tmi1_state_handler)
        self.tmi2_checkbox.stateChanged.connect(self.tmi2_state_handler)
        self.message: dict[str, str] = {self.server.ats_emulator_ip: 'имитатором АИК',
                                        self.server.ats_ip: 'АИК',
                                        self.server.feeder_module_ip: 'МФР'}

    def on_connected(self, data: dict[str, socket]) -> None:
        connected_ip: str = list(data)[0]
        ts: str = datetime.now().isoformat(" ", "seconds")
        self.server_log_text_browser.append(f'{ts}: Соединение с {self.message.get(connected_ip, connected_ip)} '\
                                            f'установлено')

    def on_disconnected(self, data: dict[str, socket]) -> None:
        connected_ip: str = list(data)[0]
        ts: str = datetime.now().isoformat(" ", "seconds")
        self.server_log_text_browser.append(f'{ts}: Соединение с {self.message.get(connected_ip, connected_ip)} '\
                                            f'разорвано')

    def on_received(self, data: bytes) -> None:
        ts: str = datetime.now().isoformat(" ", "seconds")
        self.server_log_text_browser.append(f'{ts} rx: {data.hex(" ").upper()}')

    def on_transmited(self, data: bytes) -> None:
        ts: str = datetime.now().isoformat(" ", "seconds")
        self.server_log_text_browser.append(f'{ts} tx: {data.hex(" ").upper()}')

    def disable_telemetry(self) -> bool:
        self.tmi1_checkbox.setChecked(False)
        self.tmi2_checkbox.setChecked(False)
        [worker.stop() for worker in self.server.workers.values()]
        return True

    def enable_telemetry(self) -> bool:
        self.tmi1_checkbox.setChecked(True)
        self.tmi2_checkbox.setChecked(True)
        [worker.start() for worker in self.server.workers.values()]
        return True

    def tmi1_state_handler(self, state: int):
        worker = self.server.get_worker('tmi1')
        if not worker:
            return
        worker.start() if state else worker.stop()

    def tmi2_state_handler(self, state: int):
        worker = self.server.get_worker('tmi2')
        if not worker:
            return
        worker.start() if state else worker.stop()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = GatewayServer(API_Gateway())
    w.show()
    app.exec()

