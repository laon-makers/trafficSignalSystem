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
from utils import TrackSegLayout, Size
from log import Log
from control import Control
from train import Train
from trackSegment import TrackSegment
from junctionSwitch import Junction
from signals import Signal

from menuSimulator import TsegComp_inEditor, SigComp_inEditor, TrainComp_inEditor


class Test_simEditor(unittest.TestCase):

    # as a developer, I would like to build a train track and test key methods.
    def test_1_componentTest(self):

        # Testing Track Segment Component ###################
        ts = TsegComp_inEditor(1,1, TrackSegLayout.HORIZONTAL)
        self.assertTrue(ts.bValid)
        ts = TsegComp_inEditor(1,1, TrackSegLayout.HORIZONTAL)
        self.assertFalse(ts.bValid)
        del ts       

        ts = TsegComp_inEditor(1,1, TrackSegLayout.DOWN)
        self.assertTrue(ts.bValid)

        # maximum 2 branches from on junction are supported.
        ts = TsegComp_inEditor(1,1, TrackSegLayout.UP)
        self.assertFalse(ts.bValid)
        
        ts = TsegComp_inEditor(3,1, TrackSegLayout.HORIZONTAL)
        n = TsegComp_inEditor.getNumberOfTrackSegmentComponent()
        TsegComp_inEditor.deleteTrackSegComponentByXY(3,1, TrackSegLayout.HORIZONTAL)
        self.assertEqual(n-1, TsegComp_inEditor.getNumberOfTrackSegmentComponent())

        # Testing Signal Component ###################
        ts = TsegComp_inEditor(3,1, TrackSegLayout.HORIZONTAL)
        self.assertTrue(ts.bValid)
        ts = TsegComp_inEditor(3,2, TrackSegLayout.HORIZONTAL)
        self.assertTrue(ts.bValid)
        ts = TsegComp_inEditor(3,1, TrackSegLayout.DOWN)
        self.assertTrue(ts.bValid)
        ts = TsegComp_inEditor(3,3, TrackSegLayout.UP)
        self.assertTrue(ts.bValid)

        sg = SigComp_inEditor(3,3)
        self.assertTrue(sg.bValid)
        self.assertEqual(ts.signal[0], sg)
        sg = SigComp_inEditor(3,3)
        self.assertFalse(sg.bValid)
        del sg

        # cannot add a signal where there is no track segment.
        sg = SigComp_inEditor(1,4)
        self.assertFalse(sg.bValid)

        ts = SigComp_inEditor(3,2)
        self.assertTrue(ts.bValid)
        n = SigComp_inEditor.getNumberOfSignalComponent()
        SigComp_inEditor.deleteSignalComponentByXY(3,2)
        self.assertEqual(n-1, SigComp_inEditor.getNumberOfSignalComponent())

        # Testing Train Component ##########
        tr = TrainComp_inEditor(3,1, 5,1)
        self.assertTrue(tr.bValid)
        self.assertEqual(tr.initLocation.idX, 3)
        self.assertEqual(tr.initLocation.idY, 1)
        self.assertEqual(tr.destination.idX, 5)
        self.assertEqual(tr.destination.idY, 1)
        
        tr = TrainComp_inEditor(1,1, 20,25)
        self.assertFalse(tr.bValid)
        
        n = TrainComp_inEditor.getNumberOfTrainComponent()
        TrainComp_inEditor.deleteTrainComponentByXY(3,1, 5,1)
        self.assertEqual(n-1, TrainComp_inEditor.getNumberOfTrainComponent())

    def test_2_buildingTables(self):
        pass

    def test_5_signalling(self):
        pass        

if __name__ == '__main__':
    unittest.main()