from PyQt6 import QtWidgets

class _Widgets:
    receipt_type_spin_box: QtWidgets.QSpinBox
    receipt_return_code_spin_box: QtWidgets.QSpinBox
    receipt_arg_len_spin_box: QtWidgets.QSpinBox
    cmd_type_spin_box: QtWidgets.QSpinBox
    cmd_code_spin_box: QtWidgets.QSpinBox
    cmd_arg_len_spin_box: QtWidgets.QSpinBox
    atm_arg_len_spin_box: QtWidgets.QSpinBox
    ptm_type_spin_box: QtWidgets.QSpinBox
    msg_amount_spin_box: QtWidgets.QSpinBox
    log_type_spin_box: QtWidgets.QSpinBox
    port_spin_box: QtWidgets.QSpinBox

    receipt_btn: QtWidgets.QPushButton
    cmd_btn: QtWidgets.QPushButton
    atm_btn: QtWidgets.QPushButton
    ptm_btn: QtWidgets.QPushButton
    msg_btn: QtWidgets.QPushButton
    log_btn: QtWidgets.QPushButton
    connect_btn: QtWidgets.QPushButton

    log_line_edit: QtWidgets.QLineEdit
    msg_line_edit: QtWidgets.QLineEdit
    ip_line_edit: QtWidgets.QLineEdit

    ptm_plain_text: QtWidgets.QPlainTextEdit

    receipt_args_v_layout: QtWidgets.QVBoxLayout
    cmd_v_layout: QtWidgets.QVBoxLayout
    atm_v_layout: QtWidgets.QVBoxLayout
    messages_v_layout: QtWidgets.QVBoxLayout

    log_text_browser: QtWidgets.QTextBrowser

    auto_receipt_check_box: QtWidgets.QCheckBox