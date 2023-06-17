

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QFileDialog, QProgressDialog
from PyQt6.QtGui import QAction
from PyQt6.QtTest import QTest
import os, time

from plotterHandler import plotterAttributes, chiplotlePlotter, serialPlotter, plotterJog

from chiplotle.tools.serialtools import sniff_ports_for_plotters, what_plotter_in_port
from chiplotle.tools.plottertools._instantiate_plotter import _instantiate_plotter
from chiplotle.tools.io import import_hpgl_file
from chiplotle.plotters import plotter as basicPlotterObject
from chiplotle.hpgl import commands

class mainWindow(QtWidgets.QMainWindow):
    print(os.path.curdir)

    # Main window initialization
    def __init__(self):
        super(mainWindow, self).__init__()
        uic.loadUi('windows/main.ui', self)
        self.show()

        # QGraphicsHandling
        self.view_plotPreview = self.findChild(
            QGraphicsView, 'view_plotPreview')

        # Action bar configuration
        ## File tab

        self.action_importHPGL = self.findChild(
            QAction, 'action_importHPGL')
        self.action_importHPGL.triggered.connect(self.importHPGL)

        ## Config tab
        self.action_plotterConfig = self.findChild(
            QAction, 'action_plotterConfig')
        self.action_plotterConfig.triggered.connect(self.plotterConfig)

        # Graphics view initialization
        self.graphicsWindow = self.findChild(
            QtWidgets.QGraphicsView, 'graphicsView')

        # Control button configuration
        self.spinBox_jogDistance = self.findChild(
            QtWidgets.QSpinBox,'spinBox_jogDistance')
        self.spinBox_jogDistance.setValue(plotterAttributes.jogDistance)
        self.spinBox_jogDistance.textChanged.connect(self.jogDistanceChange)

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

        ## Start plot button
        self.button_startPlot = self.findChild(
            QtWidgets.QPushButton, 'button_startPlot')
        self.button_startPlot.clicked.connect(self.startPlot)

        ## Stop plot button
        self.button_stopPlot = self.findChild(
            QtWidgets.QPushButton, 'button_stopPlot')
        self.button_stopPlot.clicked.connect(self.stopPlot)

        ## Dry run button
        self.button_dryRun = self.findChild(
            QtWidgets.QPushButton, 'button_dryRun')
        self.button_dryRun.clicked.connect(self.dryRun)

    # Function definitions

    ## Functions for jogging control

    def plotterConfig(self):
        dialogWindow = plotterConfigWindow()
        dialogWindow.exec()

    ## Jogging control
    def home(self):
        plotterJog.home()

    def jogDistanceChange(self):
        plotterAttributes.jogDistance = self.spinBox_jogDistance.value()

    def jogUp(self):
        plotterJog.up()

    def jogDown(self):
        plotterJog.down()

    def jogRight(self):
        plotterJog.right()

    def jogLeft(self):
        plotterJog.left()

    def topLeft(self):
        plotterJog.topLeft()

    def topRight(self):
        plotterJog.topRight()

    def bottomLeft(self):
        plotterJog.bottomLeft()

    def bottomRight(self):
        plotterJog.bottomRight()


    ## Functions for preview window

    def initializeGraphicsView(self):
        '''
        Initial setup work for the graphics view
        '''
        self.graphicsScene = QGraphicsScene()


    def createPlotArea(self):
        '''
        Makes a pair of rectangles representing the hard and
        soft clipping areas of the plotter. Requires a plotter
        to have been instantiated.
        '''

        if plotterAttributes.plotter != None:
            hardCoords = plotterAttributes.plotter.margins.hard.all_coordinates
            softCoords = plotterAttributes.plotter.margins.soft.all_coordinates

            print('Plotter Hard Coords: ', hardCoords)
            print('Plotter Soft Coords: ', softCoords)

    def setupGraphicsItems(self):
        '''
        Collects and adds items to be rendered in the scene
        to the graphicsScene object. 
        '''

    def renderGraphicsView(self):
        '''
        Renders the graphicsView output.
        '''

        self.view_plotPreview.setScene(self.graphicsScene)
        self.view_plotPreview.render()


    def zoomWheelEvent():
        print("Not Done!")


    ## Functions for file import/export.

    def importHPGL(self):
        self.hpgl_fileLocation = QFileDialog.getOpenFileName(self, 'Open file')[0]
        print(self.hpgl_fileLocation)

        if self.hpgl_fileLocation != None and os.path.splitext(self.hpgl_fileLocation)[1] == '.hpgl':

            if plotterAttributes.serialBackend == 'Chiplotle':
                self.hpglString_chiplotle = import_hpgl_file(self.hpgl_fileLocation)
                print('HPGL Command String length: ' + str(len(self.hpglString_chiplotle)))
            elif plotterAttributes.serialBackend == 'PySerial':
                raise NotImplementedError('The PySerial connect function has not been implemented yet!')



    ## Functions for plotter control.

    def plotterProgress(self):
        '''
        WIP - maybe integrate into MainWindow?
        A simple progress bar to indicate and contain the
        plotter write instance.
        '''

        self.progressMinimum = 0
        self.progressMaximum = len(self.hpglString_chiplotle)
        self.progressCurrent = 0

        returnValues = QProgressDialog(
            "Plot progress",
            "Cancel plot",
            self.progressMinimum,
            self.progressMaximum)


    def startPlot(self):
        '''
        Starts sending data to the plotter.
        Stop flag stops the plot when false.
        '''
        plotterAttributes.pen = 1
        setupCommands = [
            commands.SP(plotterAttributes.pen).format,
            commands.VS(plotterAttributes.penVelocity).format,
            commands.AS(plotterAttributes.penAccel).format,
            commands.FS(plotterAttributes.penForce).format
        ]

        if len(self.hpglString_chiplotle) != 0:
            for command in setupCommands:
                plotterAttributes.plotter.write(command)
                time.sleep(1.5)
            
            plotterAttributes.plotter.write(self.hpglString_chiplotle)
        elif len(self.hpglString_chiplotle) == 0:
            print("No HPGL file loaded!")

    def stopPlot(self):
        raise NotImplementedError("Not implemented yet!")

    def dryRun(self):
        '''
        Starts sending data to the plotter.
        Stop flag stops the plot when True.
        '''
        if len(self.hpglString_chiplotle) != 0:
            plotterAttributes.plotter.write(commands.SP(0))
            #plotterAttributes.plotter.write_file(self.hpgl_fileLocation)
            plotterAttributes.plotter.write(self.hpglString_chiplotle)
        elif len(self.hpglString_chiplotle) == 0:
            print("No HPGL file loaded!")



class plotterConfigWindow(QtWidgets.QDialog):
    
    serialObject = None
    # serialBackendList = ['Chiplotle', 'PySerial']
    serialBackendList = ['Chiplotle']

    serialBackend = 0

    def __init__(self):
        super(plotterConfigWindow, self).__init__()
        uic.loadUi('windows/plotterConfig.ui', self)
        self.show()

        # QDialogButtonBox setup
        self.buttonBox = self.findChild(
            QtWidgets.QDialogButtonBox, 'buttonBox')
        self.buttonBox.accepted.connect(self.storeInformation)

        # Configuration element setup
        self.combo_serialBackend = self.findChild(
            QtWidgets.QComboBox, 'combo_serialBackend')
        self.combo_serialBackend.addItems(self.serialBackendList)
        self.combo_serialBackend.setCurrentIndex(plotterAttributes.serialBackendIndex)
        self.combo_serialBackend.currentTextChanged.connect(self.serialBackendUpdate)

        self.combo_serialPort = self.findChild(
            QtWidgets.QComboBox, 'combo_serialPort')
        self.combo_serialPort.addItems([str(port[0] + ', ' + port[1]) for port in plotterAttributes.portList])
        self.combo_serialPort.setCurrentIndex(plotterAttributes.portIndex)

        self.button_serialRefresh = self.findChild(
            QtWidgets.QPushButton, 'button_serialPortRefresh')
        self.button_serialRefresh.clicked.connect(self.serialRefresh)

        self.combo_baudRate = self.findChild(
            QtWidgets.QComboBox, 'combo_baud')
        self.combo_baudRate.addItems(plotterAttributes.baudRates)
        self.combo_baudRate.setCurrentIndex(plotterAttributes.baudRateIndex)
        self.combo_baudRate.setDisabled(True)

        self.doubleSpin_timeout = self.findChild(
            QtWidgets.QDoubleSpinBox, 'doubleSpin_timeout')
        self.doubleSpin_timeout.setValue(plotterAttributes.timeout)
        self.doubleSpin_timeout.setDisabled(True)

        self.radio_xonxoff = self.findChild(
            QtWidgets.QRadioButton, 'radio_xonxoff')
        self.radio_xonxoff.setChecked(plotterAttributes.xonxoff)
        self.radio_xonxoff.setDisabled(True)

        self.radio_dsrdtr = self.findChild(
            QtWidgets.QRadioButton, 'radio_dsrdtr')
        self.radio_dsrdtr.setChecked(plotterAttributes.dsrdtr)
        self.radio_dsrdtr.setDisabled(True)
        
        self.radio_rtscts = self.findChild(
            QtWidgets.QRadioButton, 'radio_rtscts')
        self.radio_rtscts.setChecked(plotterAttributes.rtscts)

        self.radio_none = self.findChild(
            QtWidgets.QRadioButton, 'radio_none')

        self.doubleSpin_flowDelay = self.findChild(
            QtWidgets.QDoubleSpinBox, 'doubleSpin_flowDelay')
        self.doubleSpin_flowDelay.setValue(plotterAttributes.flowDelay)

        self.combo_model = self.findChild(
            QtWidgets.QComboBox, 'combo_model')
        self.combo_model.setDisabled(True)

        self.button_testConnect = self.findChild(
            QtWidgets.QPushButton, 'button_testConnect')
        self.button_testConnect.clicked.connect(self.testConnect)

        self.text_textConnect = self.findChild(
            QtWidgets.QLineEdit, 'text_testConnect')

        self.button_initializePlotter= self.findChild(
            QtWidgets.QPushButton, 'button_initialize')
        self.button_initializePlotter.clicked.connect(self.initializePlotter)

        self.text_instantiatedPlotter = self.findChild(
            QtWidgets.QLineEdit, 'text_instantiatedPlotter')
        self.text_instantiatedPlotter.setText(plotterAttributes.plotterInfo)

        self.text_drawingLimits = self.findChild(
            QtWidgets.QLineEdit, 'text_drawingLimits')
        self.text_drawingLimits.setText(plotterAttributes.drawingLimits)

        self.text_bufferSize = self.findChild(
            QtWidgets.QLineEdit, 'text_bufferSize')
        self.text_bufferSize.setText(plotterAttributes.bufferSize)


        # Functions

    def storeInformation(self):
        '''
        Takes infromation from the plotter config dialog window and
        enters it into the plotterAttributes class variables
        '''

        plotterAttributes.serialBackendIndex = self.combo_serialBackend.currentIndex()
        plotterAttributes.serialBackend = self.combo_serialBackend.currentText()
        plotterAttributes.port = plotterAttributes.portList[self.combo_serialPort.currentIndex()][0]
        plotterAttributes.portIndex = self.combo_serialPort.currentIndex()
        plotterAttributes.baudRate = int(plotterAttributes.baudRates[self.combo_baudRate.currentIndex()])
        plotterAttributes.baudRateIndex = self.combo_baudRate.currentIndex()
        plotterAttributes.timeout = self.doubleSpin_timeout.value()
        plotterAttributes.xonxoff = self.radio_xonxoff.isChecked()
        plotterAttributes.dsrdtr = self.radio_dsrdtr.isChecked()
        plotterAttributes.rtscts = self.radio_rtscts.isChecked()
        plotterAttributes.noFlowCtrl = self.radio_none.isChecked()
        plotterAttributes.flowDelay = self.doubleSpin_flowDelay.value()



    def serialRefresh(self):
        print('serialRefresh!')

        # Disable the buttons while serial refresh operation runs
        self.button_serialRefresh.setDisabled(True)
        self.combo_serialPort.setDisabled(True)

        plotterAttributes.refreshPorts()

        self.button_serialRefresh.setDisabled(False)
        self.combo_serialPort.setDisabled(False)
        self.combo_serialPort.clear()
        self.combo_serialPort.addItems([str(port[0] + ', ' + port[1]) for port in plotterAttributes.portList])

    def serialBackendUpdate(self):

        if self.combo_serialBackend.currentText() == 'Chiplotle':
            self.combo_model.setDisabled(True)
            self.combo_baudRate.setDisabled(True)
            self.doubleSpin_timeout.setDisabled(True)
            self.radio_xonxoff.setDisabled(True)
            self.radio_dsrdtr.setDisabled(True)

        elif self.combo_serialBackend.currentText() == 'PySerial':
            self.combo_model.setDisabled(False)
            self.combo_baudRate.setDisabled(False)
            self.doubleSpin_timeout.setDisabled(False)
            self.radio_xonxoff.setDisabled(False)
            self.radio_dsrdtr.setDisabled(False)


    def testConnect(self):
        print('testConnect!')

        # Get the current serial port from the serialPort combo box
        plotterAttributes.port = plotterAttributes.portList[self.combo_serialPort.currentIndex()][0]

        # Check which serial control backend is selected
        if self.combo_serialBackend.currentText() == 'Chiplotle':

            print("Serial Port: ", plotterAttributes.port)

            foundPlotters = sniff_ports_for_plotters([plotterAttributes.port])
            foundPlotters_keys = [x for x in foundPlotters.keys()]


            self.button_testConnect.setDisabled(True)

            if len(foundPlotters) == 0:
                self.text_textConnect.setText('Chiplotle found no plotters!')
            else:
                self.text_textConnect.setText(foundPlotters[plotterAttributes.port])

            self.button_testConnect.setDisabled(False)

        elif self.combo_serialBackend.currentText() == 'PySerial':

            self.serialObject = serialPlotter()

            plotterAttributes.port = plotterAttributes.portList[self.combo_serialPort.currentIndex()][0]
            plotterAttributes.baudRate = int(plotterAttributes.baudRates[self.combo_baudRate.currentIndex()])
            plotterAttributes.timeout = self.doubleSpin_timeout.value()
            plotterAttributes.xonxoff = self.radio_xonxoff.isChecked()
            plotterAttributes.dsrdtr = self.radio_dsrdtr.isChecked()
            plotterAttributes.rtscts = self.radio_rtscts.isChecked()

            self.button_testConnect.setDisabled(True)

            try:
                self.serialObject.connect()
                self.text_textConnect.setText(plotterAttributes.model)
            except Exception as e:
                print(e)
                self.text_textConnect.setText('Failed To Connect!')

            self.button_testConnect.setDisabled(False)

    def initializePlotter(self):

        # Get the current serial port from the serialPort combo box
        plotterAttributes.port = plotterAttributes.portList[self.combo_serialPort.currentIndex()][0]

        if self.combo_serialBackend.currentText() == 'Chiplotle':
            
            # Collect data for the selected plotter
            plotterAttributes.model = what_plotter_in_port(plotterAttributes.port)

            # TODO:
            # This next bit needs a safe exit path. Right now, Chiplotle calls a commandline
            # interactive prompt for manual config. Ideally, it'd return an error instead...

            # Instantiate the plotter object
            plotterAttributes.plotter = _instantiate_plotter(plotterAttributes.port, plotterAttributes.model)

            # Get info to be returned to the config window
            plotterAttributes.plotterInfo = plotterAttributes.plotter.type
            coords = plotterAttributes.plotter.margins.soft.all_coordinates
            plotterAttributes.drawingLimits = "left %s; bottom %s; right %s; top %s" % coords
            plotterAttributes.bufferSize = str(plotterAttributes.plotter.buffer_size)

            # Write info to config window
            self.text_instantiatedPlotter.setText(plotterAttributes.plotterInfo)
            self.text_drawingLimits.setText(plotterAttributes.drawingLimits)
            self.text_bufferSize.setText(plotterAttributes.bufferSize)

            # Plotter RTS/CTS implementation
            plotterAttributes.plotter.rtscts = self.radio_rtscts.isChecked()
            plotterAttributes.plotter.flowDelay = self.doubleSpin_flowDelay.value()

            # Send initialize command to plotter
            plotterAttributes.plotter.write(commands.IN().format)

        elif self.combo_serialBackend.currentText() == 'PySerial':
            raise NotImplementedError('The PySerial connect function has not been implemented yet!')


        