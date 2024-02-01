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
import unittest   # The test framework
from utils import TrackSegLayout
from log import Log
from control import Control
from train import Train
from trackSegment import TrackSegment
from junctionSwitch import Junction



    
class Test_SystemDataStructure(unittest.TestCase):

    # as a developer, I would like implement the system initialization method.
    def test_1_systemInit(self):
        ctrl = Control()
        self.assertIsNone(ctrl.systemReInit())

    # as a developer, I would like to make the data structure of the track segment.
    def test_2_trackSegmentDataStructure(self):
        '''
        Testing the data structure of the Track Segments
        '''
        
        ts = TrackSegment(1,1, TrackSegLayout.HORIZONTAL)
        # new array has been added for this object into the tsList.
        self.assertEqual(len(TrackSegment.tsList), 1)
        # new object is added to the tsList
        self.assertEqual(len(TrackSegment.tsList[0]), 1)

        ts = TrackSegment(3,1, TrackSegLayout.HORIZONTAL)
        # the 2nd object is added to the tsList.
        self.assertEqual(len(TrackSegment.tsList[0]), 2)
        
        # one connection value on the right end of the first track segment object is the same value with
        # the other one at the left end of the 2nd track segment object. So that the connection is made.
        self.assertEqual(TrackSegment.tsList[0][0].rConnector[0].idX, TrackSegment.tsList[0][1].lConnector[0].idX)
        self.assertEqual(TrackSegment.tsList[0][0].rConnector[0].idY, TrackSegment.tsList[0][1].lConnector[0].idY)

        ts = TrackSegment(1,3, TrackSegLayout.HORIZONTAL)
        # new array has been added for 3rd object into the tsList[1].
        self.assertEqual(len(TrackSegment.tsList), 2)
        # the 3rd object is added to the tsList.
        self.assertEqual(len(TrackSegment.tsList[1]), 1)

        # test sorting method
        ts = TrackSegment(10,5, TrackSegLayout.DOWN)
        ts = TrackSegment(1,5, TrackSegLayout.HORIZONTAL)
        self.assertGreater(TrackSegment.tsList[2][0].lConnector[0].idX, TrackSegment.tsList[2][1].lConnector[0].idX)
        TrackSegment.sortTrackSegment()
        self.assertLess(TrackSegment.tsList[2][0].lConnector[0].idX, TrackSegment.tsList[2][1].lConnector[0].idX)

    # as a developer, I would like to make the data structure of the junction switches.
    def test_3_junctionSwitchDataStructure(self):
        '''
        Testing the data structure of Junctions and Switches
        '''
        #ts = TrackSegment(1,1, TrackSegLayout.HORIZONTAL)
        #ts = TrackSegment(3,1, TrackSegLayout.HORIZONTAL)
        ts = TrackSegment(5,1, TrackSegLayout.HORIZONTAL)
        ts = TrackSegment(7,1, TrackSegLayout.HORIZONTAL)
        # make a fork
        ts = TrackSegment(5,1, TrackSegLayout.DOWN)
        ts2 = TrackSegment(7,2, TrackSegLayout.HORIZONTAL)
        ts2 = TrackSegment(9,2, TrackSegLayout.HORIZONTAL)
        # to make sure there is no junction object yet.
        self.assertEqual(len(Junction.jcList), 0)        
        #js = Junction(ts)
        
        TrackSegment.sortTrackSegment()

        TrackSegment.updateSegmentOnSignal()
        TrackSegment.setTerminalForTerminalTS()
        
        #ctrl = Control()
        #5.22 Junction.jcList[0].populateJunctionTable(TrackSegment.tsList)
        Junction.populateJunctionTable(TrackSegment.tsList)
        Log.print(f"{len(Junction.jcList[1].trackSeg)}\t({Junction.jcList[1].trackSeg[0].lConnector[0].idX, Junction.jcList[1].trackSeg[0].lConnector[0].idY})")
        # Added one junction related to both (5, 1, TrackSegLayout.HORIZONTAL) and (5,1, TrackSegLayout.DOWN)
        # Additional dummy junction which divert its horizontal layout to another lane which is (10, 5, TrackSegLayout.DOWN)
        self.assertEqual(len(Junction.jcList), 2)
        # Add 2 track segment information related to both (5, 1, TrackSegLayout.HORIZONTAL) and (5,1, TrackSegLayout.DOWN)
        # It is to verify the method 'populateJunctionTable()'.
        self.assertEqual(len(Junction.jcList[0].nextTrackSegLocation), 2)
        #js = Junction(ts2)
        ts = TrackSegment(7,2, TrackSegLayout.DOWN)
        ts = TrackSegment(9,3, TrackSegLayout.DOWN)
        #5.22 Junction.jcList[0].populateJunctionTable(TrackSegment.tsList)
        Junction.populateJunctionTable(TrackSegment.tsList)
        self.assertEqual(len(Junction.jcList), 7) # 2)
        self.assertEqual(len(Junction.jcList[1].nextTrackSegLocation), 1)
        


    # as a developer, I would like to make the data structure of the signals.
    #                 the signal objects are used to control the traffic of trains.
    def test_4_signalDataStructure(self):
        pass

    # as a developer, I would like to make the data structure of the trains.
    def test_5_trainDataStructure(self):
        '''
        Testing the data structure of Trains
        '''
        tr = Train(0,0,0,0)
        # the first object has been added into trainList.
        self.assertEqual(len(Train.trainList), 1)
        
        # new train is not valid one because both initial location ID and destination ID must be set.
        self.assertFalse(tr.isValidTrain())

        tr2 = Train(1,3,0,0)
        # the 2nd object has been added into trainList.
        self.assertEqual(len(Train.trainList), 2)
        
        # the 2nd train is not valid one because both initial location ID and destination ID must be set.
        self.assertFalse(tr2.isValidTrain())
        tr2.addDestinationId(20,3)
        # the 2nd train is valid one because both initial location ID and destination ID are set.
        self.assertTrue(tr2.isValidTrain())

        tr3 = Train(1,5,10,5)
        # the 3rd object has been added into trainList.
        self.assertEqual(len(Train.trainList), 3)
        
        # the 3rd train is valid one because both initial location ID and destination ID are set.
        self.assertTrue(tr3.isValidTrain())

        ctrl = Control()
        ctrl.populateRoutingTable()
    
    # as a developer, I would like to make a method to get the route of the train populated in the routingTable.
    def test_7_trainRoutingTable(self):
        pass

if __name__ == '__main__':
    unittest.main()