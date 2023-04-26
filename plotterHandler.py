
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

from hpglCommands import genericCommands

class plotterSerial():

    plotterObject = None
    stopFlag = False

    serialPort = ''
    baudRate = 0
    timeout = 0
    handshaking = ''
    xonxoff = False
    rtscts = False
    dsrdtr = True
    model = 'None'
    connectionText = ''

    portList = []
    baudRates = ['9600']

    def __init__(self):

        if platform.system() == 'Linux':
            plotterSerial.portList = []
            portList_raw = serialList.comports()

            for port, description, hwid in sorted(portList_raw):
                plotterSerial.portList.append(str(port + ', ' + description))

        elif platform.system() == 'Windows':
            print('Windows PC')
            raise NotImplementedError('This system is not ported to Windows yet!')

    def refreshPorts():
        '''
        Refreshes the list of active serial ports.
        '''

        plotterSerial.portList = []
        portList_raw = serialList.comports()

        for port, description, hwid in sorted(portList_raw):
            plotterSerial.portList.append((str(port), str(description)))

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
    def up(plotterUnits):
        print('jog up')

    def down(plotterUnits):
        print('jog down')

    def left(plotterUnits):
        print('jog left')

    def right(plotterUnits):
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