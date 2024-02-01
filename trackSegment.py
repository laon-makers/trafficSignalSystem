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
from utils import Size, TrackSegLayout, MsgLvl
from component import Location, TrackSegComponent
from signals import Signal
from log import Log

class TrackSegment(TrackSegComponent):
    ''' This class is a virtual track segment.
    === Attributes ===        
    === Private Attributes ===
        lConnector:   2 connection points at the left end of a track segment.
        rConnector:  2 connection points at the right end of a track segment.
    === Representation invariants ===
    - 
    - 
    '''

    @classmethod
    @property
    def tsList(cls):
        return tuple(cls.__tsList)
    
    __tsList = []                         # A list of TrackSegment objects. 2 dimension array.

    def __init__(self, idx, idy, orientation, lConn=None, rConn=None, cmpId=None):

        if lConn == None or rConn == None:
            super().__init__(idx, idy, orientation, lConn, rConn, cmpId)
            self.populateConnectors(idx, idy, orientation)
            #self.location = Location(idx,idy)
        else:
            super().__init__(None, None, orientation, lConn, rConn, cmpId)
            self.location = lConn[0]

        # Add new TrackSegmentList object into __tsList.
        self.addNewTrackSegment(self.lConnector[0].idX, self.lConnector[0].idY)


    def addNewTrackSegment(self, idx, idy):
        bAdded = False
        i = j = 0
        length = len(TrackSegment.__tsList)

        if length <= 0 :
            # never added before
            TrackSegment.__tsList.append([])
            TrackSegment.__tsList[0].append(self)

        else:
            for i in range(0, length):
                len2 = len(TrackSegment.__tsList[i])
                if len2 > 0:
                    # need to check only one.
                    if self.__tsList[i][0].lConnector[0].idY == idy:
                        #if length <= 0:
                        #    TrackSegment.__tsList[i].append([])

                        TrackSegment.__tsList[i].append(self)
                        bAdded = True
                        break

            if bAdded == False:
                # new row is required to add new object.
                TrackSegment.__tsList.append([])
                #TrackSegment.__tsList[i][0].append(self)
                TrackSegment.__tsList[length].append(self)

    def updateForkTineConnect(self, bReverse):
        if bReverse == True:
            if self.forkTineConnect == None:                    
                self.forkTineConnect = TrackSegLayout.RIGHT
            elif self.forkTineConnect == TrackSegLayout.LEFT:
                self.forkTineConnect = TrackSegLayout.BOTH_LEFT_RIGHT
        else:
            if self.forkTineConnect == None:                    
                self.forkTineConnect = TrackSegLayout.LEFT
            elif self.forkTineConnect == TrackSegLayout.RIGHT:
                self.forkTineConnect = TrackSegLayout.BOTH_LEFT_RIGHT

    def updateForkNeckToTineTs(self, ts, bReverse):
        if bReverse == True:
            self.forkNeck[1] = ts
        else:
            self.forkNeck[0] = ts
    def getForkNeckFromTineTs(self, bReverse):
        if bReverse == True:
            return self.forkNeck[1]
        else:
            return self.forkNeck[0]

    def updateForkNeckConnect(self, bReverse):
        if bReverse == True:

            if self.forkNeckConnect == None:
                self.forkNeckConnect = TrackSegLayout.LEFT
            elif self.forkNeckConnect == TrackSegLayout.RIGHT:
                self.forkNeckConnect = TrackSegLayout.BOTH_LEFT_RIGHT
        else:
            if self.forkNeckConnect == None:
                self.forkNeckConnect = TrackSegLayout.RIGHT
            elif self.forkNeckConnect == TrackSegLayout.LEFT:
                self.forkNeckConnect = TrackSegLayout.BOTH_LEFT_RIGHT

    def updateForkTineToNeckTs(self, ts1, ts2, bReverse):
        self.forkTine[0] = ts1
        self.forkTine[1] = ts2
        
        if ts2 == None:
            self.bSingleTine = True
        self.updateForkNeckConnect(bReverse)

    def updateJunctionForkNeckTs(self, js, bReverse):
        if bReverse == True:
            self.junction[0] = js
        else:
            self.junction[1] = js

    def addSignalRefToTrackSeg(self, sig, bOnLeft):
        
        self.bSigOnLeftEnd = bOnLeft

        if bOnLeft == True:
            self.signal[0] = sig
        else:
            self.signal[1] = sig


    def populateConnectors(self, idx, idy, orientation):
        adjX = idx
        adjY = idy

        if orientation == TrackSegLayout.VERTICAL:
            adjX += Size.trackSegmentHeightIdXIncrementStep   # only x location id value is increased by 1 for x axis connection value in the other end of the track segment.
        else:
            adjY -= Size.trackSegmentHeightIdYIncrementStep   # only x location id value is increased by 1 for x axis connection value in the other end of the track segment.

        
        # Two of 4 connections on the left end of this track segment.
        # Two or more track segments which share the same values mean that they are connected.
        #
        # It is the connections between track segments. for one end of track segment,
        # especially the left end of the segment (it is the top end if it is vertically aligned).
        # Two connections for the other end is 'rConnector' which is initialized at the bottom of this method.
        self.lConnector = [Location(idx,idy), Location(adjX,adjY)]   # 

        # check if both values are not zero. If not zero, it means the track segment layed on the track grid.
        # so values for the other end of track segment must be assigned with proper none zero values.
        if idx != 0 and idy !=0:
            if orientation == TrackSegLayout.HORIZONTAL:
                idx += Size.locationIdXIncrementStep
                adjX = idx
            elif orientation == TrackSegLayout.VERTICAL:
                idy += Size.locationIdYVerticalIncrementStep
                adjY = idy
            elif orientation == TrackSegLayout.UP:
                idx += Size.locationIdXIncrementStep
                idy -= Size.locationIdYSlopIncrementStep
                adjX = idx
                adjY = idy - Size.trackSegmentHeightIdYIncrementStep
            elif orientation == TrackSegLayout.DOWN:
                idx += Size.locationIdXIncrementStep
                idy += Size.locationIdYSlopIncrementStep
                adjX = idx
                adjY = idy - Size.trackSegmentHeightIdYIncrementStep                
        else:
            idx = idy = adjX = adjY = 0

        # Two of 4 connections on the right end of this track segment.
        # Two or more track segments which share the same values mean that they are connected.
        #
        # It is the connections between track segments. for one end of track segment,
        # especially the right end of the segment (it is the bottom end if it is vertically aligned).
        # Two connections for the other end is 'lConnector' which was initialized earlier within this method.
        self.rConnector = [ Location(idx,idy), Location(adjX,adjY) ]  # (0,0) means not linked to any other track segment.


    # # Get Track ID which is the same value as idX of the connection value
    # # on the left end of the track segment.
    # def getTrackIdY(self, ts) -> int:
    #     return ts.lConnector[0].idY


    @classmethod
    def organizeAndUpdateTrackSegData(cls):
        # the track segment list must be sorted first.
        cls.sortTrackSegment()
        cls.updateSegmentOnSignal()
        cls.setTerminalForTerminalTS()
        
    @classmethod
    def getCurrentLocationIdX(cls, ts) -> int:
        return ts.lConnector[0].idX
    
    
    @classmethod
    def sortTrackSegment(cls, bAll=True, idy=0):
        if bAll == True:
            for ts in cls.__tsList:
                ts.sort(key=cls.getCurrentLocationIdX)
        elif idy > 0 and idy < len(cls.__tsList):
            cls.__tsList.sort(key=cls.getCurrentLocationIdX)
    
    @classmethod
    def setTerminalForTerminalTS(cls):
        for ix, tsa in enumerate(cls.__tsList):

            for iy, ts in enumerate(tsa):

                bLRcFound = False    # to find the terminal on the left end of TS in question; if the left end connection with other TS's right end was found.
                bRLcFound = False    # to find the terminal on the right end of TS in question; if the right end connection with other TS's left end was found.
                cnt = 0
                for ix2, tsa2 in enumerate(cls.__tsList):
                    for iy2, ts2 in enumerate(tsa2):

                        # is it the current TS to be checked?
                        if ix == ix2 and iy == iy2:
                            continue

                        if bLRcFound == False:
                            if ts.lConnector[0].idX == ts2.rConnector[0].idX:
                                if ts.lConnector[0].idY == ts2.rConnector[0].idY:
                                    # the 'ts' is not the terminal.
                                    bLRcFound = True
                                    cnt += 1
                                    #break

                        if bRLcFound == False:
                            if ts.rConnector[0].idX == ts2.lConnector[0].idX:
                                if ts.rConnector[0].idY == ts2.lConnector[0].idY:
                                    # the 'ts' is not the terminal.
                                    bRLcFound = True
                                    cnt += 1
                                    #break
                
                        if cnt > 1:
                            break

                    if cnt > 1:
                        break

                if bLRcFound == False:
                    ts.bLeftTerminator = True

                if bRLcFound == False:
                    ts.bRightTerminator = True
                        

            

    @classmethod
    def updateSegmentOnSignal(cls):
        ''' It updates both track segments on signals and the signal on the neighboring track segments'''

        for sg in Signal.sigList:
            
            Log.print(f"**** ({sg.location.idX}, {sg.location.idY})", 50)

            for rIx, tsa in enumerate(TrackSegment.__tsList):
                for cIx, ts in enumerate(tsa):
                    Log.print(f"\t({ts.lConnector[0].idX}, {ts.lConnector[0].idY})\t({ts.rConnector[0].idX}, {ts.rConnector[0].idY})", 50)

                    if ts.lConnector[0].idX == sg.location.idX:
                        if ts.lConnector[0].idY == sg.location.idY:
                            Log.PrintBNR("\t\t*-", 50)
                            ts.signal[0] = sg
                            sg.updateTrackSegId(ts.id, True)
                            if ts.rOrientation == TrackSegLayout.HORIZONTAL:
                                sg.updateNeighboringTs(0, rIx, cIx, ts)
                            else:
                                sg.updateNeighboringTs(2, rIx, cIx, ts)

                            #ts.bFork = True
                    if ts.rConnector[0].idX == sg.location.idX:
                        if ts.rConnector[0].idY == sg.location.idY:
                            Log.PrintBNR("\t\t*=", 50)
                            ts.signal[1] = sg
                            sg.updateTrackSegId(ts.id, False)
                            #ts.bFork = True
                            if ts.rOrientation == TrackSegLayout.HORIZONTAL:
                                sg.updateNeighboringTs(1, rIx, cIx, ts)
                            else:
                                sg.updateNeighboringTs(2, rIx, cIx, ts)


    @classmethod
    def showAllTsCompInfo(cls):
        
        Log.print("*** Track Segment Info (id, location, <signalId>, bSigOnLeftEnd, terminal)", MsgLvl.DBG_MSG_DSP_UPDATE)
        for ix, tsa in enumerate(cls.__tsList):
            Log.print(f" * Track No. {ix+1}", 100)
            for ts in tsa:
                ts.showTsCompInfo(False)
    
    def showTsCompInfo(self, bHead=True):
        if bHead == True:
            Log.print("*** Track Segment Info (id, location, <signalId>, bSigOnLeftEnd, terminal)", MsgLvl.DBG_MSG_DSP_UPDATE)
        
        id1 = None
        id2 = None
        if self.signal[0] != None:
            id1 = self.signal[0].id
            if self.signal[1] != None:
                id2 = self.signal[1].id

        t = None
        if self.bLeftTerminator == True:
            t = "Left "
        
        if self.bRightTerminator == True:
            if t == None:
                t = ""
            
            t += "Right"

        if t == None:
            t = "No"
        else:
            t = "Terminal: " + t

        Log.print(f"\t{self.id},\t({self.location.idX}, {self.location.idY}),  \t<{id1}, {id2}>\t{self.bSigOnLeftEnd}, {t}", MsgLvl.DBG_MSG_DSP_UPDATE)