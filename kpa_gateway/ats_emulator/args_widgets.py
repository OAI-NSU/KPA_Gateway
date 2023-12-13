from typing import Type
from PyQt6 import QtWidgets

from kpa_gateway.frame_types.base_types import FrameCMDArgType

class MsgArg(QtWidgets.QWidget):
    def __init__(self, num: int) -> None:
        super().__init__()
        self.num: int = num
        self.h_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.h_layout)
        self.arg_num = QtWidgets.QLabel(text=f'{self.num}')
        self.line_edit = QtWidgets.QLineEdit()
        self.h_layout.addWidget(self.arg_num)
        self.h_layout.addWidget(self.line_edit)

class CMD_Arg(MsgArg):
    def __init__(self, num: int) -> None:
        super().__init__(num)
        self.arg_type = QtWidgets.QComboBox()
        self.arg_type.addItems([val.name for val in list(FrameCMDArgType)])
        self.h_layout.insertWidget(1, self.arg_type)

class ATM_Arg(MsgArg):
    def __init__(self, num: int) -> None:
        super().__init__(num)
        self.arg_type_label = QtWidgets.QLabel(text='ArgType')
        self.arg_num_label = QtWidgets.QLabel(text='ArgNum')
        self.arg_size_label = QtWidgets.QLabel(text='ArgSize')
        self.atm_type = QtWidgets.QSpinBox()
        self.arg_num = QtWidgets.QSpinBox()
        self.arg_size = QtWidgets.QSpinBox()
        [self.h_layout.insertWidget(i, w) for i, w in enumerate([self.arg_type_label, self.atm_type, self.arg_num_label,
                                                                 self.arg_num, self.arg_size_label, self.arg_size], 1)]

def _add_arg(amount: int, arg_class: Type[MsgArg | CMD_Arg | ATM_Arg], layout: QtWidgets.QLayout, storage: list):
    if amount > len(storage):
        arg: MsgArg | CMD_Arg | ATM_Arg = arg_class(amount)
        storage.append(arg)
        layout.addWidget(arg)
    elif len(storage):
        arg = storage.pop()
        arg.deleteLater()

if __name__ == '__main__':
    print([val.name for val in list(FrameCMDArgType)])