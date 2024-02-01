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
import traceback, time
from os import system
from utils import Size, TrackSegLayout, EditorMode
from utils import Util, MsgLvl, Result
from log import Log
from control import Control
from editor import TsegComp_inEditor, SigComp_inEditor, TrainComp_inEditor, Components
from data import CompData
from plot import Display
from component import Sif

class Menu:
    '''
    '''

    def __init__(self):
        self.data = None
        self.trafficSysMap = None
        self.bEnDebugCommand = False
        self.control = Control()

    def consoleMenuSim(self):

        r = Result.OK

        try:
            self.data = Components()
            self.data.trackSeg = TsegComp_inEditor.tsList
            self.data.signal = SigComp_inEditor.sigList
            self.data.train = TrainComp_inEditor.trainList
            
            opts = []   
            
            ix = 0
            #system("cls")
            Util.PrintInitMsgForConsoleMenu()
                
            log = ""
            inMsg = "* Please type a command (without quotation mark) and press enter key: "

            bEditorMode = False
            bSimPaused = False

            while True:
                k = ""   # to clear
                arg = "" # to clear
                
                del opts
                opts = []
                
                k = input(inMsg)
                
                #system("cls")

                if len(k) == 0:
                    print("\n\t No key found!!")
                    continue
                    
                
                if k == '-e' or k == 'exit': # exit the simulator.
                    r = Result.OK
                    print("\n\t Thank you...\n")
                    break                    
                elif k == '-h' or k == 'h' or k == "help":
                    Util.PrintConsoleMenu()
                    #Util.PrintEditorCommandHelp()
                    
                    print("\n* type a command and hit the enter key: ")
                    continue
                
                elif k == 'ed' or k == 'edit':
                        bEditorMode = True

                elif k == 'init':
                    if self.control == None:
                        self.control = Control()
                    self.control.reInitSimulation()

                elif k == 'sim' or k == 'start':
                    tmpK = k
                    k = input("Do you want to use your own traffic layout? (y/n):")
                    
                    # if self.control == None:
                    #     self.control = Control()
                    
                    if k == 'Y' or k == 'y':
                        b = True
                        if len(self.data.trackSeg) <= 0:
                            print("\t\tTract Segment components are missing!")
                            b = False
                        if len(self.data.signal) <= 0:
                            print("\t\tSignal components are missing!")
                            b = False
                        if len(self.data.train) <= 0:
                            print("\t\tTrain components are missing!")
                            b = False

                        if b == True:
                            self.beginSimulation(self.data, False, True)

                            r = Result.END_SIM # terminate request.
                            print("\n\t Thank you...\n")
                            break
                        else:
                            print("\n\tUnable to start the simulation because there are no traffic network data.")
                            print("\tPlease build your own traffic system network. You can get started by typing 'ed' for bringing up the editor.\n")
                    else:
                        self.beginSimulation(None)
                        r = Result.END_SIM # terminate request.
                        print("\n\t Thank you...\n")
                        break
                elif k == "run":
                        if self.bEnDebugCommand == True:
                            if bSimPaused == False:
                                bSimPaused = True
                                self.buildDefaultTrafficNetwork()

                            self.listComponents(10)

                            if self.trafficSysMap == None:
                                self.trafficSysMap = Display(Size.canvasWidth, Size.canvasHeight, TsegComp_inEditor.tsList, SigComp_inEditor.sigList, TrainComp_inEditor.trainList, None, True)
                                self.trafficSysMap.start()

                            Display.bSimulating = True

                elif k == "xy":
                        if self.bEnDebugCommand == True:
                            k = input("Type x1 y1 x2 y2 1/0?:")
                            val = k.split(" ")
                            if val[4] == "0":
                                bRedraw = False
                            else:
                                bRedraw = True
                                
                            self.trafficSysMap.updateXyVal(int(val[0]), int(val[1]), int(val[2]) ,int(val[3]), bRedraw)
                elif k == "kill":
                        #self.trafficSysMap.killDrawWIndow()
                        self.trafficSysMap.sendEvent()
                elif k.find("net") == 0:
                        
                        if bSimPaused == False:
                            bSimPaused = True

                            if k == "net" or k == "network":
                                k += " 0"

                            self.runSimDemo(k.split(" "))
                        
                        if self.listComponents(10) == False:
                            r = Result.EXIT_REQUEST # terminate request.
                            break

                        tmpK = k
                        k = input("\nDo you want to run the simulation with this network? (y/n):")
                    
                        if k == 'Y' or k == 'y':                            
                            #self.trafficSysMap.sendEvent()
                            #self.trafficSysMap = None
                            print("\nWait for a moment while flushing out memory buffer...\n")

                            self.beginSimulation(self.data, False, False, 1)

                            r = Result.END_SIM # terminate request.
                            print("\n\t Thank you...\n")
                            break
                        else:
                            bSimPaused = True
                            print("\n\n")

                        k = tmpK

                elif k == 'simn':
                    if self.bEnDebugCommand == True:
                        self.beginSimulation(None)

                        r = Result.END_SIM # terminate request.
                        print("\n\t Thank you...\n")
                        break

                elif k == 'simy' or k == 's' :
                    if self.bEnDebugCommand == True:
                        self.buildDefaultTrafficNetwork_2()                    
                        #self.listComponents(10)
                        self.beginSimulation(self.data, False, True)
                        #r = Result.END_SIM # terminate request.
                        #print("\n\t Thank you...\n")
                        #break

                elif k == 'test1':
                    tmpK = k
                    self.beginSimulation(None)
                    r = Result.END_SIM # terminate request.
                    print("\n\t Thank you...\n")
                    break
                elif k == 'test2':
                    tmpK = k
                    
                    if bSimPaused == False:
                        self.buildDefaultTrafficNetwork()
                    
                    # self.listComponents(10)
                    # k = input("Please check the component list above and click 'y' if correct: (y/n):")                    
                    # if k == 'Y' or k == 'y':
                    self.beginSimulation(self.data, False, True)
                    r = Result.END_SIM # terminate request.
                    print("\n\t Thank you...\n")
                    break
                    # else:
                    #     bSimPaused = True
                    #     print("\n\n")

                    k = tmpK

                elif  k == 'build':
                    if self.bEnDebugCommand == True:
                        self.buildDefaultTrafficNetwork()
                        
                        #self.listComponents(10)
                        self.beginSimulation(self.data, False, True)
                        r = Result.END_SIM # terminate request.
                        print("\n\t Thank you...\n")
                        break

                elif k == 'test3' or k == 't':
                    if self.bEnDebugCommand == True:
                        if bSimPaused == False:
                            self.buildDefaultTrafficNetwork_2()

                        #self.listComponents(10)
                        # k = input("Please check the component list above and click 'y' if correct: (y/n):")
                        # if k == 'Y' or k == 'y':
                        self.beginSimulation(self.data, False, True)
                        r = Result.END_SIM # terminate request.
                        print("\n\t Thank you...\n")
                        break
                        # else:
                        #     bSimPaused = True
                        #     print("\n\n")

                elif k.find("tst") == 0 or k.find("test") == 0 or k.find("demo") == 0:
                        
                    if bSimPaused == False:
                        bSimPaused = True

                        self.runSimDemo(k.split(" "))
                    
                    #self.listComponents(10)

                    #self.beginSimulation(self.data, False, True)
                    self.beginSimulation(self.data, False, False)
                    r = Result.END_SIM # terminate request.
                    print("\n\t Thank you...\n")
                    break

                elif k.find("d") == 0:
                    if self.bEnDebugCommand == True:
                        opts = ("demo", k[1:])
                        self.runSimDemo(opts)
                    
                        #self.listComponents(10)

                        #self.beginSimulation(self.data, False, True)
                        self.beginSimulation(self.data, False, False)
                        r = Result.END_SIM # terminate request.
                        print("\n\t Thank you...\n")
                        break

                elif k.find("speed") == 0:
                    opts = k.split(" ")
                    if len(opts) > 1:
                        Sif.setTrainSpeedDelay(opts[1])
                    else:
                        print("\tMissing argument! The command should be, e.g., 'delay 1'")

                elif k.find("timeout") == 0:
                    opts = k.split(" ")
                    if len(opts) > 1:
                        Sif.setSimulationTimeoutStep(opts[1])
                    else:
                        print("\tMissing argument! The command should be, e.g., 'timeout 150'")

                elif k == 'save':
                    k = input("Do you want to save component file into 'data' folder? (y/n):")
                    if k == 'Y' or k == 'y':
                        CompData.SaveComponentDataToFile()

                elif k.find('load') == 0:
                    fn = k.strip()
                    fn = fn[5:]

                    if len(fn) <= 0:
                        k = input("Please type the txt file name (no file extension) in the 'data' folder:")
                        fn = k

                    fn = f".\data\{fn}.txt"

                    if( CompData.loadComponentDataToMemory(fn) == True):
                        CompData.createComponentFromCoordinates(0, self.addOrDeleteTrackSegParam)
                        CompData.createComponentFromCoordinates(1, self.addOrDeleteSignalParam)
                        CompData.createComponentFromCoordinates(2, self.addOrDeleteTrainParam)
                        self.listComponents(10)

                elif k.find("jc") == 0:
                    if self.bEnDebugCommand == True:
                        #opts = k.split(" ")

                        if self.isTrafficSimDisplayLive() == True:
                            if self.trafficSysMap == None:
                                Display.bSimulating = False
                                self.trafficSysMap = Display.trafficNetworkDspObject
                            self.trafficSysMap.debugCommand(k)
                        else:
                            if self.control == None:                                
                                self.control = Control()
                            opts = k.split(" ")
                            cmd = "demo" 
                            if opts[1] == "open":
                                if len(opts) > 2:
                                    cmd += " " + opts[2]
                            
                            self.runSimDemo(cmd.split(" "))
                            self.control.reInitSimulation(self.data)
                            #print("Missing component! Please load a data to the system")
                else:
                    if k.find(' ') > 0:
                        opts = k.split(' ')
                        arg = "-" + opts[0]
                        opts.remove(opts[0]) # remove the first argument.
                    else:
                        arg = "-" + k


                if bEditorMode == True:
                    if self.trafficSystemEditor() == Result.END_SIM:
                        print("\n\t Exiting Main Menu...\n")
                        break

                    bEditorMode = False


            #}  End of 'while'
                    
        except Exception:
            Log.printException( traceback.print_exc() )
            r = Result.EXCEPTION
            
        #finally:
        #    # --- Cleanup on exit ---        
        #    print("\n\n\t Exiting the application !!!")        
        #    time.sleep(1)
        
        if self.isTrafficSimDisplayLive() == True:
            if self.trafficSysMap != None:
            
                if r == Result.END_SIM:
                    k = input("Press any key to close the graphic window !")

                    #if k == "y" or k == "Y":
                    self.trafficSysMap.sendEvent()            
                    time.sleep(1)
                else:
                    self.trafficSysMap.sendEvent()
                    time.sleep(1)

            else:

                if r == Result.END_SIM:
                    k = input("Press any key to close the graphic window !")

                try:
                    Display.emergencyKill()
                except Exception:
                    # this exception can be ignored.
                    Log.printException( "" )

        return r
    





    def trafficSystemEditor(self):

        r = Result.OK

        try:
            print("\n\n\t Entering to Track Editor Mode...\n")
            Util.PrintInitMsgForTrackEditorMenu()

            opts = []   

            ix = 0
        
            log = ""
            inMsg = "\n\t[ EDIT Mode ]\n* Please type one of 'ts', 'sg' and 'tr' and press enter key: "

            editorMode = EditorMode.EDIT_MD
            bWaitingValue = False
            bAddReq = False
            bSimPaused = False

            self.listComponents(10, True)

            while True:
                k = ""   # to clear
                arg = "" # to clear
                
                del opts
                opts = []
                
                k = input(inMsg)
                
                system("cls")
                if len(k) == 0:
                    print("\n\t No key found!!")
                    continue
                    
                
                if k == '-e':
                    print("\n\n\tExiting the Editor Mode...\n")
                    break
                elif k == '-ts':
                    if editorMode == EditorMode.EDIT_MD:
                        self.listComponents(10, True)

                    editorMode = EditorMode.TRACK_SEG_EDIT_MD
                    bWaitingValue = False
                    bAddReq = False
                    #print("\n* type a grid coordinate and orientation of the right end.\
                    #       \n    e.g.: 'A1 up' where 'A1' is the coordinate and 'up' ")                    
                    
                elif k == '-sg':
                    if editorMode == EditorMode.EDIT_MD:
                        self.listComponents(10, True)
                    editorMode = EditorMode.SIGNAL_EDIT_MD
                    bWaitingValue = False
                    bAddReq = False

                elif k == '-tr':
                    if editorMode == EditorMode.EDIT_MD:
                        self.listComponents(10, True)
                    editorMode = EditorMode.TRAIN_EDIT_MD
                    bWaitingValue = False
                    bAddReq = False
                    
                elif k == '-h' or k == 'h' or k == 'help':
                    Util.PrintEditorHelp()
                    print("\n* type a command and hit the enter key: ")
                    continue

                elif k == 'sim' or k == 'start':
                        tmpK = k
                        k = input("Do you want to use your own traffic layout? (y/n):")
                        # if self.console == None:
                        #     self.control = Control()
                        if k == 'Y' or k == 'y':
                            b = True
                            if len(self.data.trackSeg) <= 0:
                                print("\t\tTract Segment components are missing!")
                                b = False
                            if len(self.data.signal) <= 0:
                                print("\t\tSignal components are missing!")
                                b = False
                            if len(self.data.train) <= 0:
                                print("\t\tTrain components are missing!")
                                b = False

                            if b == True:
                                self.beginSimulation(self.data)
                                r = Result.END_SIM # terminate request.
                                print("\n\t Thank you...\n")
                                break
                            else:
                                print("\tUnable to start the simulation because there are no traffic network data.")
                                print("\tPlease build your own traffic system network. You can get started by typing 'ed' for bringing up the editor.\n")
                        else:
                            self.beginSimulation(None)
                            r = Result.END_SIM # terminate request.
                            print("\n\t Thank you...\n")
                            break

                elif k == 'simno':
                        if self.bEnDebugCommand == True:
                            self.beginSimulation(None)
                            print("\n\t Thank you...\n")
                            r = Result.END_SIM # terminate request.
                            break
                elif k == 'test1':
                        tmpK = k
                        self.beginSimulation(None)
                        r = Result.END_SIM # terminate request.
                        print("\n\t Thank you...\n")
                        break
                elif k == 'test2':
                        tmpK = k
                        if bSimPaused == False:
                            self.buildDefaultTrafficNetwork()

                        #self.listComponents(10)
                        
                        # k = input("Please check the component list above and click 'y' if correct: (y/n):")
                        # if k == 'Y' or k == 'y':
                        self.beginSimulation(self.data, False, True)
                        r = Result.END_SIM # terminate request.
                        print("\n\t Thank you...\n")
                        break
                        # else:
                        #     bSimPaused = True
                        #     print("\n\n")

                        k = tmpK
                        
                elif k == 'test3':
                        tmpK = k

                        if bSimPaused == False:
                            self.buildDefaultTrafficNetwork_2()

                        #self.listComponents(10)
                        
                        # k = input("Please check the component list above and click 'y' if correct: (y/n):")
                        # if k == 'Y' or k == 'y':
                        self.beginSimulation(self.data, False, True)
                        r = Result.END_SIM # terminate request.
                        print("\n\t Thank you...\n")
                        break
                        # else:
                        #     bSimPaused = True
                        #     print("\n\n")
                        
                        k = tmpK

                elif k.find("speed") == 0:
                    opts = k.split(" ")
                    if len(opts) > 1:
                        Sif.setTrainSpeedDelay(opts[1])
                    else:
                        print("\tMissing argument! The command should be, e.g., 'delay 1'")

                elif k.find("timeout") == 0:
                    opts = k.split(" ")
                    if len(opts) > 1:
                        Sif.setSimulationTimeoutStep(opts[1])
                    else:
                        print("\tMissing argument! The command should be, e.g., 'timeout 150'")
                        
                elif k == 'save':
                        k = input("Do you want to save component file into 'data' folder? (y/n):")
                        if k == 'Y' or k == 'y':
                            CompData.SaveComponentDataToFile()

                elif k.find('load') == 0:
                    fn = k.strip()
                    fn = fn[5:]

                    if len(fn) <= 0:
                        k = input("Please type the txt file name (no file extension) in the 'data' folder:")
                        fn = k

                    fn = f".\data\{fn}.txt"

                    if( CompData.loadComponentDataToMemory(fn) == True):
                        CompData.createComponentFromCoordinates(0, self.addOrDeleteTrackSegParam)
                        CompData.createComponentFromCoordinates(1, self.addOrDeleteSignalParam)
                        CompData.createComponentFromCoordinates(2, self.addOrDeleteTrainParam)
                        self.listComponents(10)

                elif (k == 'r') or (k == 'return'): # return to home menu
                    self.trafficSysMap.sendEvent()
                    r = Result.OK
                    break
                elif (k == 'q') or (k == 'exit'): # exit the simulator.
                    if k == 'q':
                            r = Result.OK
                    else: 
                        r = Result.EXIT_REQUEST # terminate request.
                    self.trafficSysMap.sendEvent()

                    print("\n\n\tExiting the Editor Mode...\n")
                    break

                elif k.find("tst") == 0 or k.find("test") == 0 or k.find("demo") == 0:
                        
                    if bSimPaused == False:
                        bSimPaused = True

                        self.runSimDemo(k.split(" "))
                    
                    self.beginSimulation(self.data, False, True)
                    r = Result.END_SIM # terminate request.
                    print("\n\t Thank you...\n")
                    break
                
                elif k == 'n' or k == 'new':
                    if editorMode != EditorMode.EDIT_MD:
                        #self.listComponents(10, True)
                        if self.isTrafficSimDisplayLive() == True:
                            self.trafficSysMap.sendEvent()

                    editorMode = EditorMode.EDIT_MD
                    bWaitingValue = False
                    bAddReq = False

                elif k == 'ts':
                    if editorMode == EditorMode.EDIT_MD:
                        self.listComponents(10, True)
                    editorMode = EditorMode.TRACK_SEG_EDIT_MD
                    bWaitingValue = False
                    bAddReq = True
                        
                elif k == 'sg' or k == 'sig':
                    if editorMode == EditorMode.EDIT_MD:
                        self.listComponents(10, True)
                    editorMode = EditorMode.SIGNAL_EDIT_MD
                    bWaitingValue = False
                    bAddReq = True

                elif k == 'tr':
                    if editorMode == EditorMode.EDIT_MD:
                        self.listComponents(10, True)
                    editorMode = EditorMode.TRAIN_EDIT_MD
                    bWaitingValue = False
                    bAddReq = True

                elif k == 'lts':
                    self.listComponents(1)
                    continue

                elif k == 'lsg':
                    self.listComponents(2)
                    continue

                elif k == 'ltr':
                    self.listComponents(3)
                    continue

                elif k == 'la' or k == 'lal' or k == 'lall':
                    self.listComponents(10)
                    continue

                elif k == 'ed' or k == 'edit':
                    print("\n\t* You are in the Editor mode already!")

                else:
                    if k.find(' ') > 0:
                        opts = k.split(' ')
                        arg = "-" + opts[0]
                        #opts.remove(opts[0]) # remove the first argument.
                    else:
                        arg = "-" + k


                if editorMode == EditorMode.TRACK_SEG_EDIT_MD:
                    if bWaitingValue == False:
                        if bAddReq == True:
                            inMsg = "\n\t[ Track Segment ADD Mode ]\n"
                        else:
                            inMsg = "\n\t[ Track Segment DELETE Mode ]\n"
                        inMsg += "* Please type both coordinate and orientation, e.g. 'a1 u', and press enter key: "
                        bWaitingValue = True
                    else:
                        self.addOrDeleteTrackSegParam(opts, bAddReq)
                        self.listComponents(10, True)

                elif editorMode == EditorMode.SIGNAL_EDIT_MD:
                    if bWaitingValue == False:
                        if bAddReq == True:
                            inMsg = "\n\t[ Signal ADD Mode ]\n"
                        else:
                            inMsg = "\n\t[ Signal DELETE Mode ]\n"

                        inMsg += "* Please type both coordinate and orientation, e.g. 'c3', and press enter key: "
                    else:
                        self.addOrDeleteSignalParam(k, bAddReq)
                        self.listComponents(10, True)
                        
                    bWaitingValue = True
                elif editorMode == EditorMode.TRAIN_EDIT_MD:
                    if bWaitingValue == False:
                        if bAddReq == True:
                            inMsg = "\n\t[ Train ADD Mode ]\n"
                        else:
                            inMsg = "\n\t[ Train DELETE Mode ]\n"
                        inMsg += "* Please type train's initial location coordinate and destination , e.g. 'a1 b3', and press enter key: "
                    else:
                        self.addOrDeleteTrainParam(opts, bAddReq)
                        self.listComponents(10, True)
                    bWaitingValue = True
                else:
                    inMsg = "\n\t[ EDIT Mode ]\n* Please type a command and press enter key: "
                    #bWaitingValue = False
        
        except Exception:
            Log.printException( traceback.print_exc() )

        return r
    

    def runSimDemo(self, opts):
        if len(opts) > 1:
        
            cmd = "0"
            if opts[0] == "tst" or opts[0] == "test" or opts[0] == "net" or opts[0] == "network":
                cmd = opts[1]
            elif opts[0] == "demo":
                
                if opts[1] == "1":
                    cmd = "1"
                elif opts[1] == "2":
                    cmd = "4"
                elif opts[1] == "3":
                    cmd = "5"
                elif opts[1] == "4":
                    cmd = "6"
                else:
                    cmd = "0"

            if cmd == "0":
                self.buildDefaultTrafficNetwork()
            elif cmd == "1":
                self.buildDefaultTrafficNetwork_2(1)
            elif cmd == "2":
                self.buildDefaultTrafficNetwork_2(2)
            elif cmd == "3":
                self.buildDefaultTrafficNetwork_2(3)
            elif cmd == "4":
                self.buildDefaultTrafficNetwork_2(4)
            elif cmd == "5":
                self.buildDefaultTrafficNetwork_2(5)
            elif cmd == "6":
                self.buildDefaultTrafficNetwork_2(6)
            elif cmd == "7":
                self.buildDefaultTrafficNetwork_2(7)
            elif cmd == "8":
                self.buildDefaultTrafficNetwork_2(8)


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

        ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:i3","h"], ["m4:s4","h"], ["i1","d"], ["i3","u"], ["k3","d"]]
        sig = ["g1", "k1", "m2", "i3", "k3"]
        tr = [["a1","s2"], ["a3","s4"], ["s1","a1"], ["s2","a3"]]

        for s in ts:
            o = self.addOrDeleteTrackSegParam(s, True, True)
        for sg in sig:
            o = self.addOrDeleteSignalParam(sg, True, True)
        for r in tr:
            o = self.addOrDeleteTrainParam(r, True, True)


    def buildDefaultTrafficNetwork_2(self, ix=4):

        if ix == 1:
            # * 5 trains: in this 5 train test, only one train at s3, which goes to a4, 
            # failed to building correct route table. Only 2 trains made it. Take a look at the picture #V
            # It works as of May 11, 2023        
            ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["i1","d"], ["i3","u"], ["k4","u"]]
            sig = ["g1", "k1", "g3", "m2", "g4", "o3"]
            tr = [["a1","s2"], ["a3","s3"], ["s1","a1"], ["s2","a3"], ["s3","a4"]]
        
        elif ix == 2:

            # * 4 trains: there were some exceptions at the beginning, but 4 trains arrived their destination.
            # take a look at the Rout #1 in the picture IV.
            ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["i1","d"], ["i3","u"], ["k4","u"]]
            sig = ["g1", "k1", "g3", "m2", "g4", "o3"]
            tr = [["a1","s1"], ["a3","s2"], ["s2","a1"], ["s3","a3"]]
        
        elif ix == 3:
            # 4 trains: one train at s3, which goes to a4, still failed in building correct route.
            # but all buses eventually made it. Take a look at the Route #2 in the picture IV.
            ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["i1","d"], ["i3","u"], ["k4","u"]]
            sig = ["g1", "k1", "g3", "m2", "g4", "o3"]
            tr = [["a1","s1"], ["a3","s2"], ["s2","a1"], ["s3","a4"]]

        elif ix == 4:

            # 5 train works
            ts = [["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["a6:i6", "h"], ["M5:S5", "h"], ["M7:S7", "h"], ["i3","u"], ["k4","u"], ["E3", "D"], ["k4", "d"], ["K6", "u" ], ["k6", "d"]]
            sig = ["g3", "m2", "g4", "o3", "i6", "o5"]
            tr = [["a3","s3"], ["s2","a3"], ["s3","a4"], ["a6", "s7"], ["s5", "a6"]]

        elif ix == 5:
            # 7 trains works. refers to the route #1 in the figure V-4.
            ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["a6:i6", "h"], ["M5:S5", "h"], ["M7:S7", "h"], ["i1","d"], ["i3","u"], ["k4","u"], ["E3", "D"], ["k4", "d"], ["K6", "u" ], ["k6", "d"]]
            sig = ["g1", "k1", "g3", "m2", "g4", "o3", "i6", "o5"]
            tr = [["a1","s2"], ["a3","s3"], ["s1","a1"], ["s2","a3"], ["s3","a4"], ["a6", "s7"], ["s5", "a6"]]

        elif ix == 6:
            # 8 trains works.
            ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["a6:i6", "h"], ["M5:S5", "h"], ["I7:S7", "h"], ["A8:S8", "h"], ["i1","d"], ["i3","u"], ["k4","u"], ["E3", "D"], ["k4", "d"], ["K6", "u" ], ["k6", "d"], ["G8", "u"]]
            sig = ["g1", "k1", "g3", "m2", "g4", "o3", "i6", "o5", "o7", "i7", "e8"]
            tr = [["a1","s2"], ["a3","s3"], ["s1","a1"], ["s2","a3"], ["s3","a4"], ["a6", "s7"], ["s5", "a6"], ["s7", "A8"]]

        elif ix == 7:
            # 9 trains works. It works.
            ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["a6:O6", "h"], ["M5:S5", "h"], ["G7:S7", "h"], ["A8:S8", "h"], ["i1","d"], ["i3","u"], ["k4","u"], ["E3", "D"], ["k4", "d"], ["K6", "u" ], ["M6", "d"], ["I8", "u"], ["o8", "u"]]
            sig = ["g1", "k1", "g3", "m2", "g4", "o3", "i6", "o5", "o7", "i7", "e8", "k8"]
            tr = [["a1","s2"], ["a3","s3"], ["s1","a1"], ["s2","a3"], ["s3","a4"], ["a6", "o6"], ["s5", "a6"], ["s7", "g7"], ["a8", "s7"]]

        # elif ix == 8:
        #     # 9 trains works. It isn't working yet. it is because train at track 8 wants to go to track 7 while the other one in track 7 want to go to track 8. It hasn't been resolved yet.
        #     ts = [["a1:s1","h"], ["k2:s2","h"], ["a3:s3","h"], ["a4:i4","h"], ["a6:O6", "h"], ["M5:S5", "h"], ["G7:S7", "h"], ["A8:S8", "h"], ["i1","d"], ["i3","u"], ["k4","u"], ["E3", "D"], ["k4", "d"], ["K6", "u" ], ["M6", "d"], ["I8", "u"], ["o8", "u"]]
        #     sig = ["g1", "k1", "g3", "m2", "g4", "o3", "i6", "o5", "e6", "o7", "i7", "e8", "k8"]
        #     tr = [["a1","s2"], ["a3","s3"], ["s1","a1"], ["s2","a3"], ["s3","a4"], ["a6", "s7"], ["s5", "a6"], ["s7", "A8"], ["a8", "s7"]]


        for s in ts:
            o = self.addOrDeleteTrackSegParam(s, True, True)
        for sg in sig:
            o = self.addOrDeleteSignalParam(sg, True, True)
        for r in tr:
            o = self.addOrDeleteTrainParam(r, True, True)
            
        
    def addOrDeleteTrackSegParam(self, opts, bAdd=True, bSilent=False):
        if len(opts) > 1:
            try:
                if len(opts) > 1:
                    if bSilent == False:
                        print(f"({opts[0]} {opts[1]})")
                elif bSilent == False:
                    print(f"({opts[0]})")
                opt2 = opts[0].split(':')
                
                failCnt = 0
                
                bMulti = False
                if len(opt2) > 1:
                    bMulti = True

                x1 = y1 = x2 = y2 = 0

                for val in opt2:

                    if bSilent == False:
                        print(f"({val})")

                    val = val.strip()

                    v = val[:1]
                    x = self.convertStringCoordinateToValue(v, True)

                    if x == -2 or x == -4:
                        print(f"\n\t The column value '{val}' is out of range or wrong character.")
                        print(f"\ttEvery other alphabet which is A, C, E, G, I, K, M, O, Q, S, U, V, Y is available.")
                        failCnt += 1

                    elif x > 0 and x <= Size.numTrackGridX:

                        if x1 == 0:
                            x1 = x
                        else:
                            x2 = x

                        v = val[1:]
                        y = self.convertStringCoordinateToValue(v, False)                        

                        if y <= 0 or y > Size.numTrackGridY:
                            failCnt += 1
                            print(f"\n\t The row value '{val}' is out of range or wrong character. try with a number smaller then {self.numTrackGridY}.")
                        else:
                            if y1 == 0:
                                y1 = y
                            else:
                                y2 = y

                if bMulti == True or failCnt == 0:

                    v = opts[1]
                    if v == 'u' or v == 'U':
                        ort = TrackSegLayout.UP
                    elif v == 'd' or v == 'D':
                        ort = TrackSegLayout.DOWN
                    elif v == 'h' or v == 'H':
                        ort = TrackSegLayout.HORIZONTAL
                    else:
                        ort = None
                        print("\n\t Wrong orientation character. It must be one of 'u', 'd', 'h'.")
                        failCnt += 1

                    if ort != None:
                        if bAdd == True:
                            ts = TsegComp_inEditor(x1, y1, ort)
                            if ts.bValid == False:
                                del ts
                                print(f"\t Failed in adding the track segment.\n\t There seems to be another component at the coordinate already or check if there is any typo!  ({chr(x1 + 0x40)}{str(y1)})")
                                failCnt += 1
                            elif bMulti == False:
                                if bSilent == False:
                                    print("\tDone!", end='')

                            elif x2 <= Size.numTrackGridX:
                                ts = TsegComp_inEditor(x2, y2, ort)
                                if ts.bValid == False:
                                    del ts
                                    print("\t Failed in adding the track segment.\n\t There seems to be another component at the coordinate already or check if there is any typo!")
                                    failCnt += 1

                        else:
                            if TsegComp_inEditor.deleteTrackSegComponentByXY(x, y, ort) == True:
                                if bSilent == False:
                                    if bMulti == False:
                                        print("\tDone!", end='')
                            else:
                                if bMulti == False:
                                    print("\tFailed!", end='')

                            
                        #editorMode == EditorMode.EDIT_MD
                        #bWaitingValue = False

                        if bMulti == True and failCnt == 0:
                            if ort == TrackSegLayout.HORIZONTAL:
                                if y1 == y2:
                                    #x = x1
                                    
                                    for i in range(x1+Size.locationIdXIncrementStep, x2, Size.locationIdXIncrementStep):

                                        if i < Size.numTrackGridX:
                                            y2 = 0x40 + i
                                            arg = f"{chr(y2)}{y1}"

                                            if bSilent == False:                                            
                                                print("\t" + arg, "H")

                                            self.addOrDeleteTrackSegParam( [arg, "H"], bAdd, bSilent)
                                            #self.addOrDeleteTrackSegParam( [f"{str(y2)}{y1}", "H"], bAdd)
                                        else:
                                            #y2 = 0x40 + i
                                            print(f"\tFailed! Out of range. ({chr(y2)}{str(y1)} H)")
                                            break
                                else:
                                    print("\t Failed in adding multiple segments.\n\t Adding multiple segments are allowed for the same horizontal tracks!")
                            else:
                                print("\t Failed in adding multiple segments.\n\t Adding multiple segments are allowed for the 'H' option!")
                        
                else:
                    print("\tFailed!", end='')
            except Exception:
                Log.printException( traceback.print_exc() )


    def convertStringCoordinateToValue(self, val, bAlpha) -> int:
        '''
        bAlpha: 
            True:   convert alphabet to an integer.
            False:  convert a number string to an integer

        '''
        
        v = -1

        try:
            if bAlpha == True:
                v = ord(val)

                if v > 0x40 and v < 0x5B:
                    v -= 0x40
                elif v > 0x60 and v < 0x7B:
                    v -= 0x60
                else:
                    v = -2

                    if v < 0 or v > Size.numTrackGridX:
                        v = -3

                if v > 0:
                    if v % 2 == 0:
                        v = -4   # only A, C, E, G, I, K, M, O, Q, S, U, V, Y are available.
            
            else:
                v = int(val)

        except Exception:
            Log.printException( traceback.print_exc() )

        return v


    def addOrDeleteSignalParam(self, arg, bAdd=True, bSilent=False):
        if len(arg) > 0:
            try:
                v = arg[:1]
                x = ord(v)
                if x > 0x40 and x < 0x5B:
                    x -= 0x40
                elif x > 0x60 and x < 0x7B:
                    x -= 0x60
                else:
                    x = 1000
                    print("\n\t column value is out of range or wrong character. type one of 'a' to 't'.")

                if x <= Size.numTrackGridX:
                    v = arg[1:]
                    y = int(v)

                    if y > 0 and y <= Size.numTrackGridX:
                        if bAdd == True:
                            sg = SigComp_inEditor(x, y)
                            if sg.bValid == False:
                                del sg
                                print("\t Failed in adding the signal!\n\t There seems to be no segment where the signal be installed or\n\t another component at the coordinate already, otherwise check if there is any typo.")
                            elif bSilent == False:
                                print("\t\tDone!", end='')
                        else:
                            if SigComp_inEditor.deleteSignalComponentByXY(x, y) == True:
                                if bSilent == False:                            
                                    print("\t\tDone!", end='')
                            else:
                                print("\t\tFailed!", end='')

                    else:
                        print("\n\t row value is out of range or wrong number. try with smaller number.")
                else:
                    print("\tFailed! Out of range !", end='')
            except Exception:
                Log.printException( traceback.print_exc() )

    def addOrDeleteTrainParam(self, opts, bAdd=True, bSilent=False):
        if len(opts) > 1:
            try:
                v = opts[0][:1]
                x = ord(v)
                if x > 0x40 and x < 0x5B:
                    x -= 0x40
                elif x > 0x60 and x < 0x7B:
                    x -= 0x60
                else:
                    x = 1000
                    print("\n\t column value is out of range or wrong character. type one of 'a' to 't'.")

                if x <= Size.numTrackGridX:
                    v = opts[0][1:]
                    y = int(v)

                    if y > 0 and y <= Size.numTrackGridX:

                        v = opts[1][:1]
                        x2 = ord(v)
                        if x2 > 0x40 and x2 < 0x5B:
                            x2 -= 0x40
                        elif x2 > 0x60 and x2 < 0x7B:
                            x2 -= 0x60
                        else:
                            x = 1000
                            print("\n\t destination column value is out of range or wrong character. type one of 'a' to 't'.")

                        if x2 <= Size.numTrackGridX:
                            v = opts[1][1:]
                            y2 = int(v)

                            if y2 > 0 and y2 <= Size.numTrackGridX:

                                if bAdd == True:
                                    tr = TrainComp_inEditor(x, y, x2, y2)
                                    if tr.bValid == False:
                                        del tr
                                        print("\t Failed in adding the train!\n\t There seems to be another component at the coordinate already or check if there is any typo.")
                                    elif bSilent == False:
                                        print("\t\tDone!", end='')
                                else:
                                    if TrainComp_inEditor.deleteTrainComponentByXY(x,y, x2,y2) == True:
                                        if bSilent == False:
                                            print("\t\tDone!", end='')
                                    else:
                                        print("\t\tFailed!", end='')
                                    

                                #editorMode == EditorMode.EDIT_MD
                                #bWaitingValue = False
                            else:
                                print("\tFailed! Out of range (destination) !", end='')
                    else:
                        print("\n\t row value is out of range or wrong number. try with smaller number.")
                else:
                    print("\tFailed! Out of range !", end='')
            except Exception:
                Log.printException( traceback.print_exc() )


    def listComponents(self, ix, bSilent=False, bPlot=True) -> bool:
        
        if bSilent == False:
            if ix == 1 or ix == 10:
                print("\n *** List of Track Segment components ***")
                print("\tCoordinate\tOrientation")
                for ts in TsegComp_inEditor.tsList:
                    print(f"\t{chr(ts.lConnector[0].idX + 0x40)}{ts.lConnector[0].idY}\t\t{ts.rOrientation}")
            
            if ix == 2 or ix == 10:
                print("\n *** List of Signal components ***")
                print("\tCoordinate")
                for sg in SigComp_inEditor.sigList:
                    print(f"\t{chr(sg.location.idX + 0x40)}{sg.location.idY}")
            
            if ix == 3 or ix == 10:
                print("\n *** List of Train components ***")
                print(" Train\tInit Loc.\tDestination")
                for i, tr in enumerate(TrainComp_inEditor.trainList):
                    print(f"  #{i+1}:\t{chr(tr.initLocation.idX + 0x40)}{tr.initLocation.idY} ({tr.initLocation.idX}, {tr.initLocation.idY})\t{chr(tr.destination.idX + 0x40)}{tr.destination.idY} ({tr.destination.idX}{tr.destination.idY})")

        if bPlot == True:
            if self.trafficSysMap == None:
                self.trafficSysMap = Display(Size.canvasWidth, Size.canvasHeight, TsegComp_inEditor.tsList, SigComp_inEditor.sigList, TrainComp_inEditor.trainList, None, False)
                self.trafficSysMap.start()
            elif self.isTrafficSimDisplayLive() == True:
                Display.bSimulating = False
                self.trafficSysMap = Display.trafficNetworkDspObject
                self.trafficSysMap.buildTrafficNetwork(TsegComp_inEditor.tsList, SigComp_inEditor.sigList, TrainComp_inEditor.trainList)
            else:
                print("\nThe display window seems to be closed by user. Relaunching it...")
                self.trafficSysMap = Display(Size.canvasWidth, Size.canvasHeight, TsegComp_inEditor.tsList, SigComp_inEditor.sigList, TrainComp_inEditor.trainList, None, False)
                self.trafficSysMap.start()
                
                #print("\nSorry, something went wrong!  Please restart the application.")
                #return False

        return True

    def beginSimulation(self, data, bAskConfirm=False, bShowList=False, sleepTime=None):

        bRun = False
        try:


            if bShowList == True:
                self.listComponents(10)

            
            if bAskConfirm == True:
                k = input("Please check the component list above and click 'y' if correct: (y/n):")
                if k == 'Y' or k == 'y':
                    bRun = True
            else:
                bRun = True


            if bRun == True:
                if data != None:
                    

                    CompData.SaveComponentDataToFile()

                # if self.trafficSysMap != None:
                #     self.trafficSysMap.sendEvent()
                #     self.trafficSysMap = None
                #     if sleepTime == None:
                #         time.sleep(1)

                if self.control == None:
                        self.control = Control()

                if sleepTime != None:
                    time.sleep(sleepTime)
                
                
                self.control.startTrafficControlSimulation(self.data)
        except Exception:
            Log.printException( traceback.print_exc() )

        return bRun
    
    
        
    