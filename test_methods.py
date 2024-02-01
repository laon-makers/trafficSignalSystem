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

    # as a developer, I would like to build a train track and test key methods.
    def test_1_buildingTrack(self):

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

        # test the number of tracks
        self.assertEqual(len(TrackSegment.tsList), 4)
        # test the number of each segment
        self.assertEqual(len(TrackSegment.tsList[0]), 11)
        self.assertEqual(len(TrackSegment.tsList[1]), 5)
        self.assertEqual(len(TrackSegment.tsList[2]), 7)
        self.assertEqual(len(TrackSegment.tsList[3]), 4)

        sg = Signal(7,1)
        self.assertEqual(len(Signal.sigList), 1)
        sg = Signal(11,1)
        self.assertEqual(len(Signal.sigList), 2)
        sg = Signal(13,2)
        self.assertEqual(len(Signal.sigList), 3)
        sg = Signal(9,3)
        self.assertEqual(len(Signal.sigList), 4)
        sg = Signal(11,3)
        self.assertEqual(len(Signal.sigList), 5)


    def test_2_buildingTables(self):
        # Sort the track segment list before invoke any other method.
        TrackSegment.sortTrackSegment()
        ctrl = Control()
        Junction.populateJunctionTable(TrackSegment.tsList)
        # Test the number of junctions.
        self.assertEqual(len(Junction.jcList), 5)        
        Junction.sortJunctionSwitch()


        for i, ts in enumerate(TrackSegment.tsList):
            Log.print(f"Track Id: {i+1}")
            
            Log.print(f"TS id: {ts[i].id}")
            for i2, ts2 in enumerate(ts):
                if i == 0 or i == 2:
                    x = 1 + i2 * Size.locationIdXIncrementStep
                    if i2 >= 5:
                        x -= Size.locationIdXIncrementStep

                elif i == 1:
                    x = 1 + (i2 + 5 ) * Size.locationIdXIncrementStep
                elif i == 3:
                    x = 1 + (i2 + 6 ) * Size.locationIdXIncrementStep

                y = (i  * Size.locationIdYIncrementStep) + 1

                Log.print(f"\t({ts2.lConnector[0].idX},{ts2.lConnector[0].idY}, {ts2.rOrientation})\t({ts2.rConnector[0].idX},{ts2.rConnector[0].idY})", 50)

                # test each track segment's left end x-axis Location Id value(connection value)
                self.assertEqual(ts2.lConnector[0].idX, x)
                # test each track segment's left end y-axis Location Id value(connection value)
                self.assertEqual(ts2.lConnector[0].idY, y)

        # Add 4 train
        #1, 3, 5, 7, 9, 11, 13, 15, 17, 19
        tr = Train(1,1,19,2)
        tr = Train(1,3,19,4)
        tr = Train(19,1,1,1)
        tr = Train(19,2,1,3)

        ctrl.populateRoutingTable()
        
        ln = 10 * Size.locationIdXIncrementStep + 1
        Log.print("** Train Routing Table (loc-left, rOrientation, loc-right):", 50)
        for i, tr in enumerate(Train.trainList):
            Log.print(f"Train Id: {tr.id}")
            for i2, ts in enumerate(tr.routingTable):                
                Log.print(f"\t({ts.lConnector[0].idX},{ts.lConnector[0].idY}, {ts.rOrientation})\t\t({ts.rConnector[0].idX},{ts.rConnector[0].idY})", 50)
                if i == 0:
                    x = 1 + i2 * Size.locationIdXIncrementStep
                    if i2 == 0:
                        y = 1
                    elif i2 == 5:
                        y += Size.locationIdYIncrementStep
                elif i == 1:                    
                    x = 1 + i2 * Size.locationIdXIncrementStep
                    if i2 == 0 or  i2 == 6:
                        y += Size.locationIdYIncrementStep
                elif i == 2:
                    x = ln - (1 + i2) * Size.locationIdXIncrementStep
                    y = 1
                elif i == 3:
                    x = ln - (1 + i2) * Size.locationIdXIncrementStep
                    if i2 == 0 or i2 == 5:
                        y += Size.locationIdYIncrementStep

                self.assertEqual(ts.lConnector[0].idX, x)
                self.assertEqual(ts.lConnector[0].idY, y)

            

            
            self.assertEqual(len(tr.routingTable), 10)

        for i, tr in enumerate(Train.trainList):
            #Log.print(f"Train arrival time in each tack segment: Train #{i+1}")
            for i2, tt in enumerate(tr.arrivalTimeTable):
                t = tr.travelTimePerSegment * i2
                #Log.print(f"\t({tt})")
                self.assertEqual(tt, t)

        Control.populateSwitchingTable()

        Log.print("* Junction Switching Table (train ID, TS ID, train arrival time, signal ID):")
        for i, jc in enumerate(Junction.jcList):
            Log.print(f"    #{i+1}")
            for st in jc.switchingTable:

                for i3, ts in enumerate(st.train.routingTable):
                    if ts.id == st.segment.id:
                        Log.print(f"\t{st.train.id}, {st.segment.id}, {st.train.arrivalTimeTable[i3]}, {st.signal}")
                        Log.print(f"\tx,y: ({st.segment.lConnector[0].idX}, {st.segment.lConnector[0].idY})")
                        
                        # track segment info in both the train and the segment for the given junction
                        # must be same values.
                        self.assertEqual(st.train.routingTable[i3].id, st.segment.id)


    def test_5_signalling(self):

        
    
        Signal.signalScheduling()
        ctrl = Control()
        #ctrl.startTrafficControlSimulation(None)

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

if __name__ == '__main__':
    unittest.main()