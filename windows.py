

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QFileDialog, QProgressDialog, QColorDialog, QListView, QAbstractItemView
from PyQt6.QtGui import QAction, QIcon, QColor, QPalette
from PyQt6.QtTest import QTest
from PyQt6.QtCore import pyqtSlot, QAbstractListModel, Qt, QThread, QObject, pyqtSignal

import os, time
from copy import deepcopy

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
        #self.action_importHPGL = self.findChild(QAction, 'action_importHPGL')
        self.action_importHPGL.triggered.connect(self.importHPGL)

        ## Config tab
        #self.action_plotterConfig = self.findChild(QAction, 'action_plotterConfig')
        self.action_plotterConfig.triggered.connect(self.plotterConfig)

        #self.action_penConfig = self.findChild(QAction, 'action_penConfig')
        self.action_penConfig.triggered.connect(self.penConfig)

        # Graphics view initialization
        self.graphicsWindow = self.findChild(QtWidgets.QGraphicsView, 'graphicsView')

        # Control button configuration
        #self.spinBox_jogDistance = self.findChild(QtWidgets.QSpinBox,'spinBox_jogDistance')
        self.spinBox_jogDistance.setValue(plotterAttributes.jogDistance)
        self.spinBox_jogDistance.textChanged.connect(self.jogDistanceChange)

        ## Active Pen comboBox
        #self.comboBox_activePen = self.findChild(QtWidgets.QComboBox, 'comboBox_activePen')
        self.comboBox_activePen.addItems(plotterAttributes.penConfig.keys())
        self.comboBox_activePen.setCurrentIndex(0)
        self.comboBox_activePen.currentTextChanged.connect(self.changeActivePen)

        ## Home Button
        #self.button_home = self.findChild(QtWidgets.QPushButton, 'button_home')
        self.button_home.clicked.connect(self.home)

        ## Jog up button
        self.button_jogUp = self.findChild(QtWidgets.QPushButton, 'button_up')
        self.button_jogUp.clicked.connect(self.jogUp)

        ## Jog down button
        self.button_jogDown = self.findChild(QtWidgets.QPushButton, 'button_down')
        self.button_jogDown.clicked.connect(self.jogDown)

        ## Jog right button
        self.button_jogRight = self.findChild(QtWidgets.QPushButton, 'button_right')
        self.button_jogRight.clicked.connect(self.jogRight)

        ## Jog left button
        self.button_jogLeft = self.findChild(QtWidgets.QPushButton, 'button_left')
        self.button_jogLeft.clicked.connect(self.jogLeft)

        ## Top right button
        #self.button_topRight = self.findChild(QtWidgets.QPushButton, 'button_topRight')
        self.button_topRight.clicked.connect(self.topRight)

        ## Top left button
        #self.button_topLeft = self.findChild(QtWidgets.QPushButton, 'button_topLeft')
        self.button_topLeft.clicked.connect(self.topLeft)

        ## Bottom left button
        #self.button_bottomLeft = self.findChild(QtWidgets.QPushButton, 'button_bottomLeft')
        self.button_bottomLeft.clicked.connect(self.bottomLeft)

        ## Bottom right button
        #self.button_bottomRight = self.findChild(QtWidgets.QPushButton, 'button_bottomRight')
        self.button_bottomRight.clicked.connect(self.bottomRight)

        ## Start plot button
        #self.button_startPlot = self.findChild(QtWidgets.QPushButton, 'button_startPlot')
        self.button_startPlot.clicked.connect(self.startPlot)

        ## Stop plot button/stopFlag creation
        #self.button_stopPlot = self.findChild(QtWidgets.QPushButton, 'button_stopPlot')
        self.button_stopPlot.clicked.connect(self.stopPlot)
        self.stopFlag = False

        ## Dry run button
        #self.button_dryRun = self.findChild(QtWidgets.QPushButton, 'button_dryRun')
        self.button_dryRun.clicked.connect(self.dryRun)

        # Multiplot Configuration
        ## listWidget
        self.elementModel = multiPlotModel()
        self.listView_multiPlot = self.findChild(
            QtWidgets.QListView, 'listView_multiPlot')
        

        self.listView_multiPlot.setModel(self.elementModel)
        #self.listView_multiPlot.setMovement(QListView.Movement.Free)
        #self.listView_multiPlot.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        # TODO
        # Add drag and drop functionality. It is implemented using the 
        # item flags. Need to find out how to implement those...
        # The flag attribute is under QModelIndexes

        ## Element Selection comboBox
        self.comboBox_selectElement.addItems(plotterAttributes.elementList)
        self.comboBox_selectElement.setCurrentIndex(0)
        self.comboBox_selectElement.currentTextChanged.connect(self.selectElement)

        ## Buttons
        self.button_addElement.clicked.connect(self.addElement)
        self.button_delElement.clicked.connect(self.delElement)
        self.button_resetFlags.clicked.connect(self.flagResetButton)
        self.button_startPlot2.clicked.connect(self.startPlot)

        self.plotterConfig()
        self.penConfig()

    # Function definitions

    ## Config Windows

    ### Plotter config window
    def plotterConfig(self):
        dialogWindow = plotterConfigWindow()
        dialogWindow.exec()

    ### penConfig window
    def penConfig(self):
        dialogWindow = penConfigWindow()
        dialogWindow.exec()
        self.comboBox_activePen.clear()
        self.comboBox_activePen.addItems(plotterAttributes.penConfig.keys())

    ### Multiplot Config Windows
    ## MultiPlot functions
    
    def selectElement(self):
        self.selectedElement = plotterAttributes.elementList[self.comboBox_selectElement.currentIndex()]
        #self.elementType = plotterAttributes.elementList[self.selectedElement]

    def addElement(self):

        if self.comboBox_selectElement.currentText() == 'HPGL Plot':
            dialogWindow = addHPGLWindow()
            if dialogWindow.exec():
                HPGLelement = dialogWindow.element
                self.elementModel.elements.append(HPGLelement)
                self.elementModel.layoutChanged.emit()

        elif self.comboBox_selectElement.currentText() == 'Wait':
            dialogWindow = addWaitWindow()
            if dialogWindow.exec():
                waitElement = dialogWindow.element
                self.elementModel.elements.append(waitElement)
                self.elementModel.layoutChanged.emit()

        elif self.comboBox_selectElement.currentText() == 'Pause':
            dialogWindow = addPauseWindow()
            if dialogWindow.exec():
                pauseElement = dialogWindow.element
                self.elementModel.elements.append(pauseElement)
                self.elementModel.layoutChanged.emit()

        elif self.comboBox_selectElement.currentText() == 'Page Feed':
            dialogWindow = addPageFeedWindow()
            if dialogWindow.exec():
                pageFeedElement = dialogWindow.element
                self.elementModel.elements.append(pageFeedElement)
                self.elementModel.layoutChanged.emit()

        elif self.comboBox_selectElement.currentText() == 'Repeat':
            dialogWindow = addRepeatWindow()
            if dialogWindow.exec():
                repeatElement = dialogWindow.element
                self.elementModel.elements.append(repeatElement)
                self.elementModel.layoutChanged.emit()

        else:
            print("Not implemented yet! :,(")

    def delElement(self):
        indexes = self.listView_multiPlot.selectedIndexes()
        if indexes:
            #index = indexes[0]
            for index in indexes:
                del self.elementModel.elements[index.row()]
            self.elementModel.layoutChanged.emit()
            #self.listView_multiPlot.clearSelection()

    def flagResetButton(self):
        self.resetElementFlags(False)


    ## Active pen control
    def changeActivePen(self):
        if self.comboBox_activePen != '':
            plotterAttributes.activePen = self.comboBox_activePen.currentText()
            print("Active Pen: {}".format(plotterAttributes.activePen))
        else:
            pass

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

        # Data Structure(QModelIndex/multiplot elements):

        # (status, type, name, info)

        # elementStatus - bool - element completed?
        # elementType - str - the type of the element
        # elementName - str - the name of the element
        # info - dictIndex - entry containing step info

        '''

        if plotterAttributes.plotter == None:
            print("Plotter not initialized!")

        self.multiPlotRepeatCount = None
        self.multiPlotRepeatRemainder = None

        # Multiplot handling
        if self.elementModel.rowCount() > 0:
        # Try catch added for keyboard interrupts
            try:
                while True:
                    if self.stopFlag:
                        break

                    for elementIndex, element in enumerate(self.elementModel.elements):

                        # Insert and if conditional to catch the stop flag and make the function return?
                        # Completed plots will be skipped and incomplete ones will remain...
                        # Do a layoutChanged.emit() at end of each iteration to update the listView?
                        
                        # Loop stopFlag break
                        if self.stopFlag:
                            break
                        # Check if element has been completed already
                        if element[0]:
                            pass

                        elif not element[0]:
                            # Determine element type
                            if element[1] == 'HPGL Plot':
                                print('HPGL Element')

                                penConfigs = element[3]['HPGL Plot']['penConfig']
                                plotInfo = element[3]['HPGL Plot']['chiplotleHPGL']

                                # Pen setup
                                ## Get the pen info and make into list of chiplotle
                                ## HPGL objects.
                                setupCommands = [
                                    commands.SP(penConfigs['penNumber']),
                                    commands.VS(penConfigs['velocity']),
                                    commands.AS(penConfigs['acceleration']),
                                    commands.FS(penConfigs['force']),
                                ]

                                ## Iterate through the setup commands, writing to plotter
                                for command in setupCommands:
                                    plotterAttributes.plotter.write(command)
                                    time.sleep(1)

                                # Plot setup
                                plotterAttributes.plotter.write(plotInfo)

                            elif element[1] == 'Wait':
                                print('Wait Element')
                                waitTime = element[3]['Wait']['waitTime']

                                time.sleep(waitTime)
                                print('Waited: {} Seconds'.format(waitTime))

                            elif element[1] == 'Pause':
                                dialogWindow = pauseWindow()
                                if dialogWindow.exec():
                                    print('Accepted!')
                                else:
                                    print('Rejected - multiPlot sequence stopping')
                                    self.stopFlag = True

                            elif element[1] == 'Page Feed':
                                pageFeedCommand = commands.PG()
                                plotterAttributes.plotter.write(pageFeedCommand)

                            elif element[1] == 'Repeat':

                                # If it appears this is the first repeat element encountered
                                if self.multiPlotRepeatCount == None:
                                    self.multiPlotRepeatCount = element[3]['Repeat']['count']
                                    self.multiPlotRepeatRemainder = element[3]['Repeat']['remaining'] - 1

                                # If it appears this is a cycle of the repeat
                                elif self.multiPlotRepeatCount != None:
                                    print('Plots remaining: {}'.format(self.multiPlotRepeatRemainder) + '/{}'.format(self.multiPlotRepeatCount))
                                    pass

                                else:
                                    print('Repeat Element parsing missed if catches')

                            else:
                                print('Unknown multiPlot Element entry in startPlot command')

                            # To indicate plotting complete, the first item in the element
                            # tuple, the elementStatus is changed to True to indicate it
                            # has already been run.

                            # Make a new tuple by adding a single item tuple to the front
                            # of the value of the element in the elementModel.
                            newTuple = tuple([True]) + self.elementModel.elements[elementIndex][1:]

                            # Write the new tuple to the element.
                            self.elementModel.elements[elementIndex] = newTuple
                            self.elementModel.layoutChanged.emit()

                    if self.multiPlotRepeatRemainder == None:
                        self.stopFlag = True
                        
                        # Reset the element completion states
                        self.resetElementFlags(False)

                    elif not self.multiPlotRepeatRemainder <= 0:
                        # Deincrement remaining plot value
                        self.multiPlotRepeatRemainder -= 1

                        # Reset flag states to allow repeat plot
                        self.resetElementFlags(False)

                    elif self.multiPlotRepeatRemainder <= 0:
                        self.stopFlag = True

                    else:
                        print("Oops! Infinite loop in startPlot!")
            except KeyboardInterrupt:
                print("Sequence suspended via KeyboardInterrupt")

        # Old style of single plot handling - sort of outdated now...
        elif self.elementModel.rowCount() > 0 and len(self.hpglString_chiplotle) != 0:

            plotterAttributes.pen = plotterAttributes.activePen

            setupCommands = [
                commands.SP(plotterAttributes.penConfig[plotterAttributes.activePen]['penNumber']).format,
                commands.VS(plotterAttributes.penConfig[plotterAttributes.activePen]['velocity']).format,
                commands.AS(plotterAttributes.penConfig[plotterAttributes.activePen]['acceleration']).format,
                commands.FS(plotterAttributes.penConfig[plotterAttributes.activePen]['force']).format
            ]

            if len(self.hpglString_chiplotle) != 0:
                for command in setupCommands:
                    plotterAttributes.plotter.write(command)
                    time.sleep(1.5)
                
                plotterAttributes.plotter.write(self.hpglString_chiplotle)

        elif self.elementModel.rowCount() > 0 and len(self.hpglString_chiplotle) == 0:
            print("No HPGL file loaded!")

        # stopFlag reset
        if self.stopFlag:
            self.stopFlag = False

    def multiPlot(self):
        '''
        Move multiplot stuff here someday?
        '''

    def resetElementFlags(self, flagState: bool):

        for elementIndex, element in enumerate(self.elementModel.elements):
            # Make a new tuple by adding a single item tuple to the front
            # of the value of the element in the elementModel.
            newTuple = tuple([flagState]) + self.elementModel.elements[elementIndex][1:]

            # Write the new tuple to the element.
            self.elementModel.elements[elementIndex] = newTuple
        
        self.elementModel.layoutChanged.emit()

    def stopPlot(self):
        self.stopFlag = True
        raise NotImplementedError("Not implemented yet!")

    def dryRun(self):
        '''
        Starts sending data to the plotter.
        Stop flag stops the plot when True.
        '''

        raise NotImplementedError("Not implemented yet!")
    
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
        self.radio_none.setChecked(plotterAttributes.noFlowCtrl)

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

            # Park current pen if applicable
            if b'SP' in plotterAttributes.plotter.allowedHPGLCommands:
                plotterAttributes.plotter.write(commands.SP(0))

        elif self.combo_serialBackend.currentText() == 'PySerial':
            raise NotImplementedError('The PySerial connect function has not been implemented yet!')

class penConfigWindow(QtWidgets.QDialog):

    def __init__(self):
        print('placeholder')
        super(penConfigWindow, self).__init__()
        uic.loadUi('windows/penConfig.ui', self)
        self.show()

        # Setup pen selection
        self.comboBox_pen = self.findChild(
            QtWidgets.QComboBox, 'comboBox_pen')
        self.comboBox_pen.currentTextChanged.connect(self.selectPen)
        self.comboBox_pen.setCurrentText(plotterAttributes.selectedPen)

        self.button_refreshPens = self.findChild(
            QtWidgets.QPushButton, 'button_refreshPens')
        self.button_refreshPens.clicked.connect(self.refreshPens)

        self.button_pickColor = self.findChild(
            QtWidgets.QPushButton, 'button_pickColor')
        self.button_pickColor.clicked.connect(self.openColorDialog)

        self.text_color = self.findChild(
            QtWidgets.QLineEdit, 'text_color')

        self.spinBox_penAcceleration = self.findChild(
            QtWidgets.QSpinBox, 'spinBox_penAcceleration')
        self.spinBox_penAcceleration.textChanged.connect(self.penAccelChanged)

        self.spinBox_penVelocity = self.findChild(
            QtWidgets.QSpinBox, 'spinBox_penVelocity')
        self.spinBox_penVelocity.textChanged.connect(self.penVeloChanged)

        self.spinBox_penForce = self.findChild(
            QtWidgets.QSpinBox, 'spinBox_penForce')
        self.spinBox_penForce.textChanged.connect(self.penForceChanged)

        self.doubleSpinBox_penThickness = self.findChild(
            QtWidgets.QDoubleSpinBox, 'doubleSpinBox_penThickness')
        self.doubleSpinBox_penThickness.textChanged.connect(self.penThickChanged)

        #if plotterAttributes.penConfigDone == False:
        #    self.setupPens()
        #    plotterAttributes.penConfigDone = True
        #else:
        #    self.selectPen()
        self.selectPen()
        
        # Add the pens to the comboBox
        self.comboBox_pen.clear()
        plotterAttributes.penKeyList = list(plotterAttributes.penConfig.keys())
        self.comboBox_pen.addItems(plotterAttributes.penKeyList)

        # Mask disabled pens
        for pos, key in enumerate(plotterAttributes.penKeyList):
            self.comboBox_pen.model().item(pos).setEnabled(plotterAttributes.penConfig[key]['enabled'])

    # Functions

    ## Spinbox value change handling
    def penAccelChanged(self):
        plotterAttributes.penConfig[plotterAttributes.selectedPen]['acceleration'] = self.spinBox_penAcceleration.value()

    def penVeloChanged(self):
        plotterAttributes.penConfig[plotterAttributes.selectedPen]['velocity'] = self.spinBox_penVelocity.value()

    def penForceChanged(self):
        plotterAttributes.penConfig[plotterAttributes.selectedPen]['force'] = self.spinBox_penForce.value()

    def penThickChanged(self):
        plotterAttributes.penConfig[plotterAttributes.selectedPen]['thickness'] = self.doubleSpinBox_penThickness.value()

    ## Other window functions
    def selectPen(self):
        '''
        Change the values in the menu to the values within the penConfig
        dictionary
        '''
        # Get currently selected pen string value
        if self.comboBox_pen.currentText() != '':
            plotterAttributes.selectedPen = self.comboBox_pen.currentText()
            #plotterAttributes.penConfig[plotterAttributes.selectedPen]['penNumber'] = self.comboBox_pen.currentIndex() + 1
        else:
            pass

        self.changeColor()

        # Set the spinBox values
        self.spinBox_penAcceleration.setValue(plotterAttributes.penConfig[plotterAttributes.selectedPen]['acceleration'])
        self.spinBox_penVelocity.setValue(plotterAttributes.penConfig[plotterAttributes.selectedPen]['velocity'])
        self.spinBox_penForce.setValue(plotterAttributes.penConfig[plotterAttributes.selectedPen]['force'])
        self.doubleSpinBox_penThickness.setValue(plotterAttributes.penConfig[plotterAttributes.selectedPen]['thickness'])

    def refreshPens(self):
        self.setupPens()
        # Add the pens to the comboBox
        self.comboBox_pen.clear()
        plotterAttributes.penKeyList = list(plotterAttributes.penConfig.keys())
        self.comboBox_pen.addItems(plotterAttributes.penKeyList)

        # Mask disabled pens
        for pos, key in enumerate(plotterAttributes.penKeyList):
            self.comboBox_pen.model().item(pos).setEnabled(plotterAttributes.penConfig[key]['enabled'])

    def changeColor(self):
        '''
        Select and apply the color to the pen in the penConfig dictionary.
        '''
        # New attempt:
        self.text_color.setStyleSheet("background-color: {}".format(plotterAttributes.penConfig[plotterAttributes.selectedPen]['color'].name()))


        # Old attempt:
        # Setup color palette stuff
        #self.colorPalette = self.text_color.palette()
        # Set the color palette to what the selected pen requires
        #self.colorPalette.setColor(self.colorPalette.base, plotterAttributes.penConfig[plotterAttributes.selectedPen]['color'])
        # Set the color of the text box
        #self.text_color.setPalette(self.colorPalette)

    def openColorDialog(self):
        colorValue = QColorDialog.getColor()

        if colorValue.isValid():
            print(colorValue)
            plotterAttributes.penConfig[plotterAttributes.selectedPen]['color'] = colorValue
            self.changeColor()
    
    def setupPens(self):

        # Determine what pens are in the plotter and the carousel type.
        penStatus = self.checkPens()

        if penStatus == 0:
            self.penDictSetup()

        elif penStatus == 1:
            print('Pen plotter does not support the OT command and is assumed to not use a carousel.\r1 Pen enabled.')
            print('penConfig dict remains default.')

        elif penStatus == 2:
            self.penDictSetup()

        elif penStatus == 3:
            print('PROBLEM -- OT penCheck missed if catches')

        else:
            print("penStatus value not in if catch!")
            print('penStatus: {}'.format(penStatus))

    def checkPens(self):
        if plotterAttributes.plotter == None:
            # TROUBLESHOOTING BYPASS
            # Bit states are all set to 1
            plotterAttributes.penMap = '11111111'

            # Making this a string to represent Pseudo would be weird to handle. 
            # I'm putting it out of range of the acceptable OT outputs (-1-3) as -2.
            plotterAttributes.carouselType = -2
            return 2
        else:

            plotterID = plotterAttributes.plotter.id

            # See if plotter supports OT command (7575A/7576A/7550A, etc.)
            if b'SP' in plotterAttributes.plotter.allowedHPGLCommands:
                plotterAttributes.plotter.write(commands.SP(0))

            reply = plotterAttributes.plotter.carousel_type

            if b'OT' in plotterAttributes.plotter.allowedHPGLCommands:

                # Ask plotter about carousel type and pen count
                replyDecoded = reply.decode('ascii').strip().split(',')

                # Store the returned carousel type
                plotterAttributes.carouselType = int(replyDecoded[0])

                # Convert the interger map value to a string of bit states
                # and store it.
                # int value converts to a simple string of bits with leading 0s
                # 41 converts to 00101001
                # First bit = 8th pen presence, last bit =  1st pen presence
                plotterAttributes.penMap = '{:08b}'.format(int(replyDecoded[1]))
                return 0
            
            # If plotter does not support OT command and does not have a carousel
            elif not b'OT' in plotterAttributes.plotter.allowedHPGLCommands and plotterID not in plotterAttributes.pseudoCarouselPlotters:
                plotterAttributes.penMap = '00000001'
                plotterAttributes.carouselType = 0
                return 1
            
            # If plotter does not support OT but has a carousel
            # TODO This probably should be an attribute of the plotter object?
            # It sets the penmap to show there is a pen in every position.
            # It is up to the operator to stock/choose pens.
            elif not b'OT' in plotterAttributes.plotter.allowedHPGLCommands and plotterID in plotterAttributes.pseudoCarouselPlotters:
                print('The {} plotter supports carousels, but not auto detection!\rAll pens set as present!'.format(plotterID))
                
                # Bit states are all set to 1
                plotterAttributes.penMap = '11111111'

                # Making this a string to represent Pseudo would be weird to handle. 
                # I'm putting it out of range of the acceptable OT outputs (-1-3) as -2.
                plotterAttributes.carouselType = -2
                return 2
            
            else:
                print('PROBLEM -- OT penCheck missed if catches')
                return 3
        
    def penDictSetup(self):
        '''
        Iterates through the pens and the carousel config to build 
        the new penConfig dictionary.
        '''

        plotterAttributes.penConfig = {}

        # Handling the pseudo carousel case
        if plotterAttributes.carouselType == -2:

            # Clear the pen config dictionary
            plotterAttributes.penConfig.clear()

            # Prep the dictionary - In this case, all the pens are marked as pen 1
            for index, number in enumerate([number + 1 for number in range(8)]):
                plotterAttributes.penConfig['Pen ' + str(number)] = {
                    'enabled':True,
                    'penNumber':number,
                    'color':plotterAttributes.defaultColors[index],
                    'acceleration':1,
                    'velocity':15,
                    'force':4,
                    'thickness':0.3,
                    'linetype':0
                }
            # Bit states don't really matter in this instance.

        elif plotterAttributes.carouselType == -1:
            print('Unknown Carousel reported from plotter!\r Pens not initialized')

        elif plotterAttributes.carouselType == 0:
            print('No carousel, one pen only.')

        elif plotterAttributes.carouselType > 0:
            print('Setup carousel')

            # Clear the pen config dictionary
            plotterAttributes.penConfig.clear()

            # Prep the dictionary
            for index, number in enumerate([number + 1 for number in range(8)]):
                plotterAttributes.penConfig['Pen ' + str(number)] = {
                    'enabled':True,
                    'penNumber':number,
                    'color':plotterAttributes.defaultColors[index],
                    'acceleration':1,
                    'velocity':15,
                    'force':4,
                    'thickness':0.3,
                    'linetype':0
                }

            for bitState, penKey in zip(plotterAttributes.penMap, list(plotterAttributes.penConfig.keys())[::-1]):

                if bitState == '1':
                    plotterAttributes.penConfig[penKey]['enabled'] = True
                elif bitState == '0':
                    plotterAttributes.penConfig[penKey]['enabled'] = False
                    #plotterAttributes.penConfig.pop(penKey)
                else:
                    print('Index error! Too many bitstates parsed!!')
                    print('penMap: {}'.format(plotterAttributes.penMap))
                    print('bitState: {}'.format(bitState))

        else:
            print('Plotter carousel value missed in penSetup if catch!')
            
class multiPlotModel(QAbstractListModel):

    def __init__(self, *args, elements=None, **kwargs):
        super(multiPlotModel, self).__init__(*args, **kwargs)
        self.elements = elements or []

    def data(self, index, role):
            
            # Data Structure:
            # (status, type, name, info)
            # elementStatus - bool - element completed?
            # elementType - str - the type of the element
            # elementName - str - the name of the element
            # info - dictIndex - entry containing step info

        if role == Qt.ItemDataRole.BackgroundRole:

            elementStatus, _, _, _ = self.elements[index.row()]

            if elementStatus:
                return QColor('green')
            elif elementStatus:
                return QColor('white')

        if role == Qt.ItemDataRole.DisplayRole:

            _, elementType, elementName, _ = self.elements[index.row()]
            return elementType + ', ' + elementName
        
        if role == Qt.ItemDataRole.UserRole:

            _, _, _, elementInfo = self.elements[index.row()]
            return elementInfo
        
    def rowCount(self, index=0):
        return len(self.elements)
        
class addHPGLWindow(QtWidgets.QDialog):

    hpgl_fileLocation = None

    def __init__(self):
        super(addHPGLWindow, self).__init__()
        uic.loadUi('windows/addHPGLElement.ui', self)
        self.show()

        # Setup local pen dictionary
        self.localPenConfig = deepcopy(plotterAttributes.penConfig)
        self.selectedPen = deepcopy(plotterAttributes.selectedPen)
        print('localPenConfig: {}'.format(self.localPenConfig))

        # Setup return element variable
        self.hpglString_chiplotle = None
        self.element = None

        # Add escape method
        #self.accepted.connect(self.returnInfo())
        self.buttonBox_okCancel.accepted.connect(self.returnInfo)
        self.buttonBox_okCancel.rejected.connect(self.reject)

        # Setup window elements
        self.button_fileBrowse.clicked.connect(self.importHPGL)
        self.text_fileBrowse.setText('No File Selected')

        self.comboBox_pen.currentTextChanged.connect(self.selectPen)
        self.comboBox_pen.setCurrentText(self.selectedPen)

        self.checkBox_penOverride.setChecked(False)
        self.checkBox_penOverride.stateChanged.connect(self.penOverride)

        # Setup pen selection
        self.comboBox_pen.currentTextChanged.connect(self.selectPen)
        self.comboBox_pen.setCurrentText(self.selectedPen)

        self.button_pickColor.clicked.connect(self.openColorDialog)
        self.button_pickColor.setDisabled(True)

        # Set the spinBox values and initially disable them
        self.spinBox_penAcceleration.setValue(self.localPenConfig[self.selectedPen]['acceleration'])
        self.spinBox_penAcceleration.setDisabled(True)
        self.spinBox_penAcceleration.textChanged.connect(self.penAccelChanged)

        self.spinBox_penVelocity.setValue(self.localPenConfig[self.selectedPen]['velocity'])
        self.spinBox_penVelocity.setDisabled(True)
        self.spinBox_penVelocity.textChanged.connect(self.penVeloChanged)

        self.spinBox_penForce.setValue(self.localPenConfig[self.selectedPen]['force'])
        self.spinBox_penForce.setDisabled(True)
        self.spinBox_penForce.textChanged.connect(self.penForceChanged)

        self.doubleSpinBox_penThickness.setValue(self.localPenConfig[self.selectedPen]['thickness'])
        self.doubleSpinBox_penThickness.setDisabled(True)
        self.doubleSpinBox_penThickness.textChanged.connect(self.penThickChanged)

        if self.comboBox_pen.currentText() != '':
            self.selectedPen = self.comboBox_pen.currentText()
        else:
            pass

        self.selectPen()

        # Add the pens to the comboBox
        self.comboBox_pen.clear()
        self.penKeyList = list(self.localPenConfig.keys())
        self.comboBox_pen.addItems(self.penKeyList)
        
        # Mask disabled pens
        for pos, key in enumerate(self.penKeyList):
            self.comboBox_pen.model().item(pos).setEnabled(self.localPenConfig[key]['enabled'])

    ## Spinbox value change handling
    def penAccelChanged(self):
        self.localPenConfig[self.selectedPen]['acceleration'] = self.spinBox_penAcceleration.value()

    def penVeloChanged(self):
        self.localPenConfig[self.selectedPen]['velocity'] = self.spinBox_penVelocity.value()

    def penForceChanged(self):
        self.localPenConfig[self.selectedPen]['force'] = self.spinBox_penForce.value()

    def penThickChanged(self):
        self.localPenConfig[self.selectedPen]['thickness'] = self.doubleSpinBox_penThickness.value()

    def selectPen(self):
        '''
        Change the values in the menu to the values within the local dictionary
        '''
        # Get currently selected pen string value
        if self.comboBox_pen.currentText() != '':
            self.selectedPen = self.comboBox_pen.currentText()
            #self.localPenConfig[self.selectedPen]['penNumber'] = self.comboBox_pen.currentIndex() + 1
        else:
            pass

        self.changeColor()

        # Set the spinBox values
        self.spinBox_penAcceleration.setValue(self.localPenConfig[self.selectedPen]['acceleration'])
        self.spinBox_penVelocity.setValue(self.localPenConfig[self.selectedPen]['velocity'])
        self.spinBox_penForce.setValue(self.localPenConfig[self.selectedPen]['force'])
        self.doubleSpinBox_penThickness.setValue(self.localPenConfig[self.selectedPen]['thickness'])

    def openColorDialog(self):
        colorValue = QColorDialog.getColor()

        if colorValue.isValid():
            print(colorValue)
            self.localPenConfig[self.selectedPen]['color'] = colorValue
            self.changeColor()

    def changeColor(self):
        '''penConfig
        Select and apply the color to the pen in the localPenConfig dictionary.
        '''
        # New attempt:
        self.text_color.setStyleSheet("background-color: {}".format(self.localPenConfig[self.selectedPen]['color'].name()))

    def importHPGL(self):
        self.hpgl_fileLocation = QFileDialog.getOpenFileName(self, 'Open file')[0]
        print(self.hpgl_fileLocation)
        
        if self.hpgl_fileLocation != None and os.path.splitext(self.hpgl_fileLocation)[1] == '.hpgl':


            self.hpglString_chiplotle = import_hpgl_file(self.hpgl_fileLocation)
            print('HPGL Command String length: ' + str(len(self.hpglString_chiplotle)))
            self.text_fileBrowse.setText('HPGL File Selected: {}'.format(os.path.split(self.hpgl_fileLocation)[1]))

            # TODO Left in place for the eventual PySerial port.    
            #if plotterAttributes.serialBackend == 'Chiplotle':
            #    self.hpglString_chiplotle = import_hpgl_file(self.hpgl_fileLocation)
            #    print('HPGL Command String length: ' + str(len(self.hpglString_chiplotle)))
            #    self.text_fileBrowse.setText('HPGL File Selected: {}'.format(os.path.split(self.hpgl_fileLocation)[1]))

        elif self.hpgl_fileLocation == None or os.path.splitext(self.hpgl_fileLocation)[1] != '.hpgl':
            self.text_fileBrowse.setText('Invalid HPGL file selected!')


    def changeFileName(self):
        try:
            self.label_fileName.setText(os.path.split(self.hpgl_fileLocation)[1])
        except:
            print(self.hpgl_fileLocation)
            self.label_fileName.setText('None')

    def penOverride(self):
        if not self.checkBox_penOverride.isChecked():
            self.button_pickColor.setDisabled(True)
            self.spinBox_penAcceleration.setDisabled(True)
            self.spinBox_penVelocity.setDisabled(True)
            self.spinBox_penForce.setDisabled(True)
            self.doubleSpinBox_penThickness.setDisabled(True)
            self.localPenConfig = deepcopy(plotterAttributes.penConfig)
            self.selectPen()
        
        if self.checkBox_penOverride.isChecked():
            self.button_pickColor.setDisabled(False)
            self.spinBox_penAcceleration.setDisabled(False)
            self.spinBox_penVelocity.setDisabled(False)
            self.spinBox_penForce.setDisabled(False)
            self.doubleSpinBox_penThickness.setDisabled(False)
            

    def returnInfo(self):

        if self.hpglString_chiplotle == None:
            print('Rejected!')
            self.reject()

        else:
            info = {
                'HPGL Plot':{
                    'file': self.hpgl_fileLocation,
                    'chiplotleHPGL':self.hpglString_chiplotle,
                    'penConfig':{
                        'enabled':True,
                        'penNumber':self.localPenConfig[self.selectedPen]['penNumber'],
                        'color':self.localPenConfig[self.selectedPen]['color'],
                        'acceleration':self.localPenConfig[self.selectedPen]['acceleration'],
                        'velocity':self.localPenConfig[self.selectedPen]['velocity'],
                        'force':self.localPenConfig[self.selectedPen]['force'],
                        'thickness':self.localPenConfig[self.selectedPen]['thickness'],
                        'linetype':self.localPenConfig[self.selectedPen]['linetype']
                    }
                }
            }
            
            self.element = (False, 'HPGL Plot', os.path.split(self.hpgl_fileLocation)[1], info)
            print('Accpeted!')
            self.accept()

class addWaitWindow(QtWidgets.QDialog):

    def __init__(self):
        super(addWaitWindow, self).__init__()
        uic.loadUi('windows/addWaitElement.ui', self)
        self.show()
        
        self.waitTime = plotterAttributes.elementTypes['Wait']['waitTime']

        # Add escape method
        self.buttonBox_okCancel.accepted.connect(self.returnInfo)
        self.buttonBox_okCancel.rejected.connect(self.reject)

        self.doubleSpinBox_waitTime.textChanged.connect(self.setWaitTime)

    def setWaitTime(self):
        self.waitTime = self.doubleSpinBox_waitTime.value()

    def returnInfo(self):
        self.element = (False,
                        'Wait',
                        '{} Seconds'.format(self.waitTime),
                        {'Wait':{
                            'waitTime':self.waitTime}
                        })
        print('Accpeted!')
        self.accept()

class addPauseWindow(QtWidgets.QDialog):

    def __init__(self):
        super(addPauseWindow, self).__init__()
        uic.loadUi('windows/addPauseElement.ui', self)
        self.show()

        self.message = plotterAttributes.elementTypes['Pause']['message']
        self.parkPen = plotterAttributes.elementTypes['Pause']['parkPen']

        # Add escape method
        self.buttonBox_okCancel.accepted.connect(self.returnInfo)
        self.buttonBox_okCancel.rejected.connect(self.reject)

        self.lineEdit_message.setText(self.message)
        self.checkBox_parkPen.setChecked(self.parkPen)

    def returnInfo(self):
        self.element = (False,
                        'Pause',
                        'Pen Park: {}'.format(self.parkPen),
                        {'Pause':
                         {'message': self.lineEdit_message.text(),
                         'parkPen': self.checkBox_parkPen.isChecked()}
                         })
        print('Accpeted!')
        self.accept()

class pauseWindow(QtWidgets.QDialog):

    def __init__(self):
        super(pauseWindow, self).__init__()
        uic.loadUi('windows/plotPaused.ui', self)
        self.show()

        self.message = plotterAttributes.elementTypes['Pause']['message']

        self.lineEdit_message = self.findChild(
            QtWidgets.QLineEdit, 'lineEdit_message')
        self.lineEdit_message.setText(self.message)

        self.buttonBox_okCancel.accepted.connect(self.returnInfoAccept)
        self.buttonBox_okCancel.rejected.connect(self.returnInfoReject)

    def returnInfoAccept(self):
        #self.returnResult = True
        self.accept()

    def returnInfoReject(self):
        #self.returnResult = False
        self.reject()

class addPageFeedWindow(QtWidgets.QDialog):

    def __init__(self):
        super(addPageFeedWindow, self).__init__()
        uic.loadUi('windows/addPageFeedElement.ui', self)
        self.show()

        self.message = plotterAttributes.elementTypes['Page Feed']['message']

        # Add escape method
        self.buttonBox_okCancel.accepted.connect(self.returnInfo)
        self.buttonBox_okCancel.rejected.connect(self.reject)

        self.label_message.setText(self.message)

    def returnInfo(self):
        self.element = (False,
                        'Page Feed',
                        '☞',
                        {'Page Feed':''})
        print('Accpeted!')
        self.accept()

class addRepeatWindow(QtWidgets.QDialog):

    def __init__(self):
        super(addRepeatWindow, self).__init__()
        uic.loadUi('windows/addRepeatElement.ui', self)
        self.show()

        self.message = plotterAttributes.elementTypes['Repeat']['message']
        self.repeatCount = plotterAttributes.elementTypes['Repeat']['count']
        self.remaining = plotterAttributes.elementTypes['Repeat']['remaining']

        # Add escape method
        self.buttonBox_okCancel.accepted.connect(self.returnInfo)
        self.buttonBox_okCancel.rejected.connect(self.reject)

        self.label_message.setText(self.message)

        self.spinBox_count.setValue(self.repeatCount)
        self.spinBox_count.textChanged.connect(self.updateCount)

    def updateCount(self):
        self.repeatCount = self.spinBox_count.value()
        self.remaining = self.spinBox_count.value()

    def returnInfo(self):
        self.element = (False,
                        'Repeat',
                        '{0}/{1} Plots Remain'.format(self.remaining, self.repeatCount),
                        {'Repeat':
                            {'count':self.repeatCount,
                            'remaining':self.remaining}
                            })
        print('Accpeted!')
        self.accept()

# TODO WIP
class plotThread(QObject):

    finished = pyqtSignal()

    def run(self, multiPlotElement, elementIndex):

        penConfigs = multiPlotElement[3]['HPGL Plot']['penConfig']
        plotInfo = multiPlotElement[3]['HPGL Plot']['chiplotleHPGL']

        # Pen setup
        ## Get the pen info and make into list of chiplotle
        ## HPGL objects.
        setupCommands = [
            commands.SP(penConfigs['penNumber']),
            commands.VS(penConfigs['velocity']),
            commands.AS(penConfigs['acceleration']),
            commands.FS(penConfigs['force']),
        ]

        ## Iterate through the setup commands, writing to plotter
        for command in setupCommands:
            plotterAttributes.plotter.write(command)
            time.sleep(1)

        # Plot setup
        plotterAttributes.plotter.write(plotInfo)
        self.elementModel.elements[elementIndex.row()].data[0] = True

        # Exit thread
        self.finished.emit()


