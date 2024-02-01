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
import traceback
from utils import Light, Size, TrainState
from log import Log


class Location:
    ''' This class is for the location of an object.
        The object can be one of a track segment, signal, junction switch, and train.
    === Attributes ===        
    === Private Attributes ===
        None
    === Representation invariants ===
    - 
    - 
    '''

    def __init__(self, idx, idy):
        #self.location =  Id()             # unique id of the object.
        self.idX = idx              # the column id on the track layout grid.
        self.idY = idy              # the row id on the track layout grid.
        self.x = 0                  # the x coordinate of an object, especially on the lower left end of track segment.
        self.y = 0                  # the y coordinate of an object, especially on the lower left end of track segment.

    def setCoordinate(self, x, y ):
        pass

    def getCurrentCoordinate(self):
        pass

    def getCoordinate(self, idx, idy):
        pass



class Component():
    '''
    This is a base class for track segment component, signal component, junction component and train component.
    '''
    # it is used to generate unique id
    __lastId = 0
    
    def __init__(self, posIdX=None, posIdY=None):
        #super().__init
        # unique id of the component object.
        self.id = self.newId()      # Component __init__
        self.num = None             # Component __init__
        self.valid = True           # Component __init__
        if posIdX == None or posIdY == None:
            self.location = None            
        else:
            self.location = Location(posIdX, posIdY)
            

        self.bInMoving = None       # Component __init__
        # As a junction, e.g, it is set to None only when the junction is completely free meaning no train to serve
        self.movingTrain = None     # Component __init__

        # As a junction, e.g., it is used when the 'bReverse' is False
        #   It will contain enum TrackSegLayout.
        #   It is not the orientation of the ts on which the junction locates
        #   This orientation is one of tines orientation.
        self.rOrientation= []       # Component __init__

    def newId(self) -> int:
        Component.__lastId += 1
        return Component.__lastId        # unique id of an object.
    
class TrackSegComponent(Component):
    '''
    This is a track segment component.
    Several track segments, which consist of a length of track (of arbitrary length), plus two connection points at each
    end. Each of the two connection points in a track segment can:
        - link with another track connection point directly, such that the next track segment is a continuation of the first.
        - link with another track segment in a junction, providing a fork in the track.
        - end in a terminator.
    '''
    def __init__(self, idx, idy, orientation, lConn, rConn, cmpId):
        super().__init__(idx, idy)

        if cmpId != None:
            self.id = cmpId.id
        # the class of signal objects from the simulator editor
        # is different from one it uses, so leave it as None.
        self.signal = [None, None]      # The 1st element: signal object reference for the left end of the track segment. valid object: installed, None: not installed.
                                            # The 2nd element: signal object reference for the right end of the track segment. valid object: installed, None: not installed.

        self.lConnector = lConn
        self.rConnector = rConn


        self.rOrientation = orientation # the orientation of the right end of the track segment (bottom end if it is horizontally layed).
        self.bSigOnLeftEnd = None
        self.bFork = False              # It has been added during refactoring to indicate weather this segment is a fork or not.
        self.bLeftTerminator = False    # to indicate that the left side of the track segment is a terminal.
        self.bRightTerminator = False   # to indicate that the right side of the track segment is a terminal.
        self.junction = [None, None]    # 2 Junction objects maximum.
        self.forkNeck = [None, None]    # if the track segment is tine, then it should know its neck. It is for that.
        self.forkTine = [None, None]    # it will contain two track segments which are fork's tines.
        self.forkNeckConnect = None     # TrackSegLayout. it will tell you which side of the segment is the neck of the fork.
        self.forkTineConnect = None     # TrackSegLayout, it will tell you which side of the segment is the tine of the fork.
        self.bSingleTine = False

class SignalComponent(Component):
    '''
    This is a signal device component.
    Signals, which control the flow of traffic along track segments. Signals are optionally placed at the ends of each
    track segment. Signals can have the following states:
        - Green: train traffic is allowed through.
        - Red: train traffic must stop before proceeding to the next track segment.
    '''
    def __init__(self, idx, idy, location=None, id=None):
        
        if location == None:
            super().__init__(idx, idy)
        else:
            super().__init__(None, None)
            self.location = location

        if id != None:
            self.id = id

        #self.num = 0

        self.light = Light.OFF        
        self.trackSegId = None
        self.bOnLeft = None
        # A list of signaling data (SignalDevice).
        self.signalingTable = []    # a list of SignalDevice objects
        self.sigTableIx = 0
        self.junction = None


        self.greenLightReq = [None, None, None]     # maximum 3 train object references.
        self.trCurrentTsIx = [None, None, None]     # 3 integer values maximum. To indicate current train position's index in the routing table.
        self.greenOn = [False, False, False]
        self.swReqQIx = 0
        self.bInMoving = False
        self.movingTrain = None
        self.activeJc = None

        # Maximum Table objects. it contains 3 TS (track segment) indics.
        # one is on the right left but horizontally layed TS and the 2nd
        # one is on the right right side which is horizontally layed.
        # the 3rd one is for the one which layed none horizontal orientation.
        self.tsIndex = [None, None, None]        
        self.tsRef = [None, None, None]     # 3 TrackSegment object references
        
        # Maximum 3 integer values. it contains 3 junction index. one is the 
        # nearest junctions on the left and the 2nd one on the nearest right,
        # especially among ones which were layed horizontally.
        # If the signal is installed exactly on the junction where neck and tines meet,
        # then determining whether the signal is on the right or left of junction gets
        # trickier. It is actually on opposite side of the tines but we consider
        # the junction is on the side of the tines in order not to confuse in finding 
        # right one in arranging the switching properly for coming train.
        # The 3rd one is for none horizontally layed one, but still nearest
        # one on its line.
        self.jswIndex = [None, None, None]  
        self.jswRef = [None, None, None]    # 3 Junction object references
        self.bForkPassed = False



class TrainComponent(Component):
    '''
    This is a train component.
    Trains, which are initially placed in a specific track segment, and given a direction. Trains can either be moving or
    stopped. Assume trains are one track segment long. Trains stop once they reach a terminator.
    '''
    def __init__(self, idx, idy, dstIdx, dstIdy, id=None, initLoc=None, destLoc=None):
        super().__init__(idx, idy)

        self.initialize()
        if id != None:
            self.id = id
        
        self.trainNum = 0
        
        self.state = TrainState.STOP_STATE        

        self.initLocation = initLoc
        if initLoc == None:
            self.initLocation = Location(idx,idy)
            
        self.currentLocation = Location(idx,idy)
        self.destination = destLoc
        if destLoc == None:
            self.destination = Location(dstIdx,dstIdy)
            

        # following two tables are closely linked together in term of function.
        self.routingTable = []          # A list of track segment list.
                                        # The train will move through all the track segment in the list to get to
                                        # its destination.
        self.routTblIx = 0
        self.arrivalTimeTable = []
        self.arrivalTblIx = 0
        self.nextTsToSwitchToIx = None
        self.currentSigIx = None
        self.currentJcIx = None
        self.junction = None
        # the train spend this much time to pass one track segment.
        self.travelTimePerSegment = Size.travelTimePerTrackSegment
        self.trainLength = Size.defaultTrainLength
        #self.length = 20               # 20 pixels. train length for future use.
        #self.speed = 20                # 20 pixels distance/sec. for future use.


    def initialize(self):
        self.tsIndex = 0
        self.timeLeft = 0       # time left before moving on to the text track segment.
        self.moveCount = 0
        self.bForward = True
        #self.bInit = False


class JunctionComponent(Component):
    '''
    This is a junction component.
    Junctions, which can direct train traffic only to one of the forked tracks at any given time.
    '''
    def __init__(self, fork, forkTsix, bReverse=False):

        if bReverse == False:        
            x = fork[0].rConnector[0].idX
            y = fork[0].rConnector[0].idY
        else:
            x = fork[0].lConnector[0].idX
            y = fork[0].lConnector[0].idY

        super().__init__(x, y)

        # When it set to True, it means it has only single branch to switch; no switching required.
        self.bJcDummy = False
        
        self.passPermit = [False, False, False]
        self.msgStatus = [0, 0, 0]

        # a list of 2 dimension arrays. In each 2nd dimension array,  there are 3 elements.
        # The first one in each 2nd dimension is for the train object reference.
        # The 2nd one is boolean to indicate whether the train is away from the junction or not.
        # If it is set to True, it means the train passed the junction already and too far away,
        # so no further maintenance is required.
        # The 3rd one is the index to one of value in rOrient.
        self.swReqQueue = []    # __init__
        self.swReqQIx = None    # __init__
        # It is an array of boolean. Each one marks whether the train is far away from the
        # junction. if set to True, then the junction no loner need to care about the train.
        self.bTrainAway = []    # __init__
        # it hold the switching direction for each train in the swReqQueue.
        self.switchIndex = []   # __init__

        #self.bInMoving = None
        # it is set to None only when the junction is completely free meaning no train to serve
        #self.movingTrain = None     # __init__

        # neighboring junction sets it to true to take over
        # the control of junction switch.
        # if the junction see it is true then,
        # it won't change the switch until it is cleared.
        self.bSwitchLocked = None
        # A list of track segment one of which is selected at any given time
        # to guide a train. It has been added during a code refactoring 
        # in order to make populating switchingTable easy.                   
        self.trackSeg = []
                                            
        # A list of Location object. Each location Id is the next track
        # segment location id to which a train can be guided to move.
        # It is the location of the tine, especially one that is far from the junction.
        self.nextTrackSegLocation = []

        # It is used when the 'bReverse' is False
        # It will contain enum TrackSegLayout.
        # It is not the orientation of the ts on which the junction locates
        # This orientation is one of tines orientation.
        #self.rOrientation = []

        # A junction which can be considered as a junction when it is seen by reverse direction.
        self.bReverse = bReverse
        self.reverseForkShoulder = 0
        # It is used when the 'bReverse' is True
        # It is not always same value as in the TrackSegment class.
        # It is because the far side of one of fork in the junction stand point is
        # some time right or left depending on the junction location; either forward
        # train move direction or backward.
        # So the orientation value in this array is one of tines orientation rather than a TS.
        self.leftEnd = []

        # Maximum 4 integer values. it has 4 containers but it can have maximum
        # 2 junctions's index values at any given time. The first element is for
        # the junction on the left and the 2nd one on the right, especially ones
        # on the same track. The 3rd one is one in upper track and the 4th one is
        # for the one on the lower track. It is all about junctions which are
        # connected its tine. Any other junctions are not kept in this array.
        #self.jswIndex = [None, None, None, None]    # left, right, up, down  
        self.jswRef = [None, None, None, None]      # 4 Junction object references. Only 2 are field at any given time.

        #self.sigIndex = [None, None, None]
        # Each element is a Signal object reference which requested a switching.
        # It add up the reference whenever a signal device requests switching.
        self.sigRef = [] #[None, None, None]   # a list of Signal object reference.
        # it consists of 3 TS object references. The 1st element is for the fork neck
        # the 2nd one is one of 2 tines. The 3rd element is the 2nd tine.
        self.fork = fork
        # it consists of 3 Table object. The 1st element is for the tsList
        # element index for the fork neck idex, the 2nd one is for one of two tine
        # The 3rd one is the other tine object reference.
        self.forkTsIx = forkTsix
        # it points to which direction the switch need to set.
        # it can points only one of fork tine at any given time.
        self.switchDirIx = None
        self.lastSwDirIx = None
        # it must be set to True, so that this class checks if the 
        # switch was set to its default as soon as it receives the
        # first pass request from a signal device.
        # If True, changing junction switch is in progress.
        # If False, it means the junction switch is set to position.
        # If None, it has been hidden.
        self.bWaitingDspConfirm = None      # __init__(...)



class Sif:
    '''
        Signaling Interface and shared data
    '''


    @classmethod
    @property
    def simStepInSecond(cls):
        return cls.__simStepInSecond
    @classmethod
    @property
    def simTimeOutTick(cls):
        return cls.__simTimeOutTick
    @classmethod
    @property
    def simYieldTimeTick(cls):
        return cls.__simYieldTimeTick    
    @classmethod
    @property
    def trainSpeedDelayTimeout(cls):
        return cls.__trainSpeedDelayTimeout
    

    @classmethod
    @property
    def jcNumList(cls):
        return tuple(cls.__jcNumList)

    @classmethod
    @property
    def bJcReverse(cls):
        return tuple(cls.__bJcReverse)

    @classmethod
    @property
    def jcTsROrientation(cls):
        return tuple(cls.__jcTsROrientation)
    
    # time tick based simulation
    __simStepInSecond = None          # it must be 'None' for none realtime simulation.
    __simYieldTimeTick = 1
    __simTimeOutTick = __simYieldTimeTick * 200
    
    __trainSpeedDelayTimeout = 0.01 #0.01      # in second. Increase the number to slow down the train speed.

    # realtime simulation
    # __simStepInSecond = 0.3             # each simulation step in second
    # __simTimeOutTick = 100              # simulation time out tick. Total simulation time in second = __simTimeOutTick x __simStepInSecond
    # __simYieldTimeTick = 1
    # __trainSpeedDelayTimeout = 0        # It must be 0 for the realtime simulation.

    # following arrays are populated by the Junction class
    __jcNumList  = []
    __bJcReverse = []
    __jcTsROrientation = []

    def __init__(self):
        pass

    @classmethod
    def setSimulationTimeoutStep(cls, timeoutStep):
        try:
            to = int(timeoutStep)
            cls.__simTimeOutTick = cls.__simYieldTimeTick * to
        except Exception:
            Log.printException( traceback.print_exc() )

    @classmethod
    def setTrainSpeedDelay(cls, delayStep):
        try:
            dly = int(delayStep)

            if dly > 5:
                cls.trainSpeedDelayTimeout = 0            
            elif dly == 5:
                cls.trainSpeedDelayTimeout = 0.01
            elif dly == 4:
                cls.trainSpeedDelayTimeout = 0.02
            elif dly == 3:
                cls.trainSpeedDelayTimeout = 0.03
            elif dly == 2:
                cls.trainSpeedDelayTimeout = 0.04
            elif dly == 1:
                cls.trainSpeedDelayTimeout = 0.05
            elif dly == 0:
                cls.trainSpeedDelayTimeout = 0.1

        except Exception:
            Log.printException( traceback.print_exc() )


    
    @classmethod
    def emptyJcNumList(cls):
        for i in range(len(cls.__jcNumList)):
            cls.__jcNumList.pop()

    @classmethod
    def emptyBjcReverse(cls):
        for i in range(len(cls.__bJcReverse)):
            cls.__bJcReverse.pop()

    @classmethod
    def emptyJcTsROrientation(cls):
        for i in range(len(cls.__jcTsROrientation)):
            cls.__jcTsROrientation.pop()


    @classmethod
    def appendJcNumList(cls, val):
        cls.__jcNumList.append(val)
    
    @classmethod
    def appendBjcReverse(cls, val):
        cls.__bJcReverse.append(val)

    @classmethod
    def appendJcTsROrientation(cls, val):
        cls.__jcTsROrientation.append(val)


    @classmethod
    def setReqTrainMovingFlagInJc(cls, jc, bFlag) -> bool:
        if jc.bInMoving == None:
            jc.bInMoving = bFlag
            return True
        return False

    @classmethod
    def msgSwitchingResult_dsp(cls):
        pass