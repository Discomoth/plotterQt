
# This file contains the plotter serial functions and stores information
# pertaining to communication with the plotter.

# TODO list:
# ♥ Improve RTS/CTS serialSend funciton
#       It includes unnecessary features that should be split out to
#       other functions
#       Add an option to ignore returned data?
# ♥ 

import serial
import serial.tools.list_ports as serialList
import platform
import time
from PyQt6.QtGui import QColor

from hpglCommands import genericCommands

class plotterAttributes():

    '''
    class plotterAttributes():

    This class is intended to store relevant data and
    provide functions for both the Chiplotle and PySerial
    control backends.
    '''

    # Plotter instance data
    plotter = None
    port = None
    model = None
    pen = 0
    penVelocity = 15
    penAccel = 1
    penForce = 4
    penThick = 0.3

    # Plotter test connect data
    plotterInfo = 'None'
    drawingLimits = 'NA'
    bufferSize = 'NA'


    # List data for interface
    portList = []
    baudRates = ['9600']

    # Control data for interface
    serialBackendIndex = 0
    serialBackend = ''
    stopFlag = False
    portIndex = 0
    baudRate = 0
    baudRateIndex = 0
    timeout = 0
    handshaking = ''
    xonxoff = False
    rtscts = False
    dsrdtr = False
    noFlowCtrl = True
    flowDelay = 0.015
    jogDistance = 100

    # Pen handling information
    carouselType = 0
    penMap = ''
    penConfig = {
        'Pen 1':{
            'enabled':True,
            'penNumber':1,
            'color':QColor.fromRgb(0x000000),
            'acceleration':1,
            'velocity':15,
            'force':2,
            'thickness':0.3,
            'linetype':0
        }
    }

    penConfigMask = {
        'Pen 1':True
    }

    defaultColors = [
        QColor.fromRgb(0x000000),
        QColor.fromRgb(0x57e389),
        QColor.fromRgb(0xf8e45c),
        QColor.fromRgb(0xffa348),
        QColor.fromRgb(0xed333b),
        QColor.fromRgb(0xc061cb),
        QColor.fromRgb(0x62a0ea),
        QColor.fromRgb(0xb5835a),
    ]
    penConfigDone = False
    selectedPen = 'Pen 1'
    activePen = 'Pen 1'

    elementTypes = {
        'HPGL Plot':{
            'file':'',
            'chiplotleHPGL':None,
            'penConfig':penConfig[selectedPen],
        },

        'Wait':{
            'waitTime':1,
        },
        
        'Pause':{
            'message':'Paused, press OK to resume plot',
            'parkPen':False
        },

        'Page Feed':{
            'message':
                'Be warned, this command has varying effects depending' + 
                'on the plotter being used. The original intent was to '+ 
                'automate mass plotting using the HP 7550A\'s ' +
                'autofeeding mechanism.\n\nSelect OK to add the element.'
        },

        'Chime': {
            'sound':''
        },
        'Repeat':{
            'message':
                'The repeat function will reset the completed statuses' + 
                'of the previous elements and restart the sequence at' + 
                ' the beginning. ',
            'count':1,
            'remaining':1
        }
    }
    
    elementList = [x for x in elementTypes.keys()]

    # This list is to handle special plotters that have carousels but do
    # not support the OT command and auto pen detection.
    # The 7440A is the only one I am currently aware of that is like this.
    # I'm sure there are others out there.
    pseudoCarouselPlotters = [
        '7440A'
    ]


    def refreshPorts():
        '''
        Refreshes the list of active serial ports.
        '''

        plotterAttributes.portList = []
        portList_raw = serialList.comports()

        for port, description, hwid in sorted(portList_raw):
            plotterAttributes.portList.append((str(port), str(description)))

class chiplotlePlotter():

    '''
    Placeholder
    '''

class serialPlotter():

    def __init__(self):

        if platform.system() == 'Linux':
            plotterSerial.portList = []
            portList_raw = serialList.comports()

            for port, description, hwid in sorted(portList_raw):
                plotterSerial.portList.append(str(port + ', ' + description))

        elif platform.system() == 'Windows':
            print('Windows PC')
            raise NotImplementedError('This system is not ported to Windows yet!')

    def connect(self):
        try:
            # Instantiate the serial object
            self.plotterObject = serial.Serial(
                port=self.serialPort,
                baudrate=self.baudRate,
                timeout=self.timeout,
                xonxoff=self.xonxoff,
                rtscts=self.rtscts,
                dsrdtr=self.dsrdtr
                )

            self.plotterObject.write(genericCommands.OI().encode())
            
            inBufferSize = self.plotterObject.in_waiting
            self.model = self.plotterObject.read(inBufferSize)
            print('Read!', self.model)
            #self.model = self.serialSend([genericCommands.OI()], prefixCommands=[], suffixCommands=[])

        except Exception as e:
            print('Failed to connect!')
            print(e)
            raise ConnectionError("Unable to connect to the plotter")
    
    # TODO this function is old and needs to be revised to be a bit more
    # friendly to this specfic program. It is a little more 'dumb' than
    # it should be. Also I slapped a receive handler in there too. lol
    def serialSend(self, listOfCommands, prefixCommands=['IN;'], suffixCommands=['PU;', 'SP0;'], checkDelay=0.1, slowInit=True):
        '''
        listOfCommands: A list of small commands to send to the plotter.

        CAUTION! If you send commands that are too large, the plotter buffer might
        overflow. Some tell you that happened, others just do stupid stuff! 

        This is a manual RTS/CTS mechanism to take the place of the one pySerial 
        should have implemented when someone menitioned it didnt work in 2016.

        MEOW! >:3c

        Thanks to Amulek1416 for the solution.
        https://github.com/pyserial/pyserial/issues/89
        '''

        # Add the pen select command to the prefix command list.
        #prefixCommands.append('SP' + str(penSelect) + ';')

        # Add prefex commands to the beginning of the command list.
        # Added in reverse order so 'IN' ends up in the front.

        if slowInit:
            for pre in prefixCommands:
                    
                self.plotterObject.setRTS(True)

                # Check the clear to send (CTS) line and if it is in the 
                # False state, wait
                while not self.plotterObject.getCTS():
                    pass

                self.plotterObject.write(pre.encode())
                time.sleep(1)
                self.plotterObject.setRTS(False)

        elif not slowInit:
            for pre in prefixCommands[::-1]:
                listOfCommands.insert(0, pre)

        # Appending the suffix commands to the command list.
        for suf in suffixCommands:
            listOfCommands.append(suf)

        # Iterate through the list of commands, sending each to the
        # plotter over the serial port while checking and pausing if
        # the plotter HW handshaking indicates a full buffer. 
        for command in listOfCommands:

            inBuffer_size = self.plotterObject.in_waiting
            if inBuffer_size > 0:
                print(inBuffer_size)
                inBuffer = self.plotterObject.read(inBuffer_size).decode()
                print(inBuffer)

            #Set the request to send (RTS) line 'True''.
            self.plotterObject.setRTS(True)

            # Check the clear to send (CTS) line and if it is in the 
            # False state, wait
            while not self.plotterObject.getCTS():
                pass

            self.plotterObject.write(command.encode())
            time.sleep(checkDelay)
            self.plotterObject.setRTS(False)

        return inBuffer

    def manualCommand():
        """
        Allows the manual issuing of a command to the plotter.
        """


# TODO Add input buffer checking/reveiving functionality.
    def serialSend2(self, commandList, commandDelay = 0.1, stopFlag=False):
        '''
        commandList:    A list containing command strings to be sent.
        commandDelay:   The amount of time to add between transmissions.
        stopFlag:       An object with a boolean value, used to
                        interrupt a plot in progress.

        RTS/CTS functionality is not included in pySerial, so it is
        manually implemented here.

        Thanks to Amulek1416 for the solution.
        https://github.com/pyserial/pyserial/issues/89
        '''
        
        # Command transmission loop
        for command in commandList:

            if stopFlag:
                break

            # Set the RTS line high
            self.plotterObject.setRTS(True)

            while not self.plotterObject.getCTS():
                pass

            self.plotterObject.write(command.encode())
            time.sleep(commandDelay)
            self.plotterObject.setRTS(False)


class plotterJog():

    # Functions used to control the plotter using the directional keys
    # on the main window 

    # These are used to control jogging of the plotter head. Similar to
    # K40Whisperer, this will allow one to align plots manually to where
    # they desire to execute the plot 
    def home():
        plotterAttributes.plotter.goto(0,0)

    def up():
        plotterAttributes.plotter.nudge(0, plotterAttributes.jogDistance)
        print('jog up')

    def down():
        plotterAttributes.plotter.nudge(0, (plotterAttributes.jogDistance * -1))
        print('jog down')

    def left():
        plotterAttributes.plotter.nudge((plotterAttributes.jogDistance * -1), 0)
        print('jog left')

    def right():
        plotterAttributes.plotter.nudge(plotterAttributes.jogDistance, 0)
        print('jog right')

    # These are used to move the plotter head to the respective corners
    # of the object to be plotted.  
    def topLeft():
        print('move to top left of object to be plotted')

    def topRight():
        print('move to top right of object to be plotted')

    def bottomLeft():
        print('move to bottom left of object to be plotted')

    def bottomRight():
        print('move to bottom right of object to be plotted')


    # Plotter outline will move the head to outline the extremes of the
    # object to be plotted.
    def outline():
        print('outline plot')

class plotting():

    # Variables for a plotting progress bar.
    plotProgress = 0
    plotRemaining = 0

    def executePlot():
        """
        Starts the plotting process.

        Needs to have a clean exit handler and allow for reset/restart
        of a plot. 

        Allow easy integration of a progress bar. 
        """