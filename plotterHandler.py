
# This file contains the plotter serial functions and stores information
# pertaining to communication with the plotter.

import serial
import serial.tools.list_ports as serialList
import platform

class plotterSerial():

    serialPort = ''
    baudRate = 0
    timeout = 0
    handshaking = ''
    plotterModel = ''
    connectionText = ''

    portList = []

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
            plotterSerial.portList.append(str(port + ', ' + description))
