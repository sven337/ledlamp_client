#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys, os, subprocess
from PyQt4 import QtGui, QtCore, QtNetwork
from PyQt4.Qt import QPalette
import signal

HUB_IP="192.168.1.6"
HUB_PORT=45888

class LampClient(QtGui.QWidget):
    
    def __init__(self):
        super(LampClient, self).__init__()
        self.initUI()
        
    
    def udp_message(self):
        (buf, address, port) = self.udp_socket.readDatagram(300)
# None of that is hooked up in RF24bridge
#        print("Received " + str(buf) + " from " + str(address) + ":" + str(port))
        try:
            buf = buf.decode("utf-8")
        except UnicodeDecodeError:
            print(str(buf))
            pass
        if buf.startswith("Ledlamp"):
            if buf.startswith("Ledlamp increased") or buf.startswith("Ledlamp decreased"):
                duty_cycle = [s for s in buf.split() if s.isdigit()]
                duty_cycle = duty_cycle[0]
                self.duty_cycle.setText(str(duty_cycle))
        elif buf.startswith("send rf24..."):
            # ignore
            pulse = 0
        elif buf.startswith("... successful"):
            # Radio works
            self.duty_cycle.setStyleSheet("color: #3030FF; font-weight: normal;")
            self.radio_failed = False
        elif buf.startswith("... could not send RF24 cmd"):
            # Radio not working
            self.duty_cycle.setStyleSheet("color: red; font-weight: bold;")
            self.duty_cycle.setText(str("XX"))
            self.radio_failed = True
        else:
            print("Unknown message " + str(buf))
            return
            
 
        
    def lampSliderValue(self, value):
        self.target_pct.setText(str(value))
        self.udp_socket.writeDatagram("ledlamp " + str(value) + "\n", QtNetwork.QHostAddress(HUB_IP), HUB_PORT)
       

    def getScreenBrightness(self):
        out = subprocess.check_output("ddcutil getvcp 0x10 | cut -f2 -d= | cut -f1 -d,", shell=True)
        out=out.strip()
        return out

    def screenSliderValue(self, value):
        os.system("ddcutil setvcp 0x10 %d" % value)
        self.screen_brightness.setText(self.getScreenBrightness())
    

    
    def btn_clicked_slot(self):
        if (self.lamp_slider.value() != 0):
            self.lamp_slider.oldvalue = self.lamp_slider.value()
            self.lamp_slider.setValue(0)
        else:
            self.lamp_slider.setValue(self.lamp_slider.oldvalue)
            
   
    def screenbtn_clicked_slot(self):
        if self.screen_slider.value() > 0:
            self.screen_slider.setValue(0)
        else: 
            self.screen_slider.setValue(75)

    def initUI(self):
        
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 8))
        
        self.setToolTip('This is a <b>QWidget</b> widget')
        
        btn = QtGui.QPushButton('L')
        btn.setToolTip('Eteindre lampe')
        btn.resize(20,20)
        btn.clicked.connect(self.btn_clicked_slot)
        
        self.lamp_slider = QtGui.QSlider(QtCore.Qt.Vertical)
        self.lamp_slider.setMinimum(0);
        self.lamp_slider.setMaximum(99);
        self.lamp_slider.setSingleStep(10);
        self.lamp_slider.setPageStep(30);
        self.lamp_slider.move(0,30);
        self.lamp_slider.setValue(0);
        self.lamp_slider.setTickInterval(10);
        self.lamp_slider.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.lamp_slider.valueChanged.connect(self.lampSliderValue)
        self.lamp_slider.oldvalue = 30
        self.lamp_slider.setTracking(False)
        self.target_pct = QtGui.QLabel("0")
        self.target_pct.setAlignment(QtCore.Qt.AlignCenter)

        self.screen_slider = QtGui.QSlider(QtCore.Qt.Vertical)
        self.screen_slider.setMinimum(0);
        self.screen_slider.setMaximum(100);
        self.screen_slider.setSingleStep(10);
        self.screen_slider.setPageStep(15);
        self.screen_slider.move(0,30);
        cur_brightness = self.getScreenBrightness()
        self.screen_slider.setValue(int(cur_brightness));
        self.screen_slider.setTickInterval(10);
        self.screen_slider.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.screen_slider.valueChanged.connect(self.screenSliderValue)
        self.screen_slider.setTracking(False)
        self.screen_brightness = QtGui.QLabel("0")
        self.screen_brightness.setAlignment(QtCore.Qt.AlignCenter)
        self.screen_brightness.setText(cur_brightness)
        
        
        self.duty_cycle = QtGui.QLabel("0")
        self.duty_cycle.setAlignment(QtCore.Qt.AlignCenter)
        self.duty_cycle.setStyleSheet("color: #3030FF;")
        
        self.temperature = QtGui.QLabel("0")
        self.temperature.hide()
      
        screenbtn = QtGui.QPushButton('N')
        screenbtn.resize(20, 20)
        screenbtn.clicked.connect(self.screenbtn_clicked_slot) 
         
        vlayout2 = QtGui.QVBoxLayout()
        vlayout2.addWidget(btn)
        vlayout2.addWidget(self.lamp_slider)
        vlayout2.addWidget(self.target_pct)
#        vlayout2.addWidget(self.duty_cycle)

        vlayout1 = QtGui.QVBoxLayout()
        vlayout1.addWidget(screenbtn)
        vlayout1.addWidget(self.screen_slider)
        vlayout1.addWidget(self.screen_brightness)
       
        self.layout = QtGui.QHBoxLayout()
        self.layout.addLayout(vlayout1) 
        self.layout.addLayout(vlayout2) 
        self.setLayout(self.layout) 
        self.setMaximumSize(100, 300)
        self.setWindowTitle('Lamp client')
        self.setMinimumHeight(150)
        self.setMinimumWidth(30)
        self.setFixedHeight(200)
        self.setFixedWidth(65)
        self.setWindowFlags(QtCore.Qt.SplashScreen)
        stylesheet = """
/*
	Copyright 2013 Emanuel Claesson

	Licensed under the Apache License, Version 2.0 (the "License");
	you may not use this file except in compliance with the License.
	You may obtain a copy of the License at

		http://www.apache.org/licenses/LICENSE-2.0

	Unless required by applicable law or agreed to in writing, software
	distributed under the License is distributed on an "AS IS" BASIS,
	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	See the License for the specific language governing permissions and
	limitations under the License.
*/

/*
	COLOR_DARK     = #191919
	COLOR_MEDIUM   = #353535
	COLOR_MEDLIGHT = #5A5A5A
	COLOR_LIGHT    = #DDDDDD
	COLOR_ACCENT   = #3D7848
*/

* {
	background: #191919;
	color: #DDDDDD;
	border: 1px solid #5A5A5A;
}

QWidget::item:selected {
	background: #3D7848;
}

QCheckBox, QRadioButton {
	border: none;
}

QRadioButton::indicator, QCheckBox::indicator {
	width: 13px;
	height: 13px;
}

QRadioButton::indicator::unchecked, QCheckBox::indicator::unchecked {
	border: 1px solid #5A5A5A;
	background: none;
}

QRadioButton::indicator:unchecked:hover, QCheckBox::indicator:unchecked:hover {
	border: 1px solid #DDDDDD;
}

QRadioButton::indicator::checked, QCheckBox::indicator::checked {
	border: 1px solid #5A5A5A;
	background: #5A5A5A;
}

QRadioButton::indicator:checked:hover, QCheckBox::indicator:checked:hover {
	border: 1px solid #DDDDDD;
	background: #DDDDDD;
}

QGroupBox {
	margin-top: 6px;
}

QGroupBox::title {
	top: -7px;
	left: 7px;
}

QScrollBar {
	border: 1px solid #5A5A5A;
	background: #191919;
}

QScrollBar:horizontal {
	height: 15px;
	margin: 0px 0px 0px 32px;
}

QScrollBar:vertical {
	width: 15px;
	margin: 32px 0px 0px 0px;
}

QScrollBar::handle {
	background: #353535;
	border: 1px solid #5A5A5A;
}

QScrollBar::handle:horizontal {
	border-width: 0px 1px 0px 1px;
}

QScrollBar::handle:vertical {
	border-width: 1px 0px 1px 0px;
}

QScrollBar::handle:horizontal {
	min-width: 20px;
}

QScrollBar::handle:vertical {
	min-height: 20px;
}

QScrollBar::add-line, QScrollBar::sub-line {
	background:#353535;
	border: 1px solid #5A5A5A;
	subcontrol-origin: margin;
}

QScrollBar::add-line {
	position: absolute;
}

QScrollBar::add-line:horizontal {
	width: 15px;
	subcontrol-position: left;
	left: 15px;
}

QScrollBar::add-line:vertical {
	height: 15px;
	subcontrol-position: top;
	top: 15px;
}

QScrollBar::sub-line:horizontal {
	width: 15px;
	subcontrol-position: top left;
}

QScrollBar::sub-line:vertical {
	height: 15px;
	subcontrol-position: top;
}

QScrollBar:left-arrow, QScrollBar::right-arrow, QScrollBar::up-arrow, QScrollBar::down-arrow {
	border: 1px solid #5A5A5A;
	width: 3px;
	height: 3px;
}

QScrollBar::add-page, QScrollBar::sub-page {
	background: none;
}

QAbstractButton:hover {
	background: #353535;
}

QAbstractButton:pressed {
	background: #5A5A5A;
}

QAbstractItemView {
	show-decoration-selected: 1;
	selection-background-color: #3D7848;
	selection-color: #DDDDDD;
	alternate-background-color: #353535;
}

QHeaderView {
	border: 1px solid #5A5A5A;
}

QHeaderView::section {
	background: #191919;
	border: 1px solid #5A5A5A;
	padding: 4px;
}

QHeaderView::section:selected, QHeaderView::section::checked {
	background: #353535;
}

QTableView {
	gridline-color: #5A5A5A;
}

QTabBar {
	margin-left: 2px;
}

QTabBar::tab {
	border-radius: 0px;
	padding: 4px;
	margin: 4px;
}

QTabBar::tab:selected {
	background: #353535;
}

QComboBox::down-arrow {
	border: 1px solid #5A5A5A;
	background: #353535;
}

QComboBox::drop-down {
	border: 1px solid #5A5A5A;
	background: #353535;
}

QComboBox::down-arrow {
	width: 3px;
	height: 3px;
	border: 1px solid #5A5A5A;
}

QAbstractSpinBox {
	padding-right: 15px;
}

QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
	border: 1px solid #5A5A5A;
	background: #353535;
	subcontrol-origin: border;
}

QAbstractSpinBox::up-arrow, QAbstractSpinBox::down-arrow {
	width: 3px;
	height: 3px;
	border: 1px solid #5A5A5A;
}

QSlider {
	border: none;
}

QSlider::groove:horizontal {
	height: 5px;
	margin: 4px 0px 4px 0px;
}

QSlider::groove:vertical {
	width: 5px;
	margin: 0px 4px 0px 4px;
}

QSlider::handle {
	border: 1px solid #5A5A5A;
	background: #353535;
}

QSlider::handle:horizontal {
	width: 15px;
	margin: -4px 0px -4px 0px;
}

QSlider::handle:vertical {
	height: 15px;
	margin: 0px -4px 0px -4px;
}

QSlider::add-page:vertical, QSlider::sub-page:horizontal {
	background: #3D7848;
}

QSlider::sub-page:vertical, QSlider::add-page:horizontal {
	background: #353535;
}

QLabel {
	border: none;
}

QProgressBar {
	text-align: center;
}

QProgressBar::chunk {
	width: 1px;
	background-color: #3D7848;
}

QMenu::separator {
	background: #353535;
}
   """
        self.setStyleSheet(stylesheet)
        
        self.udp_socket = QtNetwork.QUdpSocket(self)
        if (not self.udp_socket.bind(QtNetwork.QHostAddress.Any, HUB_PORT)):
            print("Unable to bind socket")
        self.udp_socket.readyRead.connect(self.udp_message)
        
        self.show()



        
def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtGui.QApplication(sys.argv)
    lamp_client = LampClient()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
