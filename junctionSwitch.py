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
from plot import Display
from typing import Tuple
import traceback
from utils import Util, Id, JunctionSwitchDevice, Error, TrackSegLayout, SimControl, Size, TrainState, Table, Param, Result
from component import Location
#from train import Train
from log import Log, MsgLvl
from component import JunctionComponent


class Junction(JunctionComponent):
    ''' This class is a virtual junction switch.
    === Attributes ===        
    === Private Attributes ===
        None
    === Representation invariants ===
    - 
    - 
    '''

    @classmethod
    @property
    def jcList(cls):
        return tuple(cls.__jcList)

    # A list of Junction objects.
    __jcList = []

    def __init__(self, fork, forkTsix, bReverse=False):
        super().__init__(fork, forkTsix, bReverse)

        self.trainLoc = [None, None]
        #self.swReqQueue = [None, None, None]     # maximum 3 train object references.

        # It indicates one element in nextTrackSegLocation which has
        # all locations where the train can be guided to move through
        # this junction. This nextIndex must have one index value
        # at any given time.
        self.nextIndex = [ 0, 0, 0]        
        #self.routingTableIx = 0     # it points to a track segment in a train's routing table.
                                    # if the train passes the segment, then the junction can be switched.

        # it point to one element in switchingTable array.
        # The train which is pointed by this member variable has priority
        # over others in terms of passing-through the junction.
        self.priorityIx = 0
        # A list of junction switching data (JunctionSwitchDevice) which
        # consists of train object, signal object, and the track segment
        # to which the train is guided to move.
        self.switchingTable = [] 

        if self.addNewJunctionSwitch(bReverse) == True:
            # add new Junction object into the __jcList.
            Junction.__jcList.append(self)

    
    @classmethod
    def assignJunctionNumber(cls):
        ix = 0
        for jc in cls.__jcList:
            jc.num = ix
            ix += 1
            
    @classmethod
    def showAllJunctionTable(cls):

        Log.print("*** Junction Table Info (number, id, location, tsId, time, green, red)", MsgLvl.DBG_MSG_TABLE)
        for sg in cls.__jcList:
                sg.showJunctionTableRow(False)
    
    def showJunctionTableRow(self, bHead=True):
        if bHead == True:
            Log.print("*** Junction Table Info (number, id, location, reversedJC, sig (left, right, up/down)", MsgLvl.DBG_MSG_TABLE)
        
        ps1 = Util.convertCoordinateFormat(self.location.idX, self.location.idY)
        loc = ""
        for sg in self.sigRef:
            loc += Util.convertCoordinateFormat(sg.location.idX, sg.location.idY) + ", "
        
        Log.print(f"\t{self.num},\t{self.id},\t@{ps1},\t{self.bReverse},\tsig @{loc}", MsgLvl.DBG_MSG_TABLE)


    def addNewJunctionSwitch(self, bReverse=False) -> bool:
        bNew = True
        i = j = 0

        # fork neck
        self.fork[0].bFork = True
        self.fork[0].bReverse = bReverse

        if bReverse == False:
            if self.fork[1] != None:
                # the 1 tine           
                self.nextTrackSegLocation.append(Location(self.fork[1].rConnector[0].idX, self.fork[1].rConnector[0].idY))
                self.leftEnd.append(self.fork[1].rOrientation)
                # the 1st tine's right end orientation.
                self.rOrientation.append(self.fork[1].rOrientation)   # next one's orientation. Not the ts on which the junction locates.
                self.trackSeg.append(self.fork[1])                

            if self.fork[2] != None:
                # the 2nd tine
                self.nextTrackSegLocation.append(Location(self.fork[2].rConnector[0].idX, self.fork[2].rConnector[0].idY))
                self.leftEnd.append(self.fork[2].rOrientation)
                # the 2nd tine's right end orientation.
                self.rOrientation.append(self.fork[2].rOrientation)   # next one's orientation. Not the ts on which the junction locates.
                self.trackSeg.append(self.fork[2])


        else:
            if self.fork[1] != None:
                self.nextTrackSegLocation.append(Location(self.fork[1].lConnector[0].idX, self.fork[1].lConnector[0].idY))
            
                if self.fork[1].rOrientation == TrackSegLayout.UP:
                    self.leftEnd.append(TrackSegLayout.DOWN)
                elif self.fork[1].rOrientation == TrackSegLayout.DOWN:
                    self.leftEnd.append(TrackSegLayout.UP)
                else:
                    self.leftEnd.append(self.fork[1].rOrientation)

                # the 1st tine's right end orientation.
                self.rOrientation.append(self.fork[1].rOrientation)   # next one's orientation. Not the ts on which the junction locates.

                self.trackSeg.append(self.fork[1])

            if self.fork[2] != None:
                self.nextTrackSegLocation.append(Location(self.fork[2].lConnector[0].idX, self.fork[2].lConnector[0].idY))

                if self.fork[2].rOrientation == TrackSegLayout.UP:
                    self.leftEnd.append(TrackSegLayout.DOWN)
                elif self.fork[2].rOrientation == TrackSegLayout.DOWN:
                    self.leftEnd.append(TrackSegLayout.UP)
                else:
                    self.leftEnd.append(self.fork[2].rOrientation)

                # 2nd tine's right end orientation.
                self.rOrientation.append(self.fork[2].rOrientation)   # next one's orientation. Not the ts on which the junction locates.
                self.trackSeg.append(self.fork[2])

        
        
        
        


        if self.fork[1] != None:
            self.fork[1].updateForkTineConnect(bReverse)
            if bReverse == True:            
                self.fork[1].junction[1] = self
            else:
                self.fork[1].junction[0] = self
            
            self.fork[1].updateForkNeckToTineTs(self.fork[0], bReverse)
        
        if self.fork[2] != None:
            self.fork[2].updateForkTineConnect(bReverse)
            if bReverse == True:            
                self.fork[2].junction[1] = self
            else:
                self.fork[2].junction[0] = self

            self.fork[2].updateForkNeckToTineTs(self.fork[0], bReverse)
        

        # for the neck
        self.fork[0].updateForkTineToNeckTs(self.fork[1], self.fork[2], bReverse)
        self.fork[0].updateJunctionForkNeckTs(self, bReverse)

        if self.fork[1] == None or self.fork[2] == None:
            self.bJcDummy = True

        return True



    @classmethod
    def initialize(cls):
        if len(Junction.__jcList) > 0:
            for js in Junction.__jcList:
                del(js)


    @classmethod
    def getCurrentLocationIdX(cls, js) -> int:
        return js.location.idX
    
    @classmethod
    def organizeAndUpdateSignalData(cls):
        cls.sortJunctionSwitch()
        cls.assignJunctionNumber()
        cls.populateConnectedJunctions()
    
    @classmethod
    def sortJunctionSwitch(cls):
        #for js in Junction.__jcList:
        #    js.sort(key=Junction.getCurrentLocationIdX)

        Junction.__jcList.sort(key=cls.getCurrentLocationIdX)

    @classmethod
    def getTimeInSwitchingTable(cls, jsdata) -> int:
        return jsdata.time
    
    @classmethod
    def sortJncSwitchingTable(cls):
        '''
        It sorts the train arriver time. 
        Short time is priority, it is sorted ascending order.
        '''
        for js in Junction.__jcList:
            js.switchingTable.sort(key=cls.getTimeInSwitchingTable)
            js.priorityIx = 0


    @classmethod
    def populateJunctionTable(cls, ts_list):
        ''' It find and add junctions '''

        try:

            # a list of TS of which orientation is not horizontal.
            lupdown = []    # for TS obj ref
            lupdownIx = []  # for index to TS obj in tsList.

            for row, tsa in enumerate(ts_list):
                for col, ts in enumerate(tsa):
                    if ts.rOrientation != TrackSegLayout.HORIZONTAL:
                        lupdown.append(ts)
                        lupdownIx.append(Table(row, col))


            
            lNeckTine = []
            lNeckTineIx = []
            bReverse = []
            objIx = -1
            # finding all necks and tines to which this TS's head is connected.
            # A TS in the lupdown is the head.
            for ix, head in enumerate(lupdown):
                
                bufIx = []
                bRvs = False
                bFound = None
                objIx += 1
                for x, tsa in enumerate(ts_list):
                    for y, ts in enumerate(tsa):
                        if lupdownIx[ix].rIx == x and lupdownIx[ix].cIx == y:
                            # found these are the same TS.
                            continue

                        # head to tail match. once found that ts is the junction neck.
                        if head.lConnector[0].idX == ts.rConnector[0].idX and head.lConnector[0].idY == ts.rConnector[0].idY:
                            
                            if bFound == None:                                
                                bufIx = [Table(x,y), lupdownIx[ix], None]
                                bRvs = False
                                bFound = True
                            else:
                                bufIx[0] = Table(x, y)


                        # head to head match. once found that ts is one of 2 tines.
                        if head.lConnector[0].idX == ts.lConnector[0].idX and head.lConnector[0].idY == ts.lConnector[0].idY:
                            
                            if bFound == None:
                                bufIx = [None, lupdownIx[ix], Table(x,y)]
                                bRvs = False
                                bFound = True
                            else:
                                bufIx[2] = Table(x,y)


                # following statements is to filter out duplicate.
                # there can be duplicate when 2 tines for a fork neck are not horizontal layout.
                if bFound == True:
                    if len(lNeckTine) > 0:
                        bFound = False
                        for js in lNeckTine:
                            if js[0].id == ts_list[bufIx[0].rIx][bufIx[0].cIx].id:
                                if js[1].id == ts_list[bufIx[1].rIx][bufIx[1].cIx].id:
                                    if len(js) > 2:
                                        if js[2].id == ts_list[bufIx[2].rIx][bufIx[2].cIx].id:
                                            bFound = True
                                    else:
                                        bFound = True
                                elif len(js) > 2:
                                    if js[1].id == ts_list[bufIx[2].rIx][bufIx[2].cIx].id:                                    
                                        if js[2].id == ts_list[bufIx[1].rIx][bufIx[1].cIx].id:
                                            bFound = True
                    
                        if bFound == False:
                            if bufIx[2] != None:
                                ts = ts_list[bufIx[2].rIx][bufIx[2].cIx]
                            else:
                                ts = None
                            lNeckTine.append([ts_list[bufIx[0].rIx][bufIx[0].cIx], ts_list[bufIx[1].rIx][bufIx[1].cIx], ts])
                            lNeckTineIx.append(bufIx)
                            bReverse.append(bRvs)
                        else:
                            objIx -= 1  # to restore the index value.
                    else:
                        if bufIx[2] != None:
                            ts = ts_list[bufIx[2].rIx][bufIx[2].cIx]
                        else:
                            ts = None
                        lNeckTine.append([ts_list[bufIx[0].rIx][bufIx[0].cIx], ts_list[bufIx[1].rIx][bufIx[1].cIx], ts])
                        lNeckTineIx.append(bufIx)
                        bReverse.append(bRvs)



            # finding all necks and tines to which this TS's tail is connected.
            # A TS in the lupdown is the tail.
            for ix, tail in enumerate(lupdown):
                bufIx = []
                bRvs = False

                bFound = None
                objIx += 1
                for x, tsa in enumerate(ts_list):
                    for y, ts in enumerate(tsa):
                        if lupdownIx[ix].rIx == x and lupdownIx[ix].cIx == y:
                            # found these are the same TS.
                            continue

                        # tail to head match. once found that ts is the junction neck.
                        if tail.rConnector[0].idX == ts.lConnector[0].idX and tail.rConnector[0].idY == ts.lConnector[0].idY:
                            
                            if bFound == None:
                                bufIx = [Table(x,y), lupdownIx[ix], None]
                                bRvs = True
                                bFound = True
                            else:
                                bufIx[0] = Table(x, y)


                        # tail to tail match. once found that ts is one of 2 tines.
                        if tail.rConnector[0].idX == ts.rConnector[0].idX and tail.rConnector[0].idY == ts.rConnector[0].idY:
                            if bFound == None:
                                bufIx = [None, lupdownIx[ix], Table(x,y)]
                                bRvs = True
                                bFound = True
                            else:
                                bufIx[2] = Table(x,y)



                # following statements is to filter out duplicate.
                # there can be duplicate when 2 tines for a fork neck are not horizontal layout.
                if bFound == True:
                    if len(lNeckTine) > 0:
                        bFound = False
                        for js in lNeckTine:
                            if js[0].id == ts_list[bufIx[0].rIx][bufIx[0].cIx].id:
                                if js[1].id == ts_list[bufIx[1].rIx][bufIx[1].cIx].id:
                                    if len(js) > 2:
                                        if js[2].id == ts_list[bufIx[2].rIx][bufIx[2].cIx].id:
                                            bFound = True
                                    else:
                                        bFound = True
                                elif len(js) > 2:
                                    if bufIx[2] != None:
                                        if js[1].id == ts_list[bufIx[2].rIx][bufIx[2].cIx].id:                                    
                                            if js[2].id == ts_list[bufIx[1].rIx][bufIx[1].cIx].id:
                                                bFound = True


                    
                        if bFound == False:
                            if bufIx[2] != None:
                                ts = ts_list[bufIx[2].rIx][bufIx[2].cIx]
                            else:
                                ts = None
                            lNeckTine.append([ts_list[bufIx[0].rIx][bufIx[0].cIx], ts_list[bufIx[1].rIx][bufIx[1].cIx], ts])
                            lNeckTineIx.append(bufIx)
                            bReverse.append(bRvs)
                        else:
                            objIx -= 1  # to restore the index value.
                    else:
                        if bufIx[2] != None:
                            ts = ts_list[bufIx[2].rIx][bufIx[2].cIx]
                        else:
                            ts = None
                        lNeckTine.append([ts_list[bufIx[0].rIx][bufIx[0].cIx], ts_list[bufIx[1].rIx][bufIx[1].cIx], ts])
                        lNeckTineIx.append(bufIx)
                        bReverse.append(bRvs)


            # creating junction table
            for ix, jsw in enumerate(lNeckTine):
                jc = Junction(jsw, lNeckTineIx[ix], bReverse[ix])

            
        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() ) 



    @classmethod
    def findMatchTsId(cls, refTs, ts1, ts2):
        ix = -1
        
        if refTs != None:
            if ts1 != None:
                if refTs.id == ts1.id:
                    ix = 0
                
            if ts2 != None:
                if refTs.id == ts2.id:
                    if ix == -1:
                        ix = 1
                    else:
                        ix = 2  # '2' means 3 TS IDs are identical.

        elif ts1 == None:
            ix = 0

            if ts2 == None:
                ix = 3  # '5' means 3 TSs are None

        elif ts2 == None:
            ix = 1

        return ix


    @classmethod
    def populateConnectedJunctions(cls):
        '''
        This method populate jsRef list in each junction.
        Other junctions in this list are connected to current junction object via current junction's fork tines.        
        '''

        for ix, jc in enumerate(cls.__jcList):
            ln = len(jc.fork)
            i = 0
            if ln > 1:
                if jc.fork[1] != None:
                    if jc.bReverse == False:
                        if jc.fork[1].junction[1] != None:
                            jc.jswRef[i] = jc.fork[1].junction[1]
                            i += 1
                    else:
                        if jc.fork[1].junction[0] != None:
                            jc.jswRef[i] = jc.fork[1].junction[0]
                            i += 1
            if ln > 2:
                if jc.fork[2] != None:
                    if jc.bReverse == False:
                        if jc.fork[2].junction[1] != None:
                            jc.jswRef[i] = jc.fork[2].junction[1]
                            i += 1
                    else:
                        if jc.fork[2].junction[0] != None:
                            jc.jswRef[i] = jc.fork[2].junction[0]
                            i += 1


    @classmethod
    def addNewReversedJunctionIfFound(self, trackIx, tsIx, ts_list):
        '''
        It search track segments of which tails are connected together.
        It there are 2 or more track segments that are connected at
        the same location. It will add them to a the junction list __jcList.
        '''
        #count = 0
        rightLinkIdx = ts_list[trackIx][tsIx].rConnector[0].idX
        rightLinkIdy = ts_list[trackIx][tsIx].rConnector[0].idY

        #index = []
        tSeg = ts_list[trackIx][tsIx]

        ln = len(ts_list[trackIx])        
        st = tsIx + 1

        if st >= ln:
            trackIx += 1
            if trackIx >= len(ts_list):
                return
            st = 0

        # iterate by each track to find junctions which can be considered as junctions
        # when it looked reverse direction.
        for ix in range(trackIx, len(ts_list)):
        #for ts in ts_list:

            # iterate by each track segment
            # check if any junction on a given track which is the same track as 'ts' locates.
            bFound = False
            
            for i in range(st, len(ts_list[ix])):
            #for i in range(0, len(ts)):
                bFound = False


                # find junctions from the next track segment.
                # one junction found
                if rightLinkIdx == ts_list[ix][i].rConnector[0].idX:
                    if rightLinkIdy == ts_list[ix][i].rConnector[0].idY:
                        #index.append([ix, i])
                        #tSeg.append(ts_list[ix][i])
                        
                        #if count > 0:
                        bFound = True
                        # the track segment indicated by 'j' must be first used to
                        # instantiate following object rather than 'i'.
                        # Otherwise the 3rd match will be discarded due to 'valid == False'.
                        js = Junction(ts_list[ix][i], True)
                        # check if it existed already.
                        if js.valid == False:
                            del(js)
                        else:
                            # Add information about the other track segment.
                            js.addNewJunctionSwitch(tSeg, True)


                        break

                        #count += 1
            
            if bFound == True:
                break

            st = 0


    
    

    def setPass(self, ix):
        self.passPermit[ix] = True
        #self.bInMoving = True  #5.21




    def getSwitchDirection(self, train):
        
        ix = None
        ts = train.getNextTrackSegmentToSwitchTo()
        if ts != None:
            for i, ro in enumerate(self.rOrientation):
                if ro == ts.rOrientation:                                    
                    ix = i  #self.switchDirIx = ix #ts.rOrientationd
                    break

        #return self.switchDirIx
        return ix


    

    def isJcSwitchReady(self, train, newSwDirIx, signal=None):
        '''
        This method will take all necessary steps to get the junction switch
        placed in its desired position. Additionally, it will manage new
        switching requests by registering them and set one of them as an
        active request which is immediately served.
        * Return:
            - True: The JcSw (Junction Switch) is ready to get the train move in and pass through.
                    The JcSw was set properly as well as other junctions associated to the train path.
            - False The JcSw (Junction Switch) is not ready to get the train move in.
        '''

        bRlt = True
        
        bFound = False
        ix = None
        swq = None

        if len(self.swReqQueue) > 0:

            if self.swReqQIx != None:   # there is one or more train which was enqueued/registered.
                if self.swReqQueue[self.swReqQIx].id != train.id:    # not an active train
                    bRlt = False

                    # search the queue to see if it needs to be registered as new.
                    for i, sq in enumerate(self.swReqQueue):
                        # Is the train in the list of Switching Request Que?
                        if sq == train:
                            bFound = True
                            # swq = sq
                            # ix = i
                            break

                else:
                    bFound = True
            else:
                bRlt = False

        
        if bFound == False:
            bRlt = False
            if signal != None:
                if self.registerNewSwReq(train, signal) == True:
                    if self.setToActiveTrain(train, signal) == True:
                        bRlt = True

        # is this train the active train to be maintained?
        if self.movingTrain != None and bRlt == True:    # it is an active one
            
            # Wasn't th train marked as away from the junction before?
            if self.bTrainAway[self.swReqQIx] == False: # not far away
                bAway = self.isTrainFarAway(train)

                if bAway == True:
                    # need to get the junction switch hidden.

                    # Wasn't the junction S/W hidden?
                    if self.bWaitingDspConfirm != None:

                        r = Display.getServiceResultFromDsp(self.num)

                        # Jc Sw in place or hidden ?
                        if r[1] == newSwDirIx or r[1] != Param.JC_SW_ARROW_HIDDEN:

                            r = Display.updateDspOnJcSwitchState(self.num, Param.JC_SW_ARROW_HIDDEN)    # requesting arrow-hide
                            # Jc Sw hidden?
                            if r[1] == Param.JC_SW_ARROW_HIDDEN:
                                if self.requestToGetJcSwitchUnlocked(self.num, train) == True:
                                    self.bWaitingDspConfirm = None  # This is the only method in which it can be set to None

                                    self.bTrainAway[self.swReqQIx] = bAway  # to be set True if it is a candidate to be removed from the swReqQueue
                            elif r[1] == newSwDirIx:  # Jc Sw in place ?
                                self.bWaitingDspConfirm = False
                            else:
                                self.bWaitingDspConfirm = True

                        elif self.movingTrain.id == train.id:   # the moving train is far away, so no longer need to guide its path.
                                                                            # In my test, the signal device which got the release from the junction earlier
                                                                            # didn't take the release notice, and re-requested the junction to set the switch.
                                                                            # To fix the issue, this 'elif' block has been added.
                            if self.requestToGetJcSwitchUnlocked(self.num, train) == True:
                                self.bWaitingDspConfirm = None  # This is the only method in which it can be set to None

                                self.bTrainAway[self.swReqQIx] = bAway  # to be set True if it is a candidate to be removed from the swReqQueue


                else:
                    # the jc sw wasn't set before?
                    #if newSwDirIx == None:
                    #    self.switchDirIx = self.getSwitchDirection(train)

                    if newSwDirIx != None:
                        r = Display.getServiceResultFromDsp(self.num)

                        if r[1] != newSwDirIx:

                            # No neighboring junction requested switch hold?
                            if self.bSwitchLocked != True:  # either False or None

                                if self.requestToGetJcSwitchLocked(self.num, train) == True:

                                    r = Display.updateDspOnJcSwitchState(self.num, newSwDirIx)
                                    
                                    if r[1] == Result.ERR_NEED_CONFIRM_FIRST:
                                        r = Display.getServiceResultFromDsp(self.num)

                                    # Jc Sw in place ?
                                    if r[1] == newSwDirIx:
                                        self.bWaitingDspConfirm = False
                                    else:
                                        self.bWaitingDspConfirm = True

                                else:
                                    bRlt = False
                            else:
                                bRlt = False

                        elif train.id == self.movingTrain.id:
                            if self.bWaitingDspConfirm == True:
                                self.bWaitingDspConfirm = False

                    else:
                        ps1 = Util.convertCoordinateFormat(self.location.idX, self.location.idY)
                        ps2 = Util.convertCoordinateFormat(self.movingTrain.initLocation.idX, self.movingTrain.initLocation.idY)
                        ps3 = Util.convertCoordinateFormat(train.currentLocation.idX, train.currentLocation.idY)
                        Log.print(f"jsw({self.num}): train {train.trainNum} {ps2}\t\t\t\tWarning!\tThe train @{ps3} unknown to the jsw @{ps1}", MsgLvl.CORE_MSG)

        
        if self.bWaitingDspConfirm == True or bRlt == False:
            # to inform that the JcSw (Junction Switch) is not ready, so busy
            return False
        
        else:
            
            # to inform that the JcSw (Junction Switch) is free and the junction switch was set properly.
            return True


    def setToActiveTrain(self, train, signal):
        # is the junction free?
        if self.bWaitingDspConfirm == None: # and self.switchDirIx == None:    # the junction is free
            for ix, tr in enumerate(self.swReqQueue):
                if self.swReqQueue[ix].id == train.id:
                    self.swReqQIx = ix
                    self.movingTrain = train
                    
                    # it can be set to True only when the signal requests it.
                    #self.bInMoving = True
                    
                    # if self.bInMoving == False or self.switchDirIx == None:
                    self.switchDirIx = self.getSwitchDirection(train)
                    
                    
                    # #ix = self.getSwitchDirection(train)
                    self.bWaitingDspConfirm = True
                    # self.isJcSwitchReady(train, True)

                    return True
                
        return False
    
    def registerNewSwReq(self, train, signal):
        '''
        Return:
            - True:  the train was new and registered
            - False: the train was not registered this time, it was done earlier.
        '''

        for tr in self.swReqQueue:
            if tr.id == train.id:
                return False
                
        ix = self.getSwitchDirection(train)                
        self.swReqQueue.append(train)
        self.bTrainAway.append(False)
        self.switchIndex.append(ix)         # it is an index to the segment to which the train will be switched.

        self.passPermit.append(False)
        self.msgStatus.append(0)
        self.sigRef.append(signal)

        # # reject request unless the junction is completely free
        # if self.movingTrain == None:
        #     if self.bWaitingDspConfirm != True:
        #         # set the index of active train
        #         self.swReqQIx = len(self.swReqQueue) - 1
        #         if bSetToMove == True:
        #             self.switchDirIx = ix

        return True

    def deregisterOldSwReq(self, ix, train=None) -> bool:

        if train != None and ix == None:
            for i, tr in enumerate(self.swReqQueue):
                if tr.id == train.id:
                    ix = i
        
        if ix != None:
            self.passPermit.pop(ix)
            self.swReqQueue.pop(ix)
            self.bTrainAway.pop(ix)
            self.switchIndex.pop(ix)
            self.msgStatus.pop(ix)
            self.sigRef.pop(ix)

            if ix == self.swReqQIx:
                self.swReqQIx = None

            if len(self.swReqQueue) == 0:
                self.swReqQIx = None
        else:
            return False
        
        return True
    

    def requestToGetJcSwitchUnlocked(self, jcNo, train) -> bool:
        
        bRlt = True
    
        for j in self.jswRef:
            if j != None:
                if jcNo != j.num:
                    if j.requestToGetJcSwitchUnlocked(self.num, train) == False:
                        bRlt = False

        if bRlt == True:
            if jcNo != self.num:
                self.bSwitchLocked = False

        return bRlt
    

    def requestToGetJcSwitchLocked(self, jcNo, train) -> bool:

        bRlt = True

        # Any pending switch change in your junction? #5.21 by removing this 'if' statement, it works better.
        #if self.bWaitingDspConfirm != True:
        if True:
            
            # Your aren't a dummy
            #if self.bJcDummy == False: #5.21
            if True:
                
                if self.bSwitchLocked == False:

                    if self.switchDirIx != None:
                        if jcNo != self.num:
                            r = Display.updateDspOnJcSwitchState(self.num, Param.JC_SW_ARROW_HIDDEN)
                            if r[1] != Param.JC_SW_ARROW_HIDDEN:
                                bRlt = False

            if bRlt == True:
                if jcNo != self.num:
                    self.bSwitchLocked = True

        
            for j in self.jswRef:
                if j != None:
                    if jcNo != j.num:
                        if j.requestToGetJcSwitchLocked(self.num, train) == False:
                            bRlt = False
        # else:
        #     bRlt = False

        return bRlt
    


    
    def isTrainFarAway(self, train, bMsg=False) -> bool:
        if train == None:
            bAway = None
        else:
            bAway = False
            extraLen =  (train.trainLength - Size.trackSegmentLength)

            if bMsg == True:
                ps1 = Util.convertCoordinateFormat(self.location.idX, self.location.idY)
                #ps2 = Util.convertCoordinateFormat(self.movingTrain.initLocation.idX, self.movingTrain.initLocation.idY)
                ps3 = Util.convertCoordinateFormat(self.movingTrain.currentLocation.idX, self.movingTrain.currentLocation.idY)

            if train.bForward == True:
                if self.bReverse == False:
                    # the junction locates right end of the TS.
                    ln = self.location.idX + Size.trackSegmentLength + extraLen
                    # if train.currentLocation.idX >= self.location.idX + Size.trackSegmentLength * 2 + extraLen:
                    #     bAway = True
                else:
                    ln = self.location.idX + extraLen

                    # if train.currentLocation.idX >= self.location.idX + extraLen:
                    #     bAway = True

                dst = ln - train.currentLocation.idX                
                msg = "."

            else:

                if self.bReverse == False:
                    ln = self.location.idX - Size.trackSegmentLength - extraLen
                    # if train.currentLocation.idX <= self.location.idX - Size.trackSegmentLength - extraLen:
                    #     bAway = True
                else:
                    ln = self.location.idX - (Size.trackSegmentLength * 2) - extraLen                    
                    # if train.currentLocation.idX <= self.location.idX - (Size.trackSegmentLength * 2) - extraLen:
                    #     bAway = True

                dst = train.currentLocation.idX - ln
                msg = "_"
                
            if dst <= 0:
                bAway = True

            if bMsg == True:
                Log.print(f"\t{msg} Left ({self.num}:{ps1}), tr ({self.movingTrain.trainNum}: cnt({self.movingTrain.moveCount}) @{ps3}: {dst}/{ln}\t\t[js_run]", MsgLvl.DBG_MSG_DSP_UPDATE)

        return bAway
    

    
        
    def markTheTrainPassed(self, train):
        
        if self.swReqQueue[self.swReqQIx].id == train.id:
            if self.isJcSwitchReady(train, Param.JC_SW_ARROW_HIDDEN) == True:

                if self.bWaitingDspConfirm == None:
                    self.sigRef[self.swReqQIx].msgFromJunction(train, True)
                    

                    cnt = 0
                    for req in self.swReqQueue:
                        if req != None:
                            cnt += 1

                    self.movingTrain = None     # markTheTrainPassed(...)
                    self.bInMoving = None
                    self.switchDirIx = None
                    
                    self.deregisterOldSwReq(self.swReqQIx, None)
                    self.requestToGetJcSwitchUnlocked(self.num, train)



    def passRequest(self, train, signal) ->  Tuple[bool, str]:
        r = [False, ""]

        bFound = False
        ps3 = Util.convertCoordinateFormat(train.currentLocation.idX, train.currentLocation.idY)
        Log.print(f"\tjsw ({self.num})  passReq:\tsig ({signal.num})\ttr #{train.trainNum} @{ps3} cnt ({train.moveCount})\t[js_passRequest]", MsgLvl.DBG_MSG_DSP_UPDATE)

        r[0] = False

        if self.movingTrain != None:
            if self.movingTrain.id == train.id:
                if self.isJcSwitchReady(train, self.switchDirIx, signal) == True:
                    r[0] = True
                    r[1] = "Switch Req. and Switched (jsw)!"
                    self.passPermit[self.swReqQIx] = True

        else:
            ix = self.getSwitchDirection(train)
            if ix != None:
                if self.isJcSwitchReady(train, ix, signal):
                    r[0] = True
                    r[1] = "Switch Req. and Switched (jsw)!"
                    self.passPermit[self.swReqQIx] = True
                    #5.21
                    # if self.bWaitingDspConfirm == None:
                    #     self.bInMoving = True
        return r

    



    def run(self):

        try:
            if SimControl.bSimStarted == True :
                clk = SimControl.controlClock

                # if clk > 80:   # for debug break point
                #     a = 30
                # if self.movingTrain != None:
                #     if self.movingTrain.initLocation.idX == 19 and self.movingTrain.initLocation.idY == 3:
                #         if self.movingTrain.currentLocation.idX == 7:
                #             a = 3
                
                for ix, req in enumerate(self.swReqQueue):
                    if self.bInMoving == True:
                        if self.movingTrain != None:
                            # if clk > 100:   # for debug break point
                            #     a = 30

                            if self.isTrainFarAway(self.movingTrain, True) == True or self.movingTrain.state == TrainState.PARKED_STATE:
                                self.markTheTrainPassed(self.movingTrain)
                            break
                        else:
                            Log.print(f"\tjsw {self.num}\t\t\t\tNo moving Train({self.num})\t[js_run]\t", MsgLvl.DBG_MSG_DSP_UPDATE)
                            self.bInMoving = False
                            break
                    else:
                        break

                
                
                if self.bInMoving == False or self.movingTrain == None:
                    # there is no moving train, so no communication possible with outside
                    # because of no train ID for the communication with either the signal or the display.

                    #if len(self.swReqQueue) > 0:
                    if self.swReqQIx != None:
                        ix = self.swReqQIx
                        tr = self.swReqQueue[ix]
                        if self.setToActiveTrain(tr, self.sigRef[ix]) == True:
                            self.passPermit[ix] = True
                            self.msgStatus[ix] = 0
                            #self.bInMoving = True  #5.21

                        ps3 = Util.convertCoordinateFormat(tr.currentLocation.idX, tr.currentLocation.idY)
                        Log.print(f"\tjsw {self.num}, tr ({tr.trainNum}) @({ps3})\t\t\t\tJSW set to pass({self.num})\t[js_run]", MsgLvl.DBG_MSG_DSP_UPDATE)
                        if tr.state == TrainState.PARKED_STATE:
                            self.markTheTrainPassed(tr)
                    else:
                        Log.print(f"\tjsw ({self.num})\t\t\tNo s/w req!({self.num})\t\t[js_run]", MsgLvl.DBG_MSG_DSP_UPDATE)

                #}  

        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() ) 

                    

                




                    