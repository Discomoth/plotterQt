

from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QAction
from PyQt6.QtTest import QTest
import os, time
from plotterHandler import plotterSerial


class mainWindow(QtWidgets.QMainWindow):
    print(os.path.curdir)

    # Main window initialization
    def __init__(self):
        super(mainWindow, self).__init__()
        uic.loadUi('windows/main.ui', self)
        self.show()


        # Action bar configuration
        ## File tab


        ## Config tab
        self.action_plotterConfig = self.findChild(
            QAction, 'action_plotterConfig')
        self.action_plotterConfig.triggered.connect(self.plotterConfig)

        # Graphics view initialization
        self.graphicsWindow = self.findChild(
            QtWidgets.QGraphicsView, 'graphicsView')

        # Control button configuration


    # Function definitions

    def plotterConfig(self):
        dialogWindow = plotterConfigWindow()
        dialogWindow.exec()


class plotterConfigWindow(QtWidgets.QDialog):
    plotterSerial()

    def __init__(self):
        super(plotterConfigWindow, self).__init__()
        uic.loadUi('windows/plotterConfig.ui', self)
        self.show()

        # Configuration
        self.combo_serialPort = self.findChild(
            QtWidgets.QComboBox, 'combo_serialPort')
        self.combo_serialPort.addItems(plotterSerial.portList)

        self.button_serialRefresh = self.findChild(
            QtWidgets.QPushButton, 'button_serialPortRefresh')
        self.button_serialRefresh.clicked.connect(self.serialRefresh)

        self.combo_baudRate = self.findChild(
            QtWidgets.QComboBox, 'combo_baudRate')

        self.doubleSpin_timeout = self.findChild(
            QtWidgets.QDoubleSpinBox, 'doubleSpin_timeout')

        self.radio_xonxoff = self.findChild(
            QtWidgets.QRadioButton, 'radio_xonxoff')

        self.radio_dsrdtr = self.findChild(
            QtWidgets.QRadioButton, 'radio_dsrdtr')

        self.radio_none = self.findChild(
            QtWidgets.QRadioButton, 'radio_none')

        self.combo_model = self.findChild(
            QtWidgets.QComboBox, 'combo_model')

        self.button_connect = self.findChild(
            QtWidgets.QPushButton, 'button_testConnect')
        self.button_connect.clicked.connect(self.testConnect)

        self.text_textConnect = self.findChild(
            QtWidgets.QLineEdit, 'text_testConnect')


        # Functions

    def serialRefresh(self):
        print('serialRefresh!')

        # Disable the buttons while serial refresh operation runs
        self.button_serialRefresh.setDisabled(True)
        self.combo_serialPort.setDisabled(True)

        plotterSerial.refreshPorts()

        self.button_serialRefresh.setDisabled(False)
        self.combo_serialPort.setDisabled(False)
        self.combo_serialPort.clear()
        self.combo_serialPort.addItems(plotterSerial.portList)

        

    def testConnect(self):
        print('testConnect!')

        self.button_connect.setDisabled(True)
        QTest.qWait(1000)
        self.button_connect.setDisabled(False)