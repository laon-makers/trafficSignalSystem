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

from utils import Util, Id, Light, Error, Size, SimControl, TrainState, Table, TrackSegLayout
from component import Location
from train import Train
from junctionSwitch import Junction
from log import Log, MsgLvl
from plot import Display
from component import Sif, SignalComponent
#from control import Control


class SignalDevice:
    '''
    === Prerequisite ===
        Following list of tables must be populated before this method is called.
        - The track segment list tsList.
        - The junction list jcList.
        - Train list trainList and arrival time table.
        - Junction switching table
    '''
    def __init__(self, sig, time, bGreenOn, bRedOn):
        #self.sigId = sid
        self.sig = sig      # object reference of Signal object.
        self.time = time
        self.bGreenOn = bGreenOn
        self.bRedOn = bRedOn
        self.junction = None



class Signal(SignalComponent):
    ''' This class is a virtual signal and signal control.
    === Attributes ===        
    === Private Attributes ===
        None
    === Representation invariants ===
    - 
    - 
    '''

    @classmethod
    @property
    def sigList(cls):
        return  tuple(cls.__sigList)
    


    __sigList = []      # a list of Signal object.

    def __init__(self, idx, idy, location=None, id=None):
        super().__init__(idx, idy, location, id)

        Signal.__sigList.append(self)         # add new Signal object into the __sigList.


    def signalControl(self):
        pass

    def updateNeighboringTs(self, ix, rowIx, colIx, tsRef):

        if self.tsIndex[ix] == None:
            self.tsIndex[ix] = Table(rowIx, colIx)
        else:
            self.tsIndex[ix].rIx = rowIx
            self.tsIndex[ix].cIx = colIx
        self.tsRef = tsRef    


    @classmethod
    def updateNeighboringJsw(cls, ts_list):

        for sg in cls.__sigList:
            
            # search the nearest junction on the left of the signal device.
            rIx = None
            # find the track where the signal is on.
            for ix, tsa in enumerate(ts_list):
                for ts in tsa:
                    if ts.rOrientation == TrackSegLayout.HORIZONTAL:
                        if sg.location.idY == ts.location.idY:
                            rIx = ix
                            break

            if rIx != None:
                sideIx = None
                #bFound = None
                for iy, ts in enumerate(ts_list[rIx]):
                    if ts.forkNeckConnect != None:
                        # fork neck found

                        # any junction on the left of this TS?
                        if ts.junction[0] != None:
                            sideIx = 0
                        elif ts.junction[1] != None:
                            sideIx = 1
                        else:
                            sideIx = None
                            print(f"Warning !  'forkNeckConnect' has been mistakenly set earlier in ts index [{ix}, {iy}]")

                        if sideIx != None:
                            if ts.junction[sideIx].location.idX < sg.location.idX:
                                # it found one junction on the signal's left
                                # but it is not necessary the nearest one on the left.
                                # there might be another one which closer than this one.

                                sg.jswRef[0] = ts.junction[sideIx]

                            elif ts.junction[sideIx].location.idX == sg.location.idX:
                                # unfortunately the signal is siting on a fork neck where it meets its tines.

                                if ts.junction[sideIx].bReverse == False:
                                    # fork tines are on the right of the signal.

                                    sg.jswRef[1] = ts.junction[sideIx]
                                    #bFound = True
                                    break
                                else:
                                    # fork tines are on the left of the signal.
                                    # it found one junction on the signal's left
                                    # but it is not necessary the nearest one on the left.
                                    # there might be another one which closer than this one.
                                    sg.jswRef[0] = ts.junction[sideIx]                                        
                            else:
                                sg.jswRef[1] = ts.junction[sideIx]
                                #bFound = True
                                break

                # discard if the junction is 3 segments away
                if sg.jswRef[0] != None:
                    # the junction is on the left of the signal device
                    if sg.location.idX - sg.jswRef[0].location.idX >= Size.max_distance_btw_junction_and_sig:
                        sg.jswRef[0] = None

                if sg.jswRef[1] != None:
                    # the junction is on the right of the signal device
                    if sg.jswRef[1].location.idX - sg.location.idX >= Size.max_distance_btw_junction_and_sig:
                        sg.jswRef[1] = None



    @classmethod
    def signalScheduling(cls):
        try:
            if len(Junction.jcList) > 0:
                if len(Junction.jcList[0].switchingTable) > 0:
                    Signal.whichTrainFirst(Junction.jcList[0].switchingTable[0])

            if Signal.reviseTimeRevInSwitchingTable(True) == True:
                cnt = 0

                while True:
                    if Signal.reviseTimeRevInSwitchingTable(False) == False:
                        break
                    
                    cnt += 1

                    if cnt > 100:
                        raise ValueError("Failure in revising arrival time in the switchingTable.")

            # updating each trains arrival time table.
            for jcl in Junction.jcList:
                for jc in jcl.switchingTable:
                    for tr in Train.trainList:
                        if tr.id == jc.trainId:
                            tr.reviseRoutingTime(jc.segment, jc.timeRev - jc.time)
                            jc.time = jc.timeRev
                            break

            # Update signal buffer in the tsList.
            #TrackSegment.updateSegmentOnSignal()

            Signal.populateSignalingTable()
            
            # sorting the time table
            for sg in Signal.__sigList:
                sg.signalingTable.sort(key=cls.sortSignalingTable)

        # TODO: apply timeRev to time and routing table
        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() ) 

    @classmethod
    def sortSignalingTable(cls, sigswd) -> int:
        return  sigswd.time

    @classmethod
    def initialize(cls):
        if len(Signal.__sigList) > 0:
            for sg in Signal.__sigList:
                #del(sg.signalingTable) 
                del(sg)

    @classmethod 
    def whichTrainFirst(cls, swTable):
        '''
        It takes a switching table which usually contains
        2 or more train objects. This method returns
        priority train which has priority to pass a junction in
        the question.
        '''
        priIx  = -1
        try:
            Junction.sortJncSwitchingTable()

            for jc in Junction.jcList:
                
                # there are maximum 2 object in each 'jcl'.
                if len(jc.switchingTable) > 1:
                    idy = jc.switchingTable[0].train.currentLocation.idY
                    idy2 = jc.switchingTable[1].train.currentLocation.idY
                    # Are they on the same track?
                    if idy == idy2:
                        # Is the destination is the same track as it initial track?
                        if jc.switchingTable[0].train.destination.idY == idy: #jc.location.idY:
                            # Swapping. One on the same track has lower priority.
                            sw = jc.switchingTable[0]
                            jc.switchingTable[0] = jc.switchingTable[1]
                            jc.switchingTable[1] = sw
                            #break
                        elif jc.switchingTable[1].train.destination.idY != idy2: #jc.location.idY:
                            if jc.switchingTable[0].time > jc.switchingTable[1].time:
                                # Swapping. Shorter distance to the junction is priority.
                                sw = jc.switchingTable[0]
                                jc.switchingTable[0] = jc.switchingTable[1]
                                jc.switchingTable[1] = sw
                                #break
                        #else:
                        #    # One on the same track has lower priority.
                        #    # It is already prioritized.
                        #    #break

                    elif idy != jc.switchingTable[1].train.destination.idY:
                        
                        if idy2 == jc.switchingTable[0].train.destination.idY:
                            # idy2 is priority, so swapping required.
                            sw = jc.switchingTable[0]
                            jc.switchingTable[0] = jc.switchingTable[1]
                            jc.switchingTable[1] = sw
                            #break
                        elif idy == jc.switchingTable[0].train.destination.idY:
                            if idy2 == jc.switchingTable[1].train.destination.idY:
                                # There is a chance they cross but goes to different track.
                                #Log.print(f"\n\tThis is not shared junction between two trains: ({jc.switchingTable[0].train.currentLocation.idX}, {idy}), ({jc.switchingTable[1].train.currentLocation.idX}, {idy2})")
                                if jc.switchingTable[0].time > jc.switchingTable[1].time:
                                    # Swapping. Shorter distance to the junction is priority.
                                    sw = jc.switchingTable[0]
                                    jc.switchingTable[0] = jc.switchingTable[1]
                                    jc.switchingTable[1] = sw

                            # idy is priority already
                            #break
                        elif idy2 == jc.switchingTable[1].train.destination.idY:
                            # idy2 is priority, so swapping required.
                            sw = jc.switchingTable[0]
                            jc.switchingTable[0] = jc.switchingTable[1]
                            jc.switchingTable[1] = sw
                            #break
                    #else: 
                    #    # idy is priority already
                    #    break

        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() ) 




    @classmethod
    def addSignalingData(cls, sig, time, bGreenOn, bRedOn):

        sig.signalingTable.append(SignalDevice(sig, time, bGreenOn, bRedOn))


    @classmethod
    def populateSignalingTable(cls):
        try:
        
            for jcl in Junction.jcList:
                for jsd in jcl.switchingTable:

                    sig = None
                    cnt = -1
                    bFirstSigFound = False
                    tsId = jsd.segment.id
                    lastSig = None

                    Log.print(f"**** ({jsd.segment.lConnector[0].idX}, {jsd.segment.lConnector[0].idY})\t({jsd.segment.rConnector[0].idX}, {jsd.segment.rConnector[0].idY})", 30)

                    for ix, ts in enumerate(jsd.train.routingTable):
                        if cnt > 0:
                            cnt += 1
                        

                        # if ts.bFork == True:
                        #     # reset the counter to find the nearest signal from the junction switch.
                        #     cnt = 0

                        Log.print(f"\t({ts.lConnector[0].idX}, {ts.lConnector[0].idY})\t({ts.rConnector[0].idX}, {ts.rConnector[0].idY})", 30)
                        msg = ""

                        if ts.signal[0] != None:
                            sig = ts.signal[0]
                            msg = "O"
                            cnt = 0
                        if ts.signal[1] != None:
                            sig = ts.signal[1]
                            msg += "o"
                            cnt = 0

                        #print(msg, end='')
                        Log.PrintBNR(msg, 10)
                            
                        # find the junction
                        #if tsId == ts.id:
                        if jsd.segment.lConnector[0].idX == ts.lConnector[0].idX and jsd.segment.lConnector[0].idY == ts.lConnector[0].idY:
                            if jsd.segment.rConnector[0].idX != ts.rConnector[0].idX or jsd.segment.rConnector[0].idY != ts.rConnector[0].idY:
                                continue

                            if cnt < 0:
                                # missing signal.
                                if bFirstSigFound == False:
                                    msg = "Missing signal before"
                                else:
                                    msg = "Missing signal after"
                                msg += f" a junction! Junction location: ({jcl.location.idX}, {jcl.location.idY}, 30)"
                                #raise ValueError(msg) #TODO: restore it after testing.

                 
                            if sig != None:
                                if sig != lastSig:
                                    if bFirstSigFound == False:
                                        t = cnt * jsd.train.travelTimePerSegment
                                        # Green on time
                                        #sgd = SignalDevice(sig, jsd.time - t, True, False)
                                        #sig.addSignalingData(sgd)
                                        sig.addSignalingData(sig, jsd.time - t, True, False)

                                        t = jsd.time + jsd.train.travelTimePerSegment
                                        # Red on time
                                        #sgd = SignalDevice(sig, t, False, True)
                                        sig.addSignalingData(sig, t, False, True)
                                        bFirstSigFound = True



                                    else:
                                        t = jsd.train.travelTimePerSegment
                                        # Green on time
                                        #sgd = SignalDevice(sig, jsd.time - t, True, False)
                                        #sig.addSignalingData(sgd)
                                        sig.addSignalingData(sig, jsd.time - t, True, False)
                                        # set to false in case there is another junction that this
                                        # train should go through.
                                        bFirstSigFound = False

                                    cnt = 0
                                    lastSig = sig


        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() )                         

    @classmethod
    def updateGivenTimeRevInSwitchingTable(cls, jcIx, trainId, time) -> bool:
        '''
        This method is invoked when an arrival time of any train in the
        switchingTable is modified.
        It checks if there is the match train in other junction table, or
        any train affected by the change. If it find any one, it will update
        the timing as well. But it check only elements which indexed by
        a smaller number than 'dataix'.
        '''

        bRevised = False

        for ix, st in enumerate(Junction.jcList):
            
            if ix != jcIx:
                for jsd in st.switchingTable:
                    if jsd.train.id == trainId:
                        jsd.timeRev += time
                        bRevised = True

        return bRevised

                    

    @classmethod
    def reviseTimeRevInSwitchingTable(cls, bFirst) -> bool:
        '''
        The train in the first element in switchingTable has priority in terms of 
        going through the junction than the other trains in the table.
        The number of branch in a junction is maximum 2 in this first version.
        It can be extended to more than 2 later.
        '''
        bRevised = False

        try:
            
            for ix, jc in enumerate(Junction.jcList):
                priIx = 0
                ln = len(jc.switchingTable)

                if ln > 1:
                    if bFirst == True:
                        # to use up-to-date value
                        jc.switchingTable[0].timeRev = jc.switchingTable[0].time

                    tGap = jc.switchingTable[0].train.travelTimePerSegment
                    time = jc.switchingTable[0].timeRev + tGap

                    # Delay following train's arrival time if it is too close to the priority train.
                    for i in range(1, ln):
                        if bFirst == True:
                            # to use up-to-date value
                            jc.switchingTable[i].timeRev = jc.switchingTable[i].time

                        # check if two trains are too close in time when it passes the junction.
                        if (jc.switchingTable[i].timeRev <= time):
                            # add one more default time gap to keep enough distance.
                            jc.switchingTable[i].timeRev = time + tGap
                            bRevised = True
                            cls.updateGivenTimeRevInSwitchingTable(ix, jc.switchingTable[i].train.id, tGap * 2)
                            
                        # to compare with the next one
                        tGap = jc.switchingTable[i].train.travelTimePerSegment
                        time = jc.switchingTable[i].timeRev + tGap

                elif ln == 0:
                    priIx = -1
                    # this junction switch object doesn't have required number of objects.
                    # valid junction switch object must have one or more 
                    # branch track segment information.
                    # The system must stop all traffic since it is a emergency.
                    #Error.setEmergencyTrafficStop()
                    raise ValueError("Missing fork track segment information! Error during signal scheduling.")


        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() ) 

        return bRevised       


    def updateTrackSegId(self, id, bOnLeft):
        self.trackSegId = id
        self.bOnLeft = bOnLeft




    def debug_updateSwitchingTime(self, ix, time, bGreen, bRed):
        self.signalingTable[ix].time = time
        self.signalingTable[ix].bGreenOn = bGreen
        self.signalingTable[ix].bRedOn = bRed

    
    @classmethod
    def turnOffAllSigLights(cls):
        for sg in cls.__sigList:                
            Display.updateSignalLightState(sg.num, Light.RED, sg.location)


    @classmethod
    def showAllSigCompInfo(cls):
        Log.print("\n*** Signal Info (number, id, location, trackSegId, bOnLeft)", MsgLvl.DBG_MSG_COMP_TABLE)
        for sg in Signal.__sigList:
            sg.showSigCompInfo(False)
    
    def showSigCompInfo(self, bHead=True):
        if bHead == True:
            Log.print("\n*** Signal Info (number, id, location, trackSegId, bOnLeft)", MsgLvl.DBG_MSG_COMP_TABLE)
            ps1 = Util.convertCoordinateFormat(self.location.idX, self.location.idY)
            Log.print(f"\t{self.num},\t{self.id},\t{ps1},\t{self.trackSegId},\t{self.bOnLeft}", MsgLvl.DBG_MSG_COMP_TABLE)


    @classmethod
    def showAllSignalJcTable(cls):
        Log.print("\n*** Signal Device Info (number, id, location, Jsw @(left, right, up/down)", MsgLvl.DBG_MSG_TABLE)
        for sg in cls.__sigList:                
                sg.showSignalJcTableRow(False)
    
    def showSignalJcTableRow(self, bHead=True):
        if bHead == True:
            Log.print("\n*** Signal Device Info (number, id, location, Jsw @(left, right, up/down)", MsgLvl.DBG_MSG_TABLE)
        
        ps1 = Util.convertCoordinateFormat(self.location.idX, self.location.idY)
        ps2 = "n/a"
        if self.jswRef[0] != None:
            ps2 = Util.convertCoordinateFormat(self.jswRef[0].location.idX, self.jswRef[0].location.idY)
        ps3 = "n/a"
        if self.jswRef[1] != None:
            ps3 = Util.convertCoordinateFormat(self.jswRef[1].location.idX, self.jswRef[1].location.idY)
        ps4 = "n/a"
        if self.jswRef[2] != None:
            ps4 = Util.convertCoordinateFormat(self.jswRef[2].location.idX, self.jswRef[2].location.idY)
        Log.print(f"\t{self.num},\t{self.id}, @({ps1}),\t{self.trackSegId},\tjsw @({ps2}, {ps3}, {ps4})", MsgLvl.DBG_MSG_TABLE)

    def msgFromJunction(self, train, bPassed):
        try:
            self.bForkPassed = bPassed
            if train != None:
                ps1 = Util.convertCoordinateFormat(train.currentLocation.idX, train.currentLocation.idY)
                Log.print(f"\tsig {self.num} for tr ({train.trainNum} @{ps1})\t\t\tReleased ({self.num})\t[sig_msgFromJunction]", MsgLvl.DBG_MSG_DSP_UPDATE)
            else:
                Log.print(f"\tsig {self.num} for tr (None)\t\t\tReleased ({self.num}) for unknown train\t[sig_msgFromJunction]", MsgLvl.DBG_MSG_DSP_UPDATE)
        except Exception:
            Log.printException( traceback.print_exc() )


    
    def isGreenLight(self, train) -> bool:
        try:
            r = False
            for ix, tr in enumerate(self.greenLightReq):
                #self.trCurrentTsIx[ix] = tsIx
                if tr == train:
                    if self.greenOn[ix] == True:
                        r = True
                    #else:
                    #    self.bInMoving = True
                    #    r = self.isTrainRouteFree(ix)

                    Display.updateSignalLightState(self.num, self.light, self.location)

                    break

        except Exception: 
            Log.printException( traceback.print_exc() )
            
        return r
    
    def markTheTrainPassed(self, train):
        r = False
        for ix, tr in enumerate(self.greenLightReq):
            if tr == train:
                self.bForkPassed = False

                #if self.bInMoving == False:
                self.greenOn[ix] = False
                self.light = Light.RED

                Display.updateSignalLightState(self.num, self.light, self.location)

                ln = len(self.greenOn) - 1
                for j in range(ix, ln):
                    self.greenOn[j] = self.greenOn[j+1]                    
                    self.greenLightReq[j] = self.greenLightReq[j+1]
                    self.trCurrentTsIx[j] = self.trCurrentTsIx[j+1]
                
                self.greenOn[ln] = False
                self.greenLightReq[ln] = None
                self.trCurrentTsIx[ln] = None
                self.movingTrain = None
                self.bInMoving = False

                ps1 = Util.convertCoordinateFormat(train.initLocation.idX, train.initLocation.idY)
                ps2 = Util.convertCoordinateFormat(train.currentLocation.idX, train.currentLocation.idY, "(@")
                Log.print(f"\tsig {self.num} for tr {train.trainNum}, {ps1}{ps2}:\t\t\treleased\t[sig_markTheTrainPassed]", MsgLvl.CORE_MSG)

                break

    def isTrainRouteFree(self, ix) -> bool:
        
        train = self.greenLightReq[ix]
        bFree = True
        ln = len(train.routingTable)
        if ln > (self.trCurrentTsIx[ix] + 1):
            for i in range(self.trCurrentTsIx[ix] + 1, ln):
                for tr in Train.trainList:
                    if tr.id == train.id:
                        continue

                    if tr.currentLocation.idX == train.routingTable[i].lConnector[0].idX:
                        if tr.currentLocation.idY == train.routingTable[i].lConnector[0].idY:
                            ps1 = Util.convertCoordinateFormat(train.initLocation.idX, train.initLocation.idY)
                            ps2 = Util.convertCoordinateFormat(tr.currentLocation.idX, tr.currentLocation.idY, "(@")

                            Log.print(f"\ttrain  {train.trainNum}, {ps1}: \t{train.moveCount}\t\t\tblocked by train #{tr.trainNum} {ps2}", MsgLvl.CORE_MSG)
                            bFree = False
                            break
                if bFree == False:
                    break
        return bFree

    def setGreen(self, ix, jcIx, train) -> bool:
        bRlt = True
        if jcIx != None:
            bRlt = Sif.setReqTrainMovingFlagInJc(self.jswRef[jcIx], True)

        if bRlt == True:
            self.light = Light.GREEN
            if train != None:
                self.greenOn[ix] = True
                self.bInMoving = True
                Log.print(f"\tsig({self.num})  set2Green:\t(tr #{train.trainNum}) cnt ({train.moveCount})\t[sig_setGreen]", MsgLvl.DBG_MSG_DSP_UPDATE)
            else:
                bRlt = False
                Log.print(f"\tsig({self.num})  set2Green:\t(for unknown tr)\t\t[sig_setGreen]", MsgLvl.DBG_MSG_DSP_UPDATE)

        return bRlt

        
    def isTrainPassedSignal(self, train, bMsg=False) -> bool:
        if train == None:
            bAway = None
        else:
            bAway = False
            extraLen =  (train.trainLength - Size.trackSegmentLength)

            if bMsg == True:
                ps1 = Util.convertCoordinateFormat(self.location.idX, self.location.idY)
                #ps2 = Util.convertCoordinateFormat(self.movingTrain.initLocation.idX, self.movingTrain.initLocation.idY)
                ps3 = Util.convertCoordinateFormat(train.currentLocation.idX, train.currentLocation.idY)

            if train.bForward == True:
                ln = self.location.idX + extraLen

                dst = ln - train.currentLocation.idX                
                msg = "."

            else:
                ln = self.location.idX - (Size.trackSegmentLength * 2) - extraLen                    

                dst = train.currentLocation.idX - ln
                msg = "_"
                
            if dst <= 0:
                bAway = True
                if bMsg == True:
                    Log.print(f"\tsig ({self.num}) @{ps1}{msg} tr ({train.trainNum} @{ps3}\tpassed the sig ({self.num})\t\t[sig_isTrainPassedSignal]", MsgLvl.DBG_MSG_DSP_UPDATE)

        return bAway
    
    def getLightState(self, train) -> bool:
        if train == self.movingTrain:
            # if self.light == Light.GREEN:
            #     return True
            # else:
            #     return False
            for ix, tr in enumerate(self.greenLightReq):
                if tr == train:
                    if self.greenOn[ix] == True:
                        return True
                    return False
        
        return None
        

    def greenLightRequest(self, train, tsIx) -> bool:
        try:
            r = False
            bRound = False
            ps2 = Util.convertCoordinateFormat(train.currentLocation.idX, train.currentLocation.idY)
            if train == self.movingTrain:
                for ix, tr in enumerate(self.greenLightReq):
                    
                    if tr == train:
                        bRound = True
                        self.trCurrentTsIx[ix] = tsIx
                        if self.greenOn[ix] == True:
                            r = True

                        #else:
                        #    self.bInMoving = True
                        #    r = self.isTrainRouteFree(ix)

                        Display.updateSignalLightState(self.num, self.light, self.location)

                        break
                    else:
                        if self.bInMoving == True:                            
                            Log.print(f"\tsig({self.num}), tr #{train.trainNum} @{ps2}\t\tmissing train!\t[sig_greenLightRequest]", MsgLvl.DBG_MSG_DSP_UPDATE)
                        
                        else:
                            Log.print(f"\tsig({self.num}), tr #{train.trainNum} @{ps2}\t\tno moving train marked!\t[sig_greenLightRequest]", MsgLvl.DBG_MSG_DSP_UPDATE)
            else:
                for ix, tr in enumerate(self.greenLightReq):
                    if tr == train:
                        bRound = True
                        Log.print(f"\tsig({self.num}), tr #{train.trainNum} @{ps2}\tis not moving train!\t[sig_greenLightRequest]", MsgLvl.DBG_MSG_DSP_UPDATE)
                        break

            # if earlier for loop did iterate to the end of greenLightReq,
            # then the ix is one less then its length value.
            # But if it find the match with the last one, still the same ix.
            # Therefore referencing 'ix' value to determine whether there was match found or not is not a choice.
            if bRound == False:
                Log.print(f"\tsig({self.num}), tr #{train.trainNum}\t\tno match train found!\t[sig_greenLightRequest]", MsgLvl.DBG_MSG_DSP_UPDATE)

                for ix, tr in enumerate(self.greenLightReq):
                    if self.greenLightReq[ix] == None:
                            
                        self.greenLightReq[ix] = train
                        self.greenOn[ix] = False
                        self.trCurrentTsIx[ix] = tsIx

                        if self.movingTrain == None:
                            if self.bInMoving != True:
                                if train.bForward == True:
                                    # no junction on the way to the destination
                                    if self.jswRef[1] == None:
                                        self.movingTrain = tr
                                        self.bInMoving = True
                                else:
                                    # no junction on the way to the destination
                                    if self.jswRef[0] == None:
                                        self.movingTrain = tr
                                        self.bInMoving = True

                            ps1 = Util.convertCoordinateFormat(train.initLocation.idX, train.initLocation.idY)
                            #ps2 = Util.convertCoordinateFormat(train.currentLocation.idX, train.currentLocation.idY)

                            Log.print(f"\ttrain  {train.trainNum} {ps1} for sig ({self.num}):\t\tGreen Request @ {ps2}. [sig_greenLightRequest]", MsgLvl.CORE_MSG)
                            break

            elif self.movingTrain == None:
                if self.bInMoving != True:
                    if train.bForward == True:
                        # no junction on the way to the destination
                        if self.jswRef[1] == None:
                            self.movingTrain = tr
                            self.bInMoving = True
                    else:
                        # no junction on the way to the destination
                        if self.jswRef[0] == None:
                            self.movingTrain = tr
                            self.bInMoving = True
            
            
                # if self.location.idY == 7:  # this if statement is only for debugging purpose breakpoint
                #     if self.location.idX == 15:
                #         a = 30
                
        except Exception: 
            Log.printException( traceback.print_exc() )
            
        return r



    def checkForGreenLight(self):


        # if self.movingTrain != None:  # this if statement is only for debugging purpose breakpoint
        #     if self.movingTrain.initLocation.idX == 19 and self.movingTrain.initLocation.idY == 3:
        #         if self.movingTrain.currentLocation.idX == 7:
        #             a = 3

        for ix, req in enumerate(self.greenLightReq):
            if self.bInMoving == True and self.movingTrain != None:

                if self.bForkPassed == True:
                    if self.isTrainPassedSignal(self.movingTrain) == True:
                        self.markTheTrainPassed(self.movingTrain)
                    # else:
                    #     self.greenOn[self.swReqQIx] = False
                    #     self.light = Light.RED

                elif self.movingTrain.bForward == True:

                        if self.jswRef[1] != None:
                            #if self.jswRef[1].bReverse == False:
                            if self.jswRef[1].passRequest(self.movingTrain, self)[0] == True:
                                bG = True
                                self.setGreen(ix, 1, self.movingTrain)
                            elif self.movingTrain == None:
                                Log.print(f"\tsig({self.num})\t\t\t\tmissing movingTrain info_1!)\t[sig_checkForGreenLight]", MsgLvl.DBG_MSG_DSP_UPDATE)

                        elif self.jswRef[0] != None:
                            # if not reverse orientation, then ignore the junction.
                            # that must be controlled by another signal which locates just before the junction on the left.
                            #if self.jswRef[0].bReverse == True:                                    
                            if self.jswRef[0].passRequest(self.movingTrain, self)[0] == True:
                                bG = True
                                self.setGreen(ix, 0, self.movingTrain)
                            elif self.movingTrain == None:
                                Log.print(f"\tsig({self.num})\t\t\t\tmissing movingTrain info_2!)\t[sig_checkForGreenLight]", MsgLvl.DBG_MSG_DSP_UPDATE)
                        #elif self.isTrainRouteFree(ix) == True:
                        else:
                            if self.movingTrain == None:
                                Log.print(f"\tsig({self.num})\t\t\t\tmissing movingTrain info_3!)\t[sig_checkForGreenLight]", MsgLvl.DBG_MSG_DSP_UPDATE)
                            self.setGreen(ix, None, self.movingTrain)
                                
                else:
                    if self.jswRef[0] != None:    # it should be true but just in case as a temporary resolution.
                        if self.jswRef[0].passRequest(self.movingTrain, self)[0] == True:
                            bG = True
                            self.setGreen(ix, 0, self.movingTrain)
                        elif self.movingTrain == None:
                            Log.print(f"\tsig({self.num})\t\t\t\tmissing movingTrain info_A!)\t[sig_checkForGreenLight]", MsgLvl.DBG_MSG_DSP_UPDATE)
                            
                            bG = False
                        
                        if SimControl.controlClock > 100:
                                a = 30
                    elif self.jswRef[1] != None:    # it should be true but just in case as a temporary resolution.
                        # if not reverse orientation, then ignore the junction.
                        # that must be controlled by another signal which locates just before the junction on the left.
                        #if self.jswRef[1].bReverse == False:
                        if self.jswRef[1].passRequest(self.movingTrain, self)[0] == True:
                            bG = True
                            self.setGreen(ix, 1, self.movingTrain)
                        elif self.movingTrain == None:
                            Log.print(f"\tsig({self.num})\t\t\t\tmissing movingTrain info_B!)\t[sig_checkForGreenLight]", MsgLvl.DBG_MSG_DSP_UPDATE)
                            bG = False
                    #elif self.isTrainRouteFree(ix) == True:
                    else:
                        if self.movingTrain == None:
                            Log.print(f"\tsig({self.num})\t\t\t\tmissing movingTrain info_C!)\t[sig_checkForGreenLight]", MsgLvl.DBG_MSG_DSP_UPDATE)
                        self.setGreen(ix, None, self.movingTrain)
                break                 

            elif req != None:
                if self.greenLightReq[ix] != None:
                    tr = self.greenLightReq[ix]
                    #self.swReqQIx = ix
                    bG = False
                    if self.isTrainRouteFree(ix) == True:
                        iJsfRefix = None
                        if tr.bForward == True:
                            if self.jswRef[1] != None:
                                if self.jswRef[1].passRequest(tr, self)[0] == True:
                                    bG = True
                                    iJsfRefix = 1
                            elif self.movingTrain == None:
                                # there is no more junction for the train until it gets to the destination.
                                bG = True
                    
                        else:
                            if self.jswRef[0] != None:    # it should be true but just in case as a temporary resolution.
                                if self.jswRef[0].passRequest(tr, self)[0] == True:
                                    bG = True
                                    iJsfRefix = 0
                            
                            elif self.movingTrain == None:
                                # there is no more junction for the train until it gets to the destination.
                                
                                bG = True
                            
                        if bG == True:
                            ps1 = Util.convertCoordinateFormat(self.location.idX, self.location.idY)
                            if self.setGreen(ix, iJsfRefix, tr) == True:
                                self.movingTrain = tr
                                Display.updateSignalLightState(self.num, self.light, self.location)
                                
                                Log.print(f"\tGreenOn({self.num})tr({tr.trainNum}: cnt:({tr.moveCount})), {ps1}\t\t\t[sig_checkForGreenLight]", MsgLvl.CORE_MSG)
                            else:
                                #self.greenOn[ix] = False
                                Log.print(f"\tGreenDelayed({self.num})tr({tr.trainNum}: cnt:({tr.moveCount})), {ps1}\t\t\t[sig_checkForGreenLight]", MsgLvl.CORE_MSG)
                    else:
                        Log.print(f"\tsig ({self.num}), tr ({tr.trainNum}:\tcnt({tr.moveCount})\t\tnoFreeRoad ({self.num})\t[sig_checkForGreenLight]", MsgLvl.CORE_MSG) #MsgLvl.CORE_MSG
                else:
                    Log.print(f"\sig ({self.num})  \t\t\tErrEmptyReqQ ({self.num})\t[sig_checkForGreenLight]", MsgLvl.CORE_MSG) #MsgLvl.CORE_MSG
                    if tr.state == TrainState.PARKED_STATE:
                        self.markTheTrainPassed(tr)

                    break


    def run(self):

        try:
            if SimControl.bSimStarted == True :

                clk = SimControl.controlClock

                self.checkForGreenLight()
                if SimControl.controlClock % Size.travelTimePerTrackSegment == 0:
                    
                    ps1 = Util.convertCoordinateFormat(self.location.idX, self.location.idY)
                    if self.light == Light.GREEN:
                        Log.print(f"\tGreen ({self.num})@{ps1}\t\t\t<sig_run>", 1)
                    else:
                        Log.print(f"\t  Red ({self.num})@{ps1}\t\t\t<sig_run>", 1)

        except Exception: 
            Log.printException( traceback.print_exc() ) 