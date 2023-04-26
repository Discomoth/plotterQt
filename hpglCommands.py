# This file contains functions to return properly formatted HPGL
# command strings. Just trying to make things a little easier than
# manually typing each command every time.

# The hope here is that the generic commands are not system specific. 
# It is hard to know if that is the case, asa every plotter seems to
# have its own custom instruction set. Considering these commands are 
# recognized on an HP 7440A ColorPro with no 'enhancement module' I
# assume anything with HPGL can understand these commands. 

class genericCommands():

    def IN():
        '''
        Sets some values in the plotter to their default state.
        '''
        return 'IN;'

    def DF():
        '''
        Sets all parameters in the plotter to their default state.
        '''
        return 'DF;'
    
    def OI():
        '''
        OI -Output Identification
        Commands the plotter to return its model number
        '''
        return 'OI;'

    def SP(pen):
        '''
        SP - Select Pen
        Selects the pen for the plotter to use

        pen: integer, 0-8
        0 value puts all the pens away.
        '''
        return('SP' + str(pen) + ';')

    def PU(points=[], setCoordMode = 'keep'):
        '''
        PU - Pen Up
        If no point tuples in list, pen lifts in current position

        points: list of coordinate tuples. [(X,Y)]
        Ex: [(3000, 5000), (500, 1500)]

        setCoordMode: Change coordinate mode
            Options:
                - 'abs': Absolute Mode
                - 'rel': Relitive Mode
                - 'keep': Maintain current mode
        '''
        # Return single PU command string
        if len(points) == 0:
            return('PU;')

        returnString = ''

        if setCoordMode == 'abs':
            returnString += 'PA;'

        elif setCoordMode == 'rel':
            returnString += 'PR;'
        
        # Parse the coordinate list into a string for the plotter
        returnString += 'PU '
        for point in points:
            returnString += str(point[0]) + ',' + str(point[1]) + ' '

        returnString += ';'

        return returnString

    def PD(points = [], setCoordMode = 'keep'):
        '''
        PD - Pen Down
        If no point tuples in list, pen drops in current position

        points: list of coordinate tuples. [(X,Y)]
        Ex: [(3000, 5000), (500, 1500)]

        setCoordMode: Change coordinate mode
            Options:
                - 'abs': Absolute Mode
                - 'rel': Relitive Mode
                - 'keep': Maintain current mode
        '''
        # Return single PU command string
        if len(points) == 0:
            return('PD;')

        returnString = ''

        if setCoordMode == 'abs':
            returnString += 'PA;'

        elif setCoordMode == 'rel':
            returnString += 'PR;'

        # Parse the coordinate list into a string for the plotter
        returnString += 'PD '

        for point in points:
            returnString += str(point[0]) + ',' + str(point[1]) + ' '

        returnString += ';'
        
        return returnString

    def LT(lineType=''):
        '''
        LT - Line Type
        Sets the line type for the subsequent plotted lines
        Remains for any lines plotted after the execution,
        unless IN issued or plotter reset/rebooted.

        lineType: integer(0 to 6) or empty string
            Options:
                - '': (empty string) Sets line type to solid (default)
                - 0: Dots only at the points plotted
                - 1: Dotted line between points
                - 2: Short dashed line
                - 3: Long dashed line
                - 4: Long dash, dot line
                - 5: Long dash, short dash line
                - 6: Long dash, double short dash line
        '''
        return 'LT' + str(lineType) + ';'


    def PA(pointsList):
        '''
        PA - Plot Relative
        Essentially the same as PU/PD
        Set the plotter to plot absolute coordinates.
        This setting will be assumed for all plotted coordinates
        until the plotter is sent a command stating otherwise (See PA)
        '''

        returnString = ''

        # Catch to not allow 0 len lists to be passed
        if len(pointsList) == 0:
            raise("List must not be 0 length")

        # Parse the coordinate list into a string for the plotter
        returnString += 'PA '
        for point in pointsList:
            returnString += str(point[0]) + ',' + str(point[1]) + ' '

        returnString += ';'
        
        return returnString

    def PR(points):
        '''
        PR - Plot Relative
        Essentially the same as PU/PD
        Set the plotter to plot relative coordinates.
        This setting will be assumed for all plotted coordinates
        until the plotter is sent a command stating otherwise (See PA)
        '''

        returnString = ''

        # Catch to not allow 0 len lists to be passed
        if len(points) == 0:
            raise("List must not be 0 length")

        # Parse the coordinate list into a string for the plotter
        returnString += 'PR '
        for point in points:
            returnString += str(point[0]) + ',' + str(point[1]) + ' '

        returnString += ';'
        
        return returnString
    
    def IP(self, p1x, p1y, p2x, p2y):
        '''
        IP - Input P1 and P2 Instruction
        Sets the P1x, P1y, P2x and P2y coordinates.
        Extreme limits and defaults are device dependent.
        '''
    
        return 'IP' + str(p1x) + ',' + str(p1y) + ',' + str(p2x) + ',' + str(p2y) + ';'
    
    def SC(self, xMin, xMax, yMin, yMax):
        '''
        SC - Scale Instruction
        Scales the plotter units between P1 and P2.
        '''

        return 'SC' + str(xMin) + ',' + str(xMax) + ',' + str(yMin) + ',' + str(yMax) + ';'
    

class hpgl():

    def LB(labelString, lineEndChar='', termChar=chr(3)):
        '''
        LB - Label
        Creates a text label at the current pen location

        labelString: string, text for the label.

        lineEndChar: string, character to end the line with.
            Options:
                - 'LF': Line feed (chr(10))
                - 'CR': Carriage return (chr(13))
                - 'ETX': End-of-text (chr(3), default LB term char)
                - 'SO': Shift out (chr(14))
                - 'SI': Shift in (chr(15))

        termChar: The character used to terminate the plotted 
                    characters.
                    TODO add a tieback to check against current
                    termination character in plotter class.

        '''
        lineEndChars = {
            'LF': chr(10),
            'CR': chr(13),
            'ETX': chr(3),
            'SO': chr(14),
            'SI': chr(15),
            '':''
            }

        return 'LB' + labelString + lineEndChars[lineEndChar] + termChar

    def SM():
        '''
        SM - Symbol Mode
        '''
        print("placeholder!")

    def DT():
        '''
        DT - Define label Terminator
        '''
        print("placeholder!")

    def CP():
        '''
        CP - Charater Plot cell
        Inserts a character plot cell, used for indentation and extra spacing.
        '''

    def SI():
        '''
        SI - Absolute Label Character Size
        '''

    def SR():
        '''
        SR - Relative Label Character Size
        '''

    def DI():
        '''
        DI - Absolute Label Direction
        '''

    def DR():
        '''
        DR - Relative Label Direction
        '''

    def SL():
        '''
        SL - Label Character Slant
        '''

    def CS():
        '''
        CS - Set Standard Label Character Set
        '''

    def CA():
        '''
        CA - Set Alternate Label Character Set
        '''

    def SS():
        '''
        SS - Select Standard label character set
        '''

    def SA():
        '''
        SA - Select Alternate label character set
        '''
    def UC():
        '''
        UC - User defined character
        '''