

from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QAction
from PyQt6.QtTest import QTest
import os, time

from plotterHandler import plotterSerial, plotterJog

### TEMPORARY Jog units are set to 10 for now until worked into GUI
jogUnits = 10

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

        ## Jog up button
        self.button_jogUp = self.findChild(
            QtWidgets.QPushButton, 'button_up')
        self.button_jogUp.clicked.connect(self.jogUp)

        ## Jog down button
        self.button_jogDown = self.findChild(
            QtWidgets.QPushButton, 'button_down')
        self.button_jogDown.clicked.connect(self.jogDown)

        ## Jog right button
        self.button_jogRight = self.findChild(
            QtWidgets.QPushButton, 'button_right')
        self.button_jogRight.clicked.connect(self.jogDown)

        ## Jog left button
        self.button_jogLeft = self.findChild(
            QtWidgets.QPushButton, 'button_left')
        self.button_jogLeft.clicked.connect(self.jogLeft)

        ## Top right button
        self.button_topRight = self.findChild(
            QtWidgets.QPushButton, 'button_topRight')
        self.button_topRight.clicked.connect(self.topRight)

        ## Top left button
        self.button_toplLeft = self.findChild(
            QtWidgets.QPushButton, 'button_topLeft')
        self.button_toplLeft.clicked.connect(self.topLeft)

        ## Bottom left button
        self.button_bottomLeft = self.findChild(
            QtWidgets.QPushButton, 'button_bottomLeft')
        self.button_bottomLeft.clicked.connect(self.bottomLeft)

        ## Bottom right button
        self.button_bottomRight = self.findChild(
            QtWidgets.QPushButton, 'button_bottomRight')
        self.button_bottomRight.clicked.connect(self.bottomRight)



    # Function definitions

    def plotterConfig(self):
        dialogWindow = plotterConfigWindow()
        dialogWindow.exec()

    def jogUp(self):
        plotterJog.up(jogUnits)

    def jogDown(self):
        plotterJog.down(jogUnits)

    def jogRight(self):
        plotterJog.right(jogUnits)

    def jogLeft(self):
        plotterJog.left(jogUnits)

    def topLeft(self):
        plotterJog.topLeft()

    def topRight(self):
        plotterJog.topRight()

    def bottomLeft(self):
        plotterJog.bottomLeft()

    def bottomRight(self):
        plotterJog.bottomRight()





class plotterConfigWindow(QtWidgets.QDialog):
    
    serialObject = None

    def __init__(self):
        super(plotterConfigWindow, self).__init__()
        uic.loadUi('windows/plotterConfig.ui', self)
        self.show()

        self.serialObject = plotterSerial()

        # Configuration
        self.combo_serialPort = self.findChild(
            QtWidgets.QComboBox, 'combo_serialPort')
        self.combo_serialPort.addItems([str(port[0] + ', ' + port[1]) for port in plotterSerial.portList])

        self.button_serialRefresh = self.findChild(
            QtWidgets.QPushButton, 'button_serialPortRefresh')
        self.button_serialRefresh.clicked.connect(self.serialRefresh)

        self.combo_baudRate = self.findChild(
            QtWidgets.QComboBox, 'combo_baud')
        self.combo_baudRate.addItems(plotterSerial.baudRates)

        self.doubleSpin_timeout = self.findChild(
            QtWidgets.QDoubleSpinBox, 'doubleSpin_timeout')

        self.radio_xonxoff = self.findChild(
            QtWidgets.QRadioButton, 'radio_xonxoff')
        self.radio_xonxoff.setChecked(plotterSerial.xonxoff)

        self.radio_dsrdtr = self.findChild(
            QtWidgets.QRadioButton, 'radio_dsrdtr')
        self.radio_dsrdtr.setChecked(plotterSerial.dsrdtr)
        
        self.radio_rtscts = self.findChild(
            QtWidgets.QRadioButton, 'radio_rtscts')
        self.radio_rtscts.setChecked(plotterSerial.rtscts)

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
        self.combo_serialPort.addItems([str(port[0] + ', ' + port[1]) for port in plotterSerial.portList])

    def testConnect(self):
        print('testConnect!')

        plotterSerial.serialPort = plotterSerial.portList[self.combo_serialPort.currentIndex()][0]
        plotterSerial.baudRate = int(plotterSerial.baudRates[self.combo_baudRate.currentIndex()])
        plotterSerial.timeout = self.doubleSpin_timeout.value()
        plotterSerial.xonxoff = self.radio_xonxoff.isChecked()
        plotterSerial.dsrdtr = self.radio_dsrdtr.isChecked()
        plotterSerial.rtscts = self.radio_rtscts.isChecked()

        self.button_connect.setDisabled(True)

        try:
            self.serialObject.connect()
            self.text_textConnect.setText(plotterSerial.model)
        except Exception as e:
            print(e)
            self.text_textConnect.setText('Failed To Connect!')

        self.button_connect.setDisabled(False)