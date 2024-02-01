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
import traceback, time
from utils import Util, Id, TrainState, Size, Error, SimControl, Light, Log, TrackSegLayout
#from trainSignalingSystem import Location
from component import TrainComponent, Sif
from log import printColorId, MsgLvl
from plot import Display
#from junctionSwitch import Junction
    

class Train(TrainComponent):
    ''' This class is a virtual train which will be moving toward 
        a given destination once the simulation gets started.
    === Attributes ===        
    === Private Attributes ===
        None
    === Representation invariants ===
    - 
    - 
    '''
    @classmethod
    @property
    def trainList(cls):
        return  tuple(cls.__trList)
    

    __trList = []      # a list of Train objects
    

    def __init__(self, idx, idy, dstIdx, dstIdy, id=None, initLoc=None, destLoc=None):
        
        super().__init__(idx, idy, dstIdx, dstIdy, id, initLoc, destLoc)

        Train.__trList.append(self)    # add new Train object into the __trList.
        

    @classmethod
    def showAllTrCompInfo(cls):

        Log.print("*** Train Info (id, location, destination)", MsgLvl.DBG_MSG_COMP_TABLE)
        for tr in cls.__trList:
            ps1 = Util.convertCoordinateFormat(tr.initLocation.idX, tr.initLocation.idY)
            ps2 = Util.convertCoordinateFormat(tr.destination.idX, tr.destination.idY)
            Log.print(f"\t{tr.trainNum},\t{ps1},\t{ps2})", MsgLvl.DBG_MSG_TABLE)


    @classmethod
    def showAllRoutingTable(cls):
        Log.print("** Train Routing Table (loc-left, loc-right, forked)/signal Left or Right and their ID if available.", MsgLvl.CORE_MSG)
        for i, tr in enumerate(cls.__trList):
            ps1 = Util.convertCoordinateFormat(tr.initLocation.idX, tr.initLocation.idY)
            ps2 = Util.convertCoordinateFormat(tr.destination.idX, tr.destination.idY)

            Log.print(f"  * Train #{i+1} ID:\n\t{tr.id},\t{ps1},\t{ps2}\t{tr.bForward}", MsgLvl.CORE_MSG)
            
            for i2, ts in enumerate(tr.routingTable):
                msg = ""
                if ts.signal[0] != None:
                    msg = f"L.Sig:{ts.signal[0].num}"
                if ts.signal[1] != None:
                    msg = f"R.Sig:{ts.signal[1].num}"
                Log.print(f"\t({ts.lConnector[0].idX},{ts.lConnector[0].idY})\t\t({ts.rConnector[0].idX},{ts.rConnector[0].idY})\t{ts.bFork}\t{msg}", MsgLvl.CORE_MSG)

                
    @classmethod
    def validateRoutingTable(cls):
        try:
            for tr in cls.__trList:
                for ix, ts in enumerate(tr.routingTable):

                    if len(tr.routingTable) > ix + 1:
                        for i in range(ix+1, len(tr.routingTable)):
                            if ts.id == tr.routingTable[i].id:
                                print("\tWaring! found a duplicate route in the routing table. It has been fixed.")
                                tr.routingTable.pop(i)
        except Exception: 
            Log.printException( traceback.print_exc() )


    def isValidTrain(self) -> bool:
        b = False

        if self.initLocation.idX != 0:
            if self.initLocation.idY != 0:
                if self.destination.idX != 0:
                    if self.destination.idY != 0:
                        b = True

        return b
    
    def addDestinationId(self, idx, idy):
        self.destination.idX = idx
        self.destination.idY = idy



    def getTrackSegIdX(self, ts) -> int:
        return ts.location.idX
    
    
    def sortRoutingTable(self):
        self.routingTable.sort(key=self.getTrackSegIdX)

        if len(self.routingTable) > 0:
            if self.routingTable[0].lConnector[0].idX < self.routingTable[0].rConnector[0].idX:
                self.bForward = True
            else:
                self.bForward = False                
        else:
            self.bForward = True            

    
    def reviseRoutingTime(self, segment, time):
        try:
            ix = 0
            bFound = False
            for ix, ts in enumerate(self.routingTable):
                if segment.lConnector[0].idX == ts.lConnector[0].idX:
                    if segment.lConnector[0].idY == ts.lConnector[0].idY:
                        bFound = True
                        break

            if bFound == True:
                for i in range(ix, len(self.arrivalTimeTable)):
                    self.arrivalTimeTable[i] += time

        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() )

        
    def parkingMesage(self):
        ps1 = Util.convertCoordinateFormat(self.initLocation.idX, self.initLocation.idY)
        ps2 = Util.convertCoordinateFormat(self.destination.idX, self.destination.idY, "@(")
        Log.PrintC(f"\tTrain #{self.trainNum}, {ps1}:   \t\tARRIVED   {ps2}", printColorId.YELLOW_BLACK)


    def getNextTrackSegmentToSwitchTo(self):
        ts = None
        if self.nextTsToSwitchToIx != None:
            if self.bForward == True:
                if self.currentLocation.idX < self.routingTable[self.nextTsToSwitchToIx].location.idX:
                    ts = self.routingTable[self.nextTsToSwitchToIx]
                else:
                    self.nextTsToSwitchToIx = None
            else:
                if self.currentLocation.idX > self.routingTable[self.nextTsToSwitchToIx].location.idX:
                    ts = self.routingTable[self.nextTsToSwitchToIx]
                else:
                    self.nextTsToSwitchToIx = None


        if ts == None:
            for ix in range(self.routTblIx, len(self.routingTable)):
                # is it a junction?
                if self.routingTable[ix].forkNeckConnect != None:   # found the nearest junction.
                    # is the train moving forward direction?
                    if self.bForward == True:
                        for fTs in self.routingTable[ix].forkTine:
                            if fTs != None:
                                # check if it is a forward junction; not a reverse one.
                                if self.routingTable[ix].rConnector[0].idX == fTs.lConnector[0].idX:
                                    # it is a froward direction junction.
                                    if fTs.rConnector[0].idY == self.destination.idY:
                                        # the next to the junction is the fork tine to get on
                                        self.nextTsToSwitchToIx = ix + 1
                                        ts = fTs
                                        break

                                else: # it is a reverse junction
                                    # if it is not the same track, then the junction is no longer
                                    # the first connect junction for the train; if the tine isn't
                                    # horizontal, then there is another junction right before the tine.
                                    if fTs.lConnector[0].idY == self.currentLocation.idY:
                                        # before the junction in the forward moving train is
                                        # the fork tine to get on
                                        self.nextTsToSwitchToIx = ix - 1
                                        ts = fTs
                                        break

                        if ts == None:
                            # be aware that there are situations when there is 
                            # no destination track connected by any fork tine.
                            # Take a look at the track number 7 in net_6 image.
                            # In this case, we need to run this for loop as well.
                            for fTs in self.routingTable[ix].forkTine:
                                if fTs != None:
                                    # check if it is a forward junction; not a reverse one.
                                    if self.routingTable[ix].rConnector[0].idX == fTs.lConnector[0].idX:
                                        # it is a froward direction junction.

                                        # check if there is a fork tine which is on the same
                                        # track as current train is on
                                        if fTs.rConnector[0].idY == self.currentLocation.idY:
                                            self.nextTsToSwitchToIx = ix + 1
                                            ts = fTs
                                            break

                        if self.routingTable[ix].rConnector[0].idY == self.destination.idY:
                            self.nextTsToSwitchToIx = ix
                            ts = self.routingTable[ix]
                            break


                    else:   # the train moves reverse direction.
                        for fTs in self.routingTable[ix].forkTine:
                            if fTs != None:
                                # check if it is a forward junction; not a reverse one.
                                if self.routingTable[ix].rConnector[0].idX == fTs.lConnector[0].idX:
                                    # it is a froward direction junction.
                                    if fTs.rConnector[0].idY == self.currentLocation.idY:
                                        # before the junction in the reversely moving train is
                                        # the fork tine to get on
                                        self.nextTsToSwitchToIx = ix - 1
                                        ts = fTs
                                        break

                                else: # it is a reverse junction                                    
                                    if fTs.lConnector[0].idY == self.destination.idY:
                                        # the next to the junction in reverse direction is
                                        # the fork tine to get on
                                        self.nextTsToSwitchToIx = ix + 1
                                        ts = fTs
                                        break

                        if ts == None:
                            # be aware that there are situations when there is 
                            # no destination track connected by any fork tine.
                            # Take a look at the track number 7 in net_6 image.
                            # In this case, we need to run this for loop as well.
                            for fTs in self.routingTable[ix].forkTine:
                                if fTs != None:
                                    # check if it is a reverse junction; not a forward one.
                                    if self.routingTable[ix].rConnector[0].idX != fTs.lConnector[0].idX:
                                        # it is a reverse junction
                                        # check if there is a fork tine which is on the same
                                        # track as current train is on
                                        if fTs.lConnector[0].idY == self.currentLocation.idY:
                                            self.nextTsToSwitchToIx = ix + 1
                                            ts = fTs
                                            break

                    if ts == None:
                        Log.print(f"\tFailed to find a TS to which the train move through!\ttr ({self.trainNum})\t[tr_getNextTrackSegmentToSwitchTo]")

                    break

        return ts


    def getItMove(self):
        try:
            self.moveCount += 1
            self.state = TrainState.MOVE_STATE

            ps1 = Util.convertCoordinateFormat(self.initLocation.idX, self.initLocation.idY)
            
            locOffset = self.moveCount % Size.travelTimePerTrackSegment
            if locOffset == 0:
                ix = int(self.moveCount / Size.travelTimePerTrackSegment)
                if ix >= len(self.routingTable):
                    self.state = TrainState.PARKED_STATE
                    if ix > 0:
                        ix -=1

                self.currentLocation.idX = self.routingTable[ix].lConnector[0].idX
                self.currentLocation.idY = self.routingTable[ix].lConnector[0].idY
                #Display.updateTrainLocation(self.trainNum, self.currentLocation, 0)
                self.routTblIx += 1

                if (self.routTblIx + 1) >= len(self.routingTable):
                    self.routTblIx -= 1
                    self.state = TrainState.PARKED_STATE
                else:
                    if self.bForward == True:
                        if self.routingTable[self.routTblIx].bRightTerminator == True:
                            self.state = TrainState.PARKED_STATE
                            Log.print("\tThe terminator on the right. Parking in progress...", MsgLvl.CORE_MSG)
                    else:
                        if self.routingTable[self.routTblIx].bLeftTerminator == True:
                            self.state = TrainState.PARKED_STATE
                            Log.print("\tThe terminator on the left. Parking in progress...", MsgLvl.CORE_MSG)

                ps2 = Util.convertCoordinateFormat(self.currentLocation.idX, self.currentLocation.idY)
                Log.print(f"\tTrain #{self.trainNum}, {ps1}->{ps2}:\t\t\tGot in: {ps2}\t[tr_getItMove]", MsgLvl.CORE_MSG)    

            Display.updateTrainLocation(self.trainNum, self.currentLocation, locOffset, self.bForward, self.routingTable[self.routTblIx].rOrientation)
            Log.print(f"\tTrain #{self.trainNum}, {ps1}:\tcnt({self.moveCount})\t\t\t\t[tr_getItMove]", MsgLvl.CORE_MSG)

            if self.state == TrainState.PARKED_STATE:
                self.parkingMesage()

        except Exception: 
            Error.setEmergencyTrafficStop()
            #print("Exception: (Control.getItMove)", str(err))
            Log.printException( traceback.print_exc() )


    def run(self):
        try:
            # if SimControl.bSimStarted == True:                # debug purpose: to set a breakpoint.
            #     bSignal = False
            #     if SimControl.controlClock > 80:
            #         if self.initLocation.idX == 1 and self.initLocation.idY == 1:
            #             if self.currentLocation.idX == 5:
            #                 a = 3

                # check if it got the job done already.
                if self.state != TrainState.PARKED_STATE:
                    ln = len(self.routingTable)
                    sg = None
                    if self.bForward == True:
                        sg = self.routingTable[self.routTblIx].signal[0]
                        tmpIx = 0
                        if sg == None:
                            # this 'if' state is necessary only for forward direction trains.
                            if ln > self.routTblIx + 1:
                                if self.routingTable[self.routTblIx + 1].signal[0] == None or self.bForward == True:
                                    sg = self.routingTable[self.routTblIx].signal[1]
                                    tmpIx = 1
                    else:
                        sg = self.routingTable[self.routTblIx].signal[1]
                        tmpIx = 1
                        if sg == None:
                            sg = self.routingTable[self.routTblIx].signal[0]
                            tmpIx = 0

                    ps1 = Util.convertCoordinateFormat(self.initLocation.idX, self.initLocation.idY)
                    ps2 = Util.convertCoordinateFormat(self.currentLocation.idX, self.currentLocation.idY)

                    if sg != None:
                        # the train found the signal light on current TS (track segment).
                        # It means the next track segment in its routing table is either
                        # a junction (fork neck) or a tine unless the signal light was
                        # installed too far way from the junction.
                        # The train needs to ask for junction switching toward it is moving through.
                        self.currentSigIx = tmpIx
                        #if sg.getLightState(self) != True:    # either False or None
                        if sg.greenLightRequest(self, self.routTblIx) == True:
                            Log.print(f"\ttrain  {self.trainNum}, {ps1}->{ps2}:\tcnt({self.moveCount})\t\tGreen ({sg.num})\t[tr_run]", MsgLvl.CORE_MSG)
                            
                            self.getItMove()
                        else:
                            self.state = TrainState.STOP_STATE
                            if len(self.routingTable) > self.routTblIx + 1:
                                ts2 = self.routingTable[self.routTblIx+1]
                                Log.PrintC(f"\ttrain  {self.trainNum}, {ps1}@{ps2}:\tcnt({self.moveCount})\t\twaiting for green... ({sg.num}) <tr_getItMove>", printColorId.RED_BLACK)
                            else:
                                Log.PrintC(f"\ttrain  {self.trainNum}, {ps1}@{ps2}:\tcnt({self.moveCount})\t\twaiting for green... ({sg.num}) <tr_getItMove>", printColorId.RED_BLACK)
                            #Log.PrintC("Stopped", printColorId.RED_BLACK)
                    else:
                        self.currentSigIx = None
                        self.getItMove()


                # if Sif.trainSpeedDelayTimeout > 0:    
                #     time.sleep(Sif.trainSpeedDelayTimeout)
                #     #time.sleep(0.1)

                

        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() )
        
    
