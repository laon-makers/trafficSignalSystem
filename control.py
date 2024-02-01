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
import simpy, sys, traceback, time
from utils import TrainState, TrackSegLayout, Size, Error, SimControl, JunctionSwitchDevice
from component import Sif
from train import Train
from trackSegment import TrackSegment
from junctionSwitch import Junction
from signals import Signal
from log import Log
from editor import TsegComp_inEditor, SigComp_inEditor, TrainComp_inEditor, Components
from plot import Display


class Control:
    ''' This class controls traffic light, junction switch, and train.
    === Attributes ===        
    === Private Attributes ===
        None
    === Representation invariants ===
    - 
    - 
    '''

    # All components will get started as soon as it turned to True.
    bSimStarted = False

    def __init__(self):
        #self.signalingTable = []        
        self.simControl = None
        self.simDone = False
        self.display = None

    # 
    def systemReInit(self):
        '''
        this method is called to get the system reinitialized.
        '''
        try:
            Junction.initialize()
            Signal.initialize()

        except Exception: 
            Log.printException( traceback.print_exc() )

    #
    
    def reInitSimulation(self, data):
        '''
        this method is called just before each simulation gets started.
        '''
        # Following method invocation order must be maintained.

        ####### Init attributes for new simulation ######
        try:
            self.systemReInit()

            # build a network            
            self.generateTrafficNetwork(data)            

            # the track segment list must be sorted first.
            TrackSegment.organizeAndUpdateTrackSegData()

            Junction.populateJunctionTable(TrackSegment.tsList)
            Junction.organizeAndUpdateSignalData()

            self.populateRoutingTable()

            Train.validateRoutingTable()            
            Signal.updateNeighboringJsw(TrackSegment.tsList)

            # show all component data            
            TrackSegment.showAllTsCompInfo()
            Signal.showAllSigCompInfo()
            Signal.showAllSignalJcTable()
            Junction.showAllJunctionTable()
            Train.showAllTrCompInfo()           
            Train.showAllRoutingTable()
            
            # following routines must be called at this late.
            # there are data to be shared with the Display, but it must be the latest.
            # Therefore, it is called at the very end of this method.
            # Otherwise there will be an issue when it was invoked inside generateTrafficNetwork
            if self.display == None:            
                if Display.bInitialized == False:
                    self.display = Display(Size.canvasWidth, Size.canvasHeight, TrackSegment.tsList, Signal.sigList, Train.trainList, Junction.jcList)
                    self.display.start()
                elif self.isTrafficSimDisplayLive() == True:
                    Display.bSimulating = True
                    self.display = Display.trafficNetworkDspObject
                    self.display.buildTrafficNetwork(TrackSegment.tsList, Signal.sigList, Train.trainList, Junction.jcList)
                
                else:
                    self.display = Display(Size.canvasWidth, Size.canvasHeight, TrackSegment.tsList, Signal.sigList, Train.trainList, Junction.jcList)
                    self.display.start()
                    #print("\nSorry, something went wrong!  Please restart the application.")
            elif self.isTrafficSimDisplayLive() == True:
                Display.bSimulating = True
                #self.display = Display.trafficNetworkDspObject
                self.display.buildTrafficNetwork(TrackSegment.tsList, Signal.sigList, Train.trainList, Junction.jcList)
            
            else:
                self.display = Display(Size.canvasWidth, Size.canvasHeight, TrackSegment.tsList, Signal.sigList, Train.trainList, Junction.jcList)
                self.display.start()
            
        except Exception:
            Log.printException( traceback.print_exc() ) 



    def getlConnectorIdX(cls, ts) -> int:
        return ts.lConnector[0].idX
    
    def getlConnectorIdY(cls, ts) -> int:
        return ts.lConnector[0].idY

    def generateTrafficNetwork(self, data=None):
        '''
        it build traffic network with given component data.
        '''
        if data == None:
            self.buildDefaultTrafficNetwork()
        else:
            
            TsegComp_inEditor.tsList.sort(key=self.getlConnectorIdX)
            TsegComp_inEditor.tsList.sort(key=self.getlConnectorIdY)

            # add signal first since the constraint, which requires the signals must be
            # attached to the track segment, was applied in the build editor.
            for i, sg in enumerate(data.signal):
                if sg.bValid == True:
                    o = Signal(0,0, sg.location, sg.id)
                    o.num = i + 1

            for ts in data.trackSeg:
                if ts.bValid == True:
                    o = TrackSegment(0, 0, ts.rOrientation, ts.lConnector, ts.rConnector, ts.tSeg)
            
            
            for i, tr in enumerate(data.train):
                if tr.bValid == True:
                    o = Train(tr.initLocation.idX,tr.initLocation.idY,0,0,  tr.id, tr.initLocation, tr.destination)
                    o.trainNum = i + 1


    
    def isTrafficSimDisplayLive(self) -> bool:
        r = False
        try:
            r = Display.poll()
        except Exception:
            r = False
            pass
        finally:
            return r

    def buildDefaultTrafficNetwork(self):
        # building train track
        m = Size.locationIdXIncrementStep * 10
        for i in range(1, m, Size.locationIdXIncrementStep):
            ts = TrackSegment(i,1, TrackSegLayout.HORIZONTAL)
            
        x = 1 + Size.locationIdXIncrementStep * 4
        ts = TrackSegment(x, 1, TrackSegLayout.DOWN)

        x = 1 + Size.locationIdXIncrementStep * 5
        y = Size.locationIdYIncrementStep * 2
        for i in range(x, m, Size.locationIdXIncrementStep):            
            ts = TrackSegment(i,y, TrackSegLayout.HORIZONTAL)

        x = 1 + Size.locationIdXIncrementStep * 4
        y = Size.locationIdYIncrementStep * 3
        ts = TrackSegment(x,y, TrackSegLayout.UP)

        z = Size.locationIdXIncrementStep * 5
        for i in range(1, z, Size.locationIdXIncrementStep):
            ts = TrackSegment(i,y, TrackSegLayout.HORIZONTAL)
        
        x = 1 + Size.locationIdXIncrementStep * 5
        ts = TrackSegment(x,y, TrackSegLayout.DOWN)
        
        x = 1 + Size.locationIdXIncrementStep * 6
        y = Size.locationIdYIncrementStep * 4
        for i in range(x, m, Size.locationIdXIncrementStep):
            ts = TrackSegment(i,y, TrackSegLayout.HORIZONTAL)

        # Add signals
        sg = Signal(7,1)
        sg.num = 1
        sg = Signal(11,1)
        sg.num = 2
        sg = Signal(13,2)
        sg.num = 3        
        sg = Signal(9,3)
        sg.num = 4
        sg = Signal(11,3)
        sg.num = 5

        # Add 4 train
        #1, 3, 5, 7, 9, 11, 13, 15, 17, 19
        tr = Train(1,1,19,2)
        tr.trainNum = 1
        tr = Train(1,3,19,4)
        tr.trainNum = 2
        tr = Train(19,1,1,1)
        tr.trainNum = 3
        tr = Train(19,2,1,3)
        tr.trainNum = 4



    @classmethod
    def populateSwitchingTable(cls):
        '''
        This method find trains which will go through this junction.
        Based on the passing time of each train,
        Switching table is made.
        === Prerequisite ===
            Following list of tables must be populated before this method is called.
            - The track segment list tsList.
            - The junction list __jcList.
            - Train list trainList and arrival time table.
        '''
        try:
            for js in Junction.jcList:
                for ts in js.trackSeg:
                    for tr in Train.trainList:
                        sig = None

                        for ix in range(len(tr.routingTable)):

                            if tr.bForward == True:
                                if tr.routingTable[ix].signal[0] != None:
                                    sig = tr.routingTable[ix].signal[0]
                                
                                if tr.routingTable[ix].signal[1] != None:
                                    sig = tr.routingTable[ix].signal[1]                                
                                
                            else:
                                
                                if tr.routingTable[ix].signal[1] != None:
                                    sig = tr.routingTable[ix].signal[1]                                    
                                if tr.routingTable[ix].signal[0] != None:
                                    sig = tr.routingTable[ix].signal[0]
                                

                            # find a match of segment IDs by comparing one in the junction switch table
                            # and with the other one in the train routing table.
                            if ts.id == tr.routingTable[ix].id:
                                js.switchingTable.append(JunctionSwitchDevice(ix, tr, sig, ts))
                                if sig != None:
                                    sig = js
                                tr.junction = js
                                #ts.junction[0] or ts.junction[1] = js # it will be populated in populateJunctionTable



        
        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() ) 


    
    




    


    def populateRoutingTable(self):
        '''
        It figures out the train's travel route and populate the routing table.
            * Note: Make sure the table tsList was sorted before invoke this method
                    and the junction list jcList must be populated.
            * Steps to populate the table:
            1. Check if the train move in reverse direction (left to right).
                If it is reverse direction, then get the start and destination swapped
                in a local buffer and then populate the route.
                Once the route table population is completed, get the route sorted in
                reverse order.
            2. Checking if both starting track and the destination track are the same one.
            3. If different, find junction to guide the train to the destination.
            4. Populate the routing table.
            5. Sort the routing table.
            6. Populate the arrival time table.
        '''

        try:
            if len(TrackSegment.tsList) > 0:
                for tr in Train.trainList:
                    #bOnSameTrack = False
                    bReverseDir = False

                    # if len(tr.routingTable) > 0:
                    #     del (tr.routingTable)
                    #     del (tr.arrivalTimeTable)

                    if tr.isValidTrain() == False:
                        continue

                    # Check if both starting track and the destination track are the same one.
                    if tr.currentLocation.idX > tr.destination.idX:
                        start = tr.destination
                        dest = tr.currentLocation   # used it instead of initLocation in order to run re-population on the move in the future.                        
                        bReverseDir = True
                        tr.bForward = False
                    else:
                        start = tr.currentLocation
                        dest = tr.destination
                        tr.bForward = True

                    bOnDestinationTrack = False
                    #start = tr.currentLocation
                    #dest = tr.destination

                    # Check if both starting track and the destination track are the same one.
                    if start.idY == dest.idY:
                        dir = None
                        #bToOtherTrack = True
                        # populate the routing table for the given train.
                        for tsa in TrackSegment.tsList:
                            for ts in tsa:
                                
                                # Check if it is the same horizontal train track
                                # If it is different? then ignore current segment because this train is not going to any other track.
                                if start.idY == ts.lConnector[0].idY:   # be aware that both start track and the destination track are the same track within the outer 'if' statement.

                                    # in case the train is set to park any position before the last one,
                                    # the ts which is positioned after the destination must not be in the routing table.
                                    if start.idX <= ts.lConnector[0].idX and ts.lConnector[0].idX <= dest.idX:
                                        # check if it is not a fork to brach to other track.
                                        # if it is, then ignore it because this train was known earlier to travel the same track.
                                        if start.idY == ts.rConnector[0].idY:
                                            tr.routingTable.append(ts)

                    else:
                        # now I know that the train's destination is on different track than its starting track.
                        bJsFound = False
                        dir = TrackSegLayout.HORIZONTAL

                        
                        neck = None

                        # populate the routing table for the given train.
                        for tsa in TrackSegment.tsList:
                            for ts in tsa:
                                
                                # if true, you found the start track
                                if ts.lConnector[0].idY == start.idY: # and ts.rOrientation == TrackSegLayout.HORIZONTAL:
                                    if ts.forkNeckConnect == None and neck == None:
                                        if start.idX <= ts.lConnector[0].idX and ts.lConnector[0].idX <= dest.idX:
                                            # check if it is not a fork to brach to other track.
                                            if start.idY == ts.rConnector[0].idY:
                                                tr.routingTable.append(ts)

                                    #elif bReverseDir == False:
                                    else:
                                        if ts.forkNeckConnect == TrackSegLayout.RIGHT and neck == None:
                                            if start.idX <= ts.lConnector[0].idX and ts.lConnector[0].idX <= dest.idX:
                                                # check if it is not a fork to brach to other track.
                                                if start.idY == ts.rConnector[0].idY:                                                    
                                                    tr.routingTable.append(ts)
                                                    # added to fix another missing TS. It was caused by E3 on the track in the figure IV-4.
                                                    if ts.forkTine[0] != None:
                                                        if ts.forkTine[0].rConnector[0].idY == dest.idY: 
                                                            neck = ts
                                                    if neck == None:
                                                        if ts.forkTine[1] != None:
                                                            if ts.forkTine[1].rConnector[0].idY == dest.idY: 
                                                                neck = ts

                                                    
                                        elif neck != None:
                                            # It is a tine; either on the left or both.
                                            

                                            # is it a right tine to switch to?
                                            #if neck.forkTine[0].rConnector[0].idY == dest.idY:
                                            if ts.rConnector[0].idY == dest.idY:
                                                if start.idX <= ts.lConnector[0].idX and ts.lConnector[0].idX <= dest.idX:
                                                    bOnDestinationTrack = True
                                                    tr.routingTable.append(ts)
                                                    break

                                            else:
                                                if neck.bSingleTine == False:
                                                    #if neck.forkTine[1].rConnector[0].idY == dest.idY:
                                                    if ts.rConnector[0].idY == dest.idY:
                                                        if start.idX <= ts.lConnector[0].idX and ts.lConnector[0].idX <= dest.idX:
                                                            bOnDestinationTrack = True
                                                            tr.routingTable.append(ts)
                                                            break
                                                    #else:
                                                    #    print("Waring! There seems to be a missing track segment (forward direction). Please check the network.")

                                        # it has been added to fix missing segment in the router table. E3 on the track #4 in figure IV-4 did cause this error.
                                        elif ts.forkNeckConnect == TrackSegLayout.LEFT:
                                            if start.idX <= ts.lConnector[0].idX and ts.lConnector[0].idX <= dest.idX:
                                                if start.idY == ts.rConnector[0].idY:
                                                    tr.routingTable.append(ts)


                                    # else:
                                    #     if ts.forkNeckConnect == TrackSegLayout.RIGHT:
                                    #         if start.idX <= ts.lConnector[0].idX and dest.idX >= ts.lConnector[0].idX:
                                    #             # check if it is not a fork to brach to other track.
                                    #             if start.idY == ts.rConnector[0].idY:
                                    #                 tr.routingTable.append(ts)
                                    #                 neck = ts
                                    #     elif neck != None:
                                    #         # It is a tine; either on the left or both.
                                            
                                    #         # is it a right tine to switch to?
                                    #         if neck.forkTine[0].rConnector[0].idY == dest.idY:
                                    #             if start.idX <= ts.lConnector[0].idX and dest.idX >= ts.lConnector[0].idX:
                                    #                 bOnDestinationTrack = True
                                    #                 tr.routingTable.append(ts)
                                    #             break

                                    #         elif neck.forkTine[1].rConnector[0].idY == dest.idY:
                                    #             if start.idX <= ts.lConnector[0].idX and dest.idX >= ts.lConnector[0].idX:
                                    #                 bOnDestinationTrack = True
                                    #                 tr.routingTable.append(ts)
                                    #             break

                                    #         else:
                                    #             print("Waring! There seems to be a missing track segment (reverse direction). Please check the network.")

                            if bOnDestinationTrack == True:
                                break
                        

                    if bOnDestinationTrack == True:
                        # continue finding the rest of the track segments on its trains route,
                        # especially on a different track from the starting track.
                        for tsa in TrackSegment.tsList:
                            for ts in tsa:
                                # if true, you found the destination track
                                if ts.lConnector[0].idY == dest.idY:
                                    if ts.rOrientation == TrackSegLayout.HORIZONTAL:
                                        if neck.rConnector[0].idX < ts.lConnector[0].idX and dest.idX >= ts.lConnector[0].idX:
                                            # check if it is not a fork to brach to other track.
                                            if dest.idY == ts.rConnector[0].idY:
                                                tr.routingTable.append(ts)
                        
                    
                    if bReverseDir == True:
                        if dir == TrackSegLayout.UP:
                            # Sorting is necessary because the destination track segment
                            # has been added first, especially in case the orientation is UP.
                            tr.sortRoutingTable()

                        tl = len(tr.routingTable)
                        ln = int(tl/2)
                        
                        if tl > 1:
                            j = tl - 1
                            # reverse to restore the order
                            #for ts in tr.routingTable:
                            for i in range(0, ln):

                                ts = tr.routingTable[j-i]
                                tr.routingTable[j-i] = tr.routingTable[i]
                                tr.routingTable[i] = ts

            
                # Populate the arrival time table with each arrival time.
                self.populateDefaultArrivalTimeTable()

        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() ) 
    

    def populateDefaultArrivalTimeTable(self):
        try:
            for tr in Train.trainList:
                # if len(tr.arrivalTimeTable) > 0:
                #     del(tr.arrivalTimeTable)

                for i in range(len(tr.routingTable)):
                    t = tr.travelTimePerSegment * i
                    tr.arrivalTimeTable.append(t)
        
        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() ) 







    

    
        


    @classmethod
    def reviseTrainArrivalTimeTable(cls):
        '''
        It must be called after all timeRev values in junction switch table
        are updated by its train's priority.        
        '''

        # for jc in Junction.jcList:
        #      for ts in tsa:
        pass


    



    def startTrafficControlSimulation(self, data) -> bool:
        try:
            print("\n***** Simulation Get Started ! *******\n")
            
            print(" * some data format to be displayed:")
            print("   ** simulation clock **")
            print("\tTrain #Id, (initial location: x,y):     travel-distance")
            print("\t   train (train no.), (initial location: x, y),     (current location: x, y)")
            print("\t   train (train no.), (initial location: x,y)      xx       travel-distance              waiting...\n\n")
            print(" **************************************************************")
            print(" Clock  Component (no.): travel-distance\n")


            self.simDone = False

            self.reInitSimulation(data)

            self.simControl = SimControl()
            self.simControl.run()
            SimControl.bSimStarted = True

            if Sif.simStepInSecond == None:
                env = simpy.Environment()
                env.process(self.traffic_signal_control_sim(env))
                env.run(until=Sif.simTimeOutTick)

            else:
                env = simpy.rt.RealtimeEnvironment(factor=Sif.simStepInSecond)
                proc = env.process(self.traffic_signal_control_sim(env))
                env.run(until=proc)

            n = 0
            for tr in Train.trainList:
                if tr.state == TrainState.PARKED_STATE:
                    n += 1

            if self.simDone == False:
                print(" **************************************************************")
            print(f"\n\n\t** {n} arrived !!  ({n}/{len(Train.trainList)})\n")
            
            if self.simDone == True:
                print("  Simulation Completed !\n\n")
            else:
                print("  Simulation Time Out !!!\n\n")
            print(" **************************************************************\n\n")
        except Exception:
            Log.printException( traceback.print_exc() ) 

        return self.simDone


    def traffic_signal_control_sim(self, env):
        try:

            while True:

                if self.simControl.run() >= Sif.simTimeOutTick:
                    if Sif.simStepInSecond != None:
                        break

                for sig in Signal.sigList:
                    sig.run()

                for js in Junction.jcList:
                    js.run()

                bStillMoving = False
                for tr in Train.trainList:
                    if tr.state != TrainState.PARKED_STATE:
                        bStillMoving = True

                    tr.run()


                if bStillMoving == False:
                    print("\n\n **************************************************************")
                    print("\n\t** All trains are in their destination now !!")
                    self.simDone = True
                    Signal.turnOffAllSigLights()
                    #sys.exit()
                    break
                
                yield env.timeout(Sif.simYieldTimeTick)
                
                if Sif.trainSpeedDelayTimeout > 0:    
                    time.sleep(Sif.trainSpeedDelayTimeout)
                    #time.sleep(0.1)

        except Exception: 
            Error.setEmergencyTrafficStop()
            Log.printException( traceback.print_exc() )     
