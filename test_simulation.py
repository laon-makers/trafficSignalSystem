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

class Test_SystemMethods(unittest.TestCase):

    # as a tester, I would like to run the simulation to check if there is any show-stopper.
    def test_1_buildingTrack(self):

        ctrl = Control()
        
        ctrl.startTrafficControlSimulation(None)
       
        Log.print("* SwitchingTable Data (train location, train id, arrival time):")
        for i, jc in enumerate(Junction.jcList):
            Log.print(f"    #\t{i+1}")
            for sw in jc.switchingTable:
                Log.print(f"\t({sw.train.initLocation.idX}, {sw.train.initLocation.idY}), {sw.trainId}, {sw.timeRev}")

            #if len(jc.switchingTable) > 1:
            #    self.assertEqual(jc.switchingTable[1].time, jc.switchingTable[0].time + 10)
        
        print("* Train Routing Table:")
        for ix, tr in enumerate(Train.trainList):
            print(f"  * Routing Table #{ix+1} (location, time)")
            for i, rt in enumerate(tr.routingTable):
                print(f"\t({rt.lConnector[0].idX}, {rt.lConnector[0].idY}),\t{tr.arrivalTimeTable[i]}")

       

        print("* Signaling Table:")
        for ix, sg in enumerate(Signal.sigList):
            print(f"  * Signaling Table #{ix+1} (location, time, light <green, red>)")
            print(f"\t({sg.location.idX}, {sg.location.idY}) ===")
            for ix, sgd in enumerate(sg.signalingTable):
                print(f"\t({sgd.time}, <{sgd.bGreenOn},{sgd.bRedOn}>")


    def test_2_simulate4trains(self):        

        # * 4 trains: there were some exceptions at the beginning, but 4 trains arrived their destination.
        # take a look at the Rout #1 in the picture IV.
        ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["i1","d"], ["i3","u"], ["k4","u"]]
        sig = ["g1", "k1", "g3", "m2", "g4", "o3"]
        tr = [["a1","s1"], ["a3","s2"], ["s2","a1"], ["s3","a3"]]

    def test_3_simulate4trains(self):
        # 4 trains: one train at s3, which goes to a4, still failed in building correct route.
        # but all buses eventually made it. Take a look at the Route #2 in the picture IV.
        ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["i1","d"], ["i3","u"], ["k4","u"]]
        sig = ["g1", "k1", "g3", "m2", "g4", "o3"]
        tr = [["a1","s1"], ["a3","s2"], ["s2","a1"], ["s3","a4"]]

    def test_4_simulate5trains(self):
        # * 5 trains: in this 5 train test, only one train at s3, which goes to a4, 
        # failed to building correct route table. Only 2 trains made it. Take a look at the picture #V
        # It works as of May 11, 2023
        ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["i1","d"], ["i3","u"], ["k4","u"]]
        sig = ["g1", "k1", "g3", "m2", "g4", "o3"]
        tr = [["a1","s2"], ["a3","s3"], ["s1","a1"], ["s2","a3"], ["s3","a4"]]

    def test_5_simulate5trains(self):

        # 5 train works
        ts = [["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["a6:i6", "h"], ["M5:S5", "h"], ["M7:S7", "h"], ["i3","u"], ["k4","u"], ["E3", "D"], ["k4", "d"], ["K6", "u" ], ["k6", "d"]]
        sig = ["g3", "m2", "g4", "o3", "i6", "o5"]
        tr = [["a3","s3"], ["s2","a3"], ["s3","a4"], ["a6", "s7"], ["s5", "a6"]]

    def test_6_simulate7trains(self):
        # 7 trains works. refers to the route #1 in the figure IV-4.
        ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["a6:i6", "h"], ["M5:S5", "h"], ["M7:S7", "h"], ["i1","d"], ["i3","u"], ["k4","u"], ["E3", "D"], ["k4", "d"], ["K6", "u" ], ["k6", "d"]]
        sig = ["g1", "k1", "g3", "m2", "g4", "o3", "i6", "o5"]
        tr = [["a1","s2"], ["a3","s3"], ["s1","a1"], ["s2","a3"], ["s3","a4"], ["a6", "s7"], ["s5", "a6"]]



if __name__ == '__main__':
    unittest.main()