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
#from typing import Tuple
from os import write
from utils import Size, TrackSegLayout
from datetime import datetime
from editor import EditorGrid, TsegComp_inEditor, SigComp_inEditor, TrainComp_inEditor, Components
from log import Log, MsgLvl



class CompData:

    compTSeg = []
    compSig = []
    compTrain = []
    
    def __init__(self):
        self.datafile = None

    
    @classmethod
    def SaveComponentDataToFile(cls) -> None:
        
        now = datetime.now()
        fn = ".\data\data_" + now.strftime("%Y%m%d_%H_%M_%S")

        fl = open( fn + ".txt", "a")

        n = 0
        if len(TsegComp_inEditor.tsList) > 0:
            
            msg = "segment::"
            for ts in TsegComp_inEditor.tsList:
                if ts.rOrientation == TrackSegLayout.HORIZONTAL:
                    ort = "H"
                elif ts.rOrientation == TrackSegLayout.UP:
                    ort = "U"
                elif ts.rOrientation == TrackSegLayout.DOWN:
                    ort = "D"
                else:
                    ort = ""
                    print("\tWarning! There are missing orientation in the data.")
                    
                msg += f"{chr(ts.lConnector[0].idX + 0x40)}{ts.lConnector[0].idY} {ort}."
                
            msg = msg[:len(msg)-1]  # to get rid of the last comma
            fl.write(msg)
        else:
                n += 1

        if len(SigComp_inEditor.sigList) > 0:
                msg = "\nsignal::"

                for sg in SigComp_inEditor.sigList:
                    if ts.rOrientation == TrackSegLayout.HORIZONTAL:
                        ort = "H"
                    elif ts.rOrientation == TrackSegLayout.UP:
                        ort = "U"
                    elif ts.rOrientation == TrackSegLayout.DOWN:
                        ort = "D"
                    else:
                        ort = ""
                        print("\tWarning! There are missing orientation in the data.")

                    msg += f"{chr(sg.location.idX + 0x40)}{sg.location.idY}."

                msg = msg[:len(msg)-1]  # to get rid of the last comma
                fl.write(msg)
        else:
                n += 1

        if len(TrainComp_inEditor.trainList) > 0:
            msg = "\ntrain::"
            for tr in TrainComp_inEditor.trainList:
                msg += f"{chr(tr.initLocation.idX + 0x40)}{tr.initLocation.idY} {chr(tr.destination.idX + 0x40)}{tr.destination.idY}."

            msg = msg[:len(msg)-1]  # to get rid of the last comma
            fl.write(msg)
            fl.flush()

        else:
            n += 1


        if n >= 3:
            print("\tNo component data found. Please add data in the Editor mode.")

        fl.close()


    @classmethod
    def loadComponentDataToMemory(cls, fName) -> bool:

        f = None

        try:
            f = open(fName, "r")
        except Exception:
            print( fName + " file not found !!")
            if f != None:
                f.close()

            return False
        
        cls.clearExistingData()

        ln = f.readline()
        
        while len(ln) > 0:                            
            dt = ln.split("::")
            if len(dt) > 1:
                dt[1] = dt[1].replace("\n", "")  # added .replace(...) to get rid of carriage return
                d = dt[1].split(".")
                

                if dt[0] == "segment":
                    for e in d:
                        cls.compTSeg.append(e.strip())

                elif dt[0] == "signal":
                    #d = d.replace(" ", "")   # added .replace(...) to get rid of white spaces
                    for e in d:
                        cls.compSig.append(e.strip())
                elif dt[0] == "train":
                    for e in d:
                        cls.compTrain.append(e.strip())
            ln = f.readline()
            
        f.close()

        return True
        
    @classmethod
    def clearExistingData(cls):
        try:
            for i in reversed(range(len(cls.compTrain))):
                cls.compTrain.pop[i]

            for i in reversed(range(len(cls.compSig))):
                cls.compSig.pop[i]

            for i in reversed(range(len(cls.compTSeg))):
                cls.compTSeg.pop[i]

            for i in reversed(range(len(TsegComp_inEditor.tsList))):
                TsegComp_inEditor.tsList.pop(i)

            for i in reversed(range(len(SigComp_inEditor.sigList))):
                SigComp_inEditor.sigList.pop(i)

            for i in reversed(range(len(TrainComp_inEditor.trainList))):
                TrainComp_inEditor.trainList.pop(i)
        except Exception: 
            Log.printException( traceback.print_exc() )

        
    @classmethod
    def createComponentFromCoordinates(cls, ix, func) -> bool:
        try:
            if ix == 0:
                for ts in cls.compTSeg:
                    dt = ts.split(" ")
                    for s in dt:
                        s = s.strip()

                    func(dt)
            elif ix == 1:
                for sg in cls.compSig:
                    func(sg)
            elif ix == 2:
                for tr in cls.compTrain:
                    dt = tr.split(" ")
                    for s in dt:
                        s = s.strip()

                    func(dt)
        
            return True
        except Exception: 
            Log.printException( traceback.print_exc() )
            return False
        
