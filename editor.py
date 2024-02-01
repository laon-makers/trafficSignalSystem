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
from component import Location
from utils import Size, TrackSegLayout, Id
from train import TrainState

class EditorGrid:

    def __init__(self):
        pass


    @classmethod
    def isInGrid(cls, idx, idy) -> bool:
        if idx > 0 and idx <= Size.numTrackGridX:
            if idy > 0 and idy <= Size.numTrackGridY:
                return True
            
        return False


class TsegComp_inEditor:
    tsList = []

    def __init__(self, idx, idy, orientation):
        self.bValid = False
        cnt = 0
        if EditorGrid.isInGrid(idx, idy) == True:
            self.bValid = True

            if len(TsegComp_inEditor.tsList) > 0:
                # check if there is another component on the same location
                for ts in TsegComp_inEditor.tsList:
                    if ts.lConnector[0].idX == idx and ts.lConnector[0].idY == idy:
                        if ts.rOrientation == orientation:
                            self.bValid = False
                            break
                        else:
                            cnt += 1

        if cnt > 1:
            # current system support maximum 2 branches.
            self.bValid = False

        if self.bValid == True:
            self.tSeg = Id()        
            self.bForked = False
            self.signal = [None, None]  # reference to SigComp_inEditor object.

            # Calculate the connector id on the left end.
            adjX = idx
            adjY = idy
            if orientation == TrackSegLayout.VERTICAL:
                adjX += Size.trackSegmentHeightIdXIncrementStep   # only x location id value is increased by 1 for x axis connection value in the other end of the track segment.
            else:
                adjY -= Size.trackSegmentHeightIdYIncrementStep   # only x location id value is increased by 1 for x axis connection value in the other end of the track segment.

            # 2 connectors on the left end of the track segment. The first one faces the grid line.
            self.lConnector = [Location(idx, idy), Location(adjX, adjY)]


            # Calculate the connector id on the other (right) end.
            adjX = idx
            adjY = idy

            if orientation == TrackSegLayout.VERTICAL:
                adjX += Size.trackSegmentHeightIdXIncrementStep   # only x location id value is increased by 1 for x axis connection value in the other end of the track segment.
            else:
                adjY -= Size.trackSegmentHeightIdYIncrementStep   # only x location id value is increased by 1 for x axis connection value in the other end of the track segment.

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

            # The other 2 connectors. The first element faces the grid line.
            self.rConnector = [Location(idx, idy), Location(adjX, adjY)]

            self.rOrientation = orientation
            TsegComp_inEditor.tsList.append(self)


    
    
    def addSignalRefToTrackSeg(self, sig, bOnLeft):
        if bOnLeft == True:
            self.signal[0] = sig
        else:
            self.signal[1] = sig

    def deleteSignalRefFromTrackSeg(self, sig, bOnLeft):
        if bOnLeft == True:
            self.signal[0] = None
        else:
            self.signal[1] = None
        
    def deleteTrackSegComponent(self):
        for ix, ts in enumerate(TsegComp_inEditor.tsList):
            if ts.id == self.id:
                TsegComp_inEditor.tsList.pop(ix)

    @classmethod
    def deleteTrackSegComponentByXY(cls, idx, idy, orientation) -> bool:
        for ix, ts in enumerate(TsegComp_inEditor.tsList):

            if ts.lConnector[0].idX == idx and ts.lConnector[0].idY == idy:
                if ts.rOrientation == orientation:
                    TsegComp_inEditor.tsList.pop(ix)
                    return True
        
        return False
    
    @classmethod
    def getNumberOfTrackSegmentComponent(cls) -> int:
        return len(TsegComp_inEditor.tsList)





class SigComp_inEditor:
    '''
    '''
    sigList = []

    def __init__(self, idx, idy):
        self.bValid = False
        if EditorGrid.isInGrid(idx, idy) == True:
            if len(TsegComp_inEditor.tsList) > 0:
                # check if there is another component on the same location
                for ts in TsegComp_inEditor.tsList:
                    if ts.lConnector[0].idX == idx and ts.lConnector[0].idY == idy:
                        # a track segment found to get it installed on.
                        if ts.bValid == True:
                            if ts.signal[0] == None:
                                self.bValid = True
                                self.bOnLeftEnd = True
                                ts.addSignalRefToTrackSeg(self, True)
                                break
                        else:
                            break

                    elif ts.rConnector[0].idX == idx and ts.rConnector[0].idY == idy:
                        # a track segment found to get it installed on.
                        if ts.bValid == True:
                            if ts.signal[1] == None:
                                self.bValid = True
                                self.bOnLeftEnd = False
                                ts.addSignalRefToTrackSeg(self, False)
                                break
                        else:
                            break

        if self.bValid == True:
            self.id = Id().id

            self.trackSegId = None            
            self.location = Location(idx, idy)
            self.sigList.append(self)

    @classmethod
    def deleteSignalComponentByXY(cls, idx, idy):
        for ix, sg in enumerate(SigComp_inEditor.sigList):

            if sg.location.idX == idx and sg.location.idY == idy:
                if len(TsegComp_inEditor.tsList) > 0:
                    # check if there is another component on the same location
                    for ts in TsegComp_inEditor.tsList:
                        if ts.lConnector[0].idX == idx and ts.lConnector[0].idY == idy:
                            # a track segment found to get it unregistered.
                            ts.deleteSignalRefFromTrackSeg(sg, True)
                            break
                            
                        elif ts.rConnector[0].idX == idx and ts.rConnector[0].idY == idy:
                            # a track segment found to get it unregistered.
                            ts.deleteSignalRefFromTrackSeg(sg, False)
                            break
                SigComp_inEditor.sigList.pop(ix)
                return True
        
        return False
            

    @classmethod
    def getNumberOfSignalComponent(cls) -> int:
        return len(SigComp_inEditor.sigList)
    

class TrainComp_inEditor:
    
    trainList = []      # a list of Train objects

    def __init__(self, idx, idy, dstIdx, dstIdy):
        self.bValid = False

        if EditorGrid.isInGrid(idx, idy) == True:
            if EditorGrid.isInGrid(dstIdx, dstIdy) == True:
                self.bValid = True

                if len(TrainComp_inEditor.trainList) > 0:
                    # check if there is another component on the same location
                    for tr in TrainComp_inEditor.trainList:
                        if tr.currentLocation.idX == idx and tr.currentLocation.idY == idy:
                            self.bValid = False
                            break  

        if self.bValid == True:
            self.id = Id().id
            self.state = TrainState.STOP_STATE
            self.initLocation = Location(idx,idy)
            self.currentLocation = Location(idx,idy)
            self.destination = Location(dstIdx,dstIdy)
            TrainComp_inEditor.trainList.append(self)
    
    @classmethod
    def deleteTrainComponentByXY(cls, idx, idy, dstIx, dstIy):
        for ix, tr in enumerate(TrainComp_inEditor.trainList):

            if tr.initLocation.idX == idx and tr.initLocation.idY == idy:
                if tr.destination.idX == dstIx and tr.destination.idY == dstIy:
                    TrainComp_inEditor.trainList.pop(ix)
                    return True
        
        return False

    @classmethod
    def getNumberOfTrainComponent(cls) -> int:
        return len(TrainComp_inEditor.trainList)


    '''
    '''
class Components:
    def __init__(self):
        self.trackSeg = []
        self.signal = []
        self.junction = []
        self.train = []
