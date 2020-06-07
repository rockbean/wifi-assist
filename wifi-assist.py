#!/usr/bin/env python
import sys
import os
from PyQt5 import QtCore, QtWidgets, uic, QtGui
import json
import dev_info
import dev_radio

DevAstUI = "devast.ui"

radio_list = ["wifi0", "wifi1"]
radio_mode = {"access": "images/Access.png", "dual": "images/Dual.png",
              "mesh": "images/Mesh.png", "sensor": "images/Sensor.png"}
vap_state = {"Up": "images/Up.png", "Down": "images/Down.png"}

current_directory = os.path.dirname(os.path.realpath(__file__))


class DevAstWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(DevAstWindow, self).__init__()
        ui_path = os.path.join(current_directory, 'mainwindow.ui')
        uic.loadUi(ui_path, self)
        self._dev_info = dev_info.DevInfo()
        self.xDevPwd = XPwdLineEdit(self)
        self.layoutDevLog.addWidget(self.xDevPwd)
        self.lnDevUsr.setMinimumHeight(32)
        self.lnDevIp.setMinimumHeight(32)
        self.btnDevCon.clicked.connect(self.connect)
        self.btnDevClose.clicked.connect(self.close)
        self._DbgLvlGroup = QtWidgets.QButtonGroup(self)
        self._DbgLvlGroup.addButton(self.rdoLogBuf, 0)
        self._DbgLvlGroup.addButton(self.rdoLogFlash, 1)
        self.rdoLogBuf.setChecked(True)
        self.rdoLogBuf.clicked.connect(self.set_dbg_flag)
        self.rdoLogFlash.clicked.connect(self.set_dbg_flag)
        self._debug_flag = "buffered"
        self.btnShowLog.clicked.connect(self.show_log)
        self.btnShowConfig.clicked.connect(self.show_config)
        self.btnAddConfig.clicked.connect(self.add_config)
        self.btnDelConfig.clicked.connect(self.del_config)
        self.qss = open('qss/metro.qss', 'r')
        self.qssStyle = self.qss.read()
        self.setStyleSheet(self.qssStyle)

    def connect(self):
        ip = str(self.lnDevIp.text())
        usr = str(self.lnDevUsr.text())
        pwd = str(self.xDevPwd.text())
        conn = self._dev_info.dev_connect(ip, usr, pwd)
        if conn == True:
            self.lblDevStatus.setText("Device access")
            self.imgDevCon.setPixmap(QtGui.QPixmap("images/Connect.png"))
            for radio in radio_list:
                iface = self._dev_info.dev_get_radio(radio)
                self.show_radio(dev_radio.DevRadio(iface))
        else:
            self.lblDevStatus.setText("Device deny")
            self.imgDevCon.setPixmap(
                QtGui.QPixmap("images/Disconnect.png"))

    def close(self):
        if self._dev_info.dev_is_connect() == True:
            self._dev_info.dev_disconnect()
            self.lblDevStatus.setText("Device close")
        else:
            self.lblDevStatus.setText("Device deny")
        self.imgDevCon.setPixmap(QtGui.QPixmap("images/Disconnect.png"))

    def set_dbg_flag(self):
        id = self._DbgLvlGroup.checkedId()
        if id == 0:
            self._debug_flag = "buffered"
        elif id == 1:
            self._debug_flag = "flash"
        else:
            self._debug_flag = "buffered"

    def show_log(self):
        ret, log = self._dev_info.dev_show_log(self._debug_flag)
        self.txtDevLog.clear()
        for line in log:
            self.txtDevLog.append(line)

    def show_radio(self, radio):
        if radio._name == "wifi0":
            radio_id = 0
        elif radio._name == "wifi1":
            radio_id = 1

        mode_name = "lblDev"+str(radio_id)+"Mode"
        mode = self.findChild(QtWidgets.QLabel, mode_name)
        mode.setPixmap(QtGui.QPixmap(radio_mode[radio._mode]))
        mode.setToolTip(radio._mode)

        freq_name = "lblDev"+str(radio_id)+"Freq"
        freq = self.findChild(QtWidgets.QLabel, freq_name)
        freq.setText(str(radio._channel) + "(" + radio._chan_width + ")")

        power_name = "lblDev"+str(radio_id)+"Power"
        power = self.findChild(QtWidgets.QLabel, power_name)
        power.setText(str(radio._txpower))

        self.show_radio_vap(radio_id, radio._vap)

    def show_radio_vap(self, radio_id, vaps):
        for vap in vaps:
            img_name = "img"+str(radio_id)+"_"+vap._name[-1]+"up"
            img = self.findChild(QtWidgets.QLabel, img_name)
            img.setPixmap(QtGui.QPixmap(vap_state[vap._state]))

            ssid_name = "lbl"+str(radio_id)+"_"+vap._name[-1]+"Ssid"
            ssid = self.findChild(QtWidgets.QLabel, ssid_name)
            ssid.setText(vap._ssid)

            auth_name = "lbl"+str(radio_id)+"_"+vap._name[-1]+"Auth"
            auth = self.findChild(QtWidgets.QLabel, auth_name)
            auth.setText(vap._auth)

    def show_config(self):
        self.lstConfig.clear()
        ret, conf = self._dev_info.dev_show_configure()
        self.lstConfig.addItems(conf)

    def add_config(self):
        add = AddDlg('Add Configure:', self)
        if add.exec_():
            conf = add.content
            self.lstConfig.addItem(conf)
            # Todo add this conf in device

    def del_config(self):
        result = QtWidgets.QMessageBox.warning(self,
                                               "Delete Configure",
                                               "Are you sure you want to do this?",
                                               QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if result == QtWidgets.QMessageBox.Ok:
            conf_deleted = self.lstConfig.takeItem(self.lstConfig.currentRow())
            # Todo undo this conf in device
            conf_deleted = None

    def closeEvent(self, event):
        result = QtWidgets.QMessageBox.question(self,
                                                "Confirm Exit...",
                                                "Are you sure you want to exit ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            if self._dev_info.dev_is_connect() == True:
                self._dev_info.dev_disconnect()
            event.accept()


class XPwdLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(XPwdLineEdit, self).__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.image = XLabel(self)
        self.image.setCursor(QtCore.Qt.ArrowCursor)
        self.image.setFocusPolicy(QtCore.Qt.NoFocus)
        self.image.setStyleSheet("border: none;")
        self.image.setPixmap(QtGui.QPixmap("images/Pwd.png"))
        self.image.adjustSize()
        self.image.setScaledContents(True)
        self.layout.addWidget(
            self.image, alignment=QtCore.Qt.AlignRight)
        self.textChanged.connect(self.changed)
        self.image.hide()
        self.image.clicked.connect(self.show_text)
        self._show_text = False
        self.setMinimumHeight(32)
        self.setMaxLength(32)
        self.setEchoMode(QtWidgets.QLineEdit.Password)

    def show_text(self):
        self._show_text = not self._show_text
        if self._show_text == True:
            self.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.setEchoMode(QtWidgets.QLineEdit.Password)

    def changed(self, text):
        if len(text) > 0:
            self.image.show()
        else:  # if entry is empty
            self.image.hide()


class XLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(XLabel, self).__init__(parent)

    def mousePressEvent(self, event):
        event.accept()
        self.clicked.emit()


class AddDlg(QtWidgets.QDialog):
    def __init__(self, title, content=None, parent=None):
        super(AddDlg, self).__init__(parent)
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        lblDlgAddTitle = QtWidgets.QLabel(title)
        lblDlgAddTitle.setWordWrap(True)

        self.content_edit = QtWidgets.QLineEdit(content)
        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(lblDlgAddTitle)
        v_box.addWidget(self.content_edit)
        v_box.addWidget(btns)
        self.setLayout(v_box)

        self.content = None

    def accept(self):
        self.content = str(self.content_edit.text())
        QtWidgets.QDialog.accept(self)

    def reject(self):
        QtWidgets.QDialog.reject(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DevAstWindow()
    window.show()
    sys.exit(app.exec_())
