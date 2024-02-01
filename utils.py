'''
Copyright 2024   Gi Tae Cho

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
from enum import IntEnum, Enum
from log import Log, printColorId, MsgLvl

# from typing import Union, Tuple



class Size (IntEnum):
    ''' Inherited IntEnum to make variables to read-only.
        If you want to dynamically modify any one in run-time,
        get rid of 'IntEnum' above and uncomment following __init__. '''
    # def __init__ (self):
    #     pass
    locationIdXIncrementStep = 2
    locationIdYIncrementStep = 1
    locationIdYSlopIncrementStep = 1
    locationIdYVerticalIncrementStep = 2

    trackSegmentHeightIdXIncrementStep = 1
    trackSegmentHeightIdYIncrementStep = 1

    # 2 blocks in the grid.
    trackSegmentLength  = 2
    defaultTrainLength  = trackSegmentLength
    longTrainLength     = defaultTrainLength * 2
    max_distance_btw_junction_and_sig = 3 * locationIdXIncrementStep

    # this is the time taken from entering a new track segment to completely leaving it.
    travelTimePerTrackSegment = 5   
    # whenever the train moves, this amount time will elapse.
    moveTimeInEachCycle = 1         

    numTrackGridX = 21
    numTrackGridY = 10
    numPixelGridStartX = 50
    numPixelGridStartY = 40
    numPixelPerGridX   = 50
    numPixelPerGridY   = 60
    numPixelPerGridSlop= 80
    numPixelPerTrackSegment = numPixelPerGridX * 2
    numPixelXPerMoveCount = int((numPixelPerGridX*2)/travelTimePerTrackSegment)
    numPixelYPerMoveCount = int(numPixelPerGridY/travelTimePerTrackSegment)

    numPixelJunctionSwWidth = numPixelPerGridX * 2
    numPixelJunctionSwHeight = numPixelPerGridY * 3
    numPixelTsHeight   = 38
    canvasWidth = 1191 #1200 #1181
    canvasHeight = 681 #691 #681

    trackSegHPosAdj = 15
    trackSegUpPosAdj = 73
    sigPosYAdj = 45
    sigPosXAdj = -28
    trainPosAdj = 30

    trainHeightPixel = 99
    trainLengthPixel = 38


class ComponentId(Enum):
    ID_TRACK_SEG = 1
    ID_SIG       = 2
    ID_JUNCTION  = 3
    ID_TRAIN     = 4
    ID_UNKNOWN   = 5

class TrackSegLayout(IntEnum):
    '''
    it is used to indicate the orientation of the track segment,
    especially the right end compared to the left end of the segment.
    '''
    #TERMINATOR = -1
    HORIZONTAL = 0      # Track segment layed horizontally.                         DO NOT CHANGE the value.
    UP = 1              # A track segment layed upward, especially the right end.   DO NOT CHANGE the value.
    DOWN = 2            # A track segment layed downward, especially the right end. DO NOT CHANGE the value.
    VERTICAL = 3        # Track segment layed vertically
    LEFT = 4            # to indicate the left end of the track segment.
    RIGHT = 5           # to indicate the right end of the track segment.
    BOTH_LEFT_RIGHT = 6 # to indicate both left and right end of the track segment.

# it is the state of the signal light
# Do not change the value.
class Light(IntEnum):    
    RED = 0
    GREEN = 1
    GREEN_RED_ON = 2
    OFF = 3

# it is used to indicate the state of a train
class TrainState(Enum):
    PARKED_STATE = 0    # the train won't move until next simulation starts.
    STOP_STATE = 1
    MOVE_STATE = 2
    
class EditorMode(Enum):
    EDIT_MD = 0
    TRACK_SEG_EDIT_MD = 1
    SIGNAL_EDIT_MD = 2
    TRAIN_EDIT_MD = 3


# control state to be used in Control object
class ControlState(Enum):
    IDLE = 0
    ACTIVE = 1
    WAIT = 2


class FeatureId(IntEnum):
    FID_SIM_EDITOR = 1
    FID_SIM    = 2
    FID_UNKNOWN = 0xFF


class Result(IntEnum):
    OK = 0
    FAIL = 1
    EXCEPTION = 2
    WARNING = 3
    EXIT_REQUEST  = 9
    END_SIM  = 10
    NO_RESULT_YET   = 0xF0    
    JC_SW_ARROW_HIDE_REQ_RECEIVED = 0xFF

    ERR_NEED_CONFIRM_FIRST = -10
    ERR_NO_MATCH_FOUND = -100
    UNKNOWN__ERR = -200

class Param(IntEnum):
    JC_SW_ARROW_HIDDEN = -1


# a class to generate and maintain unique id for each object.
class Id:
    lastId = 0
    
    def __init__(self):
        Id.lastId += 1
        self.id = Id.lastId        # unique id of an object.


class Table:
    def __init__(self, row_index, col_index):
        self.rIx = row_index
        self.cIx = col_index
class JunctionSwitchDevice:
    '''
    === Prerequisite ===
        Following list of tables must be populated before this method is called.
        - The track segment list tsList.
        - The junction list jcList.
        - Train list trainList and arrival time table.
        - Junction switching table
    '''
    def __init__(self, junctionIx, train, signal, segment):
        self.trainId = train.id
        self.time = train.arrivalTimeTable[junctionIx]        
        # it is used while the time is being revised.
        self.timeRev = self.time

        self.train = train
        self.signal = signal
        self.segment = segment               


        


class SimControl:
    '''
    This class is used to be referred as a control signal of the simulation.
    Moved to this file to avoid inter referencing issues.
    '''
    # All components will get started as soon as it turned to True.
    @classmethod
    @property
    def bSimStarted(cls) -> bool:
        return  cls.__bSimStarted
    __bSimStarted = False

    # the signals heavily rely on this clock.
    # when ever move cycle comes, it is increased by
    # given default number 'moveTimeInEachCycle'
    @classmethod
    @property
    def controlClock(cls) -> int:
        return  cls.__controlClock
    __controlClock = 0

    def __init__(self):
        pass

    def run(self) -> int:
        if SimControl.__bSimStarted == True :
            SimControl.__controlClock += Size.moveTimeInEachCycle
            Log.print(f" * {SimControl.__controlClock}", 1)

        return SimControl.__controlClock

class Error:
    @staticmethod
    def setEmergencyTrafficStop(msg="", id=0):
        '''
        It is to stop all traffic in case there is any critical system error.
        '''
        pass



class Util:

    bAlphaNumCoordinate = True

    def __init__(self):
        pass

    #####
    @classmethod
    def GetCfgValue(cls, key:str, fIx:int = 1) -> str:
        
        r = ""
        try:
            if fIx == 1:
                f = open("sim.cfg", "r")            
            else:
                return r
        except Exception:
            Log.PrintBNR('\t', 1, bForced=True)
            if fIx == 1:
                Log.PrintC("'sim.cfg' file not found !!",printColorId.WHITE_RED, bForced=True)
            #print("Exception: ", str(err))
            return r
        ln = f.readline()
            
        while len(ln) > 0:                            
            cfg = ln.split("::")
            if len(cfg) > 1:
                if cfg[0] == key:
                    r = cfg[1]
                    r = r.replace("\n", "")  # added .replace(...) to get rid of carriage return
                    r = r.replace(" ", "")   # added .replace(...) to get rid of white spaces
                    break
            ln = f.readline()
        
        f.close()
        return r    
     


    @classmethod  
    def convertCoordinateFormat(cls, x, y, head="(", tail=")") -> str:
        
        if cls.bAlphaNumCoordinate == True:
            x += 0x60

            r = f"{head}{chr(x)}{y}{tail}"
        else:
            r = f"{head}{x}, {y}{tail}"
        
        return r



        
    @classmethod
    def PrintEditorCommandHelp(cls):
        print("\n****[ Editor Command  ]**************************************")
        print("\t** the list of available commands and for track editor **")
        print("       COMMAND           FUNCTION")
        print(    "\t r  or  return     # return to home menu.")
        print(    "\t tr                # add a Train. Once typed, you need to provide coordinates.\n \
                   \t          Enter the grid coordinate at which the right edge of the train is aligned\n \
                   \t          followed by another coordination for train destination.\n \
                   \t          e.g. 'a1 b20'. You can see the coordinate like a cell in the Excel, but\n \
                   \t          consider it as a grid rather than cell. Each crossed line as a coordinate.")
        print(    "\t ts                # add a Track Segment.\n \
                   \t          enter the grid coordinate and the orientation of the right end of the track segment.\n\
                   \t          e.g. 'b2 u' where 'b2' is the coordinate and 'u' is the orientation for 'up' direction.\n\
                   \t          Orientation: 'u' for up,  'd' for down,  'h' for horizontal.")        
        print(    "\t sg                # add a Signal.\n \
                   \t          enter the grid coordinate at which the signal is placed.\n\
                   \t          e.g. 'a3' is the coordinate like in an excel cell coordinate, but\n\
                   \t          see the cell as a grid and each line for a coordinate.")    
        print(    "\t -ts               # delete a Track Segment. Once typed, you need to provide coordinate and its orientation.")
        print(    "\t -tr               # delete a Train. Once typed, you need to provide coordinate.")
        print(    "\t -sg               # delete a Signal. Once typed, you need to provide coordinate.")
        print(    "\t lts               # display added track segments.")
        print(    "\t lsg               # display added signal components.")
        print(    "\t ltr               # display train components.")
        print(    "\t la                # display all components.")
        print(    "\t q                 # exit the editor mode and return to main menu.") 
        print(    "\t -e                # terminate simulator.") 


    #####
    @classmethod
    def PrintHelp(cls):
        cls.PrintInitMsgForConsoleMenu()
        cls.PrintConsoleMenu    

    @classmethod
    def PrintEditorHelp(cls):
        cls.PrintInitMsgForTrackEditorMenu()
        cls.PrintConsoleMenu()
        cls.PrintEditorCommandHelp()

    @classmethod
    def PrintInitMsgForConsoleMenu(cls):                                                                   #
        print("\n**** simulator  [  Top Menu (Traffic Control System)  ]**************************************")    
        print("\t Type 'h' or 'help' and hit Enter key to list the available commands.") 
        print("\t Type one of '-e' and 'exit' in order to terminate this application.") 
        print(  "*********************************************************************************************\n")

    @classmethod
    def PrintInitMsgForTrackEditorMenu(cls):                                                                   #
        print("\n**** simulator  [  Traffic System Build  ]***************************************************")    
        print("\t Type 'h' or 'help' and hit Enter key to list the available commands.") 
        print("\t Type one of '-e' or 'exit' in order to terminate this application.") 
        print(  "*********************************************************************************************\n")

    #####
    @classmethod
    def PrintConsoleMenu(cls):
        print("\n****[  Top Level Menu  ]**********************************************************************")
        print("** the list of available commands.")
        print(    "\t 'save'                 # save edited component data to a file.")
        print(    "\t 'load [file name]'     # load component data and run simulation with 'sim' command.\n \
                                     e.g. 'load myFile' myFile is txt file.")
        print(    "\t 'ed'  or 'editor'      # enter into editor mode from the top menu.")
        print(    "\t 'sim' or 'start'       # start the simulation.")
        print(    "\t 'demo 0'               # start the simulation with pre-build traffic network 0.")
        print(    "\t 'demo n'               # where 'n' is one of 1, 2, 3, and 4 to get the simulation \n \
                                     started with a pre-build traffic network.")
        print(    "\t 'test 1'               # start the simulation with pre-build traffic network.")
        print(    "\t 'test 2'               # start the simulation with traffic network which will be \n \
                   \t                built by this app just before simulation gets started.")
        print("    \t '-e'  or 'exit'        # terminate this application.")
        print("    \t 'h'   or 'help'        # list the available commands and arguments.")
        print(    "\n******************************************************************************************")
        