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
#import subprocess
import threading, traceback
import time
import pygame
from pygame.locals import *
from utils import Size, TrackSegLayout, ComponentId, Light, Result, Param
from typing import Tuple
from component import Location
from log import MsgLvl, Log
from component import Sif

class Display(threading.Thread):

    CLOSE_APP_CMD_EVT = pygame.USEREVENT + 1
    REDRAW_CMD_EVT = pygame.USEREVENT + 2
    JSW_CTRL_CMD_EVT = pygame.USEREVENT + 3

    bSimulating = False
    sigPosPixel = []        # a list of Rect objects.
    sigLightState = []
    sigNumber = []          # a list of integers.

    trainPos = []           # a list of 'Location' objects
    trainPosExtraStep = []  # a list of integers.
    trainNumber = []        # a list of integers.
    bTrainPosChanged = []   # a list of booleans
    trPosPixel = []         # a list of Rect objects.
    trPosNewPixel = []      # a list of 'Location' objects.
    bInitialized = False
    bPause = False

    
    jcNeckPosPixel = []     # a list of [x, y] which is the coordinate of each junction
    jcTinePosPixelRect = []
    jcSwIdx = []
    jcNewSwIdx = []
    
    # The junction sets it to true when there is a switch change 
    # is required from a junction. Then the display set to None once it serves 
    # the request. The junction can get it set to False by calling getServiceResultFromDsp method.
    # until it is set to false, this class will reject any further request from the junction.
    # however, if the switch was already set to what the junction requested, then it will
    # set it false immediately returning the service was done.
    bJcSwChangeReq = [] 

    trafficNetworkDspObject = None
    
    __jcSwRefreshIx = None
    __bJcSwRefresh = False

    def __init__(self, width, height, tsList=None, sigList=None, trainList=None, jcList=None, bSim=True):
        threading.Thread.__init__(self)
        self.width = width
        self.height = height
        self.trfNetwork = None
        self.bgSurface = None
        self.line_x1 = 0
        self.line_y1 = 0
        self.line_x2 = 0
        self.line_y2 = 0
        self.bRedraw = False
        self.running = True
         # Set the background color
        self.background_color = pygame.Color("gray95") #(255, 255, 255)
        # Draw lines and circles
        self.grid_line_color = pygame.Color("gray90")   # the bigger the number, the brighter it is.
        self.grid_line_color_b = pygame.Color("gray80")
        self.line_color = (0, 0, 0)
        self.circle_color = (255, 0, 0)
        self.buildingYard = None
        self.trackSegH = None
        self.trackSegDwn = None
        self.signalImg = []
        #self.train = None
        self.trainImg = []
        self.jcArrowImg = []
        
        Display.bSimulating = bSim
        self.tsList = tsList
        self.sigList = sigList
        self.trainList = trainList
        self.jcList = jcList
        #self.reInitDisplay()
        Display.trafficNetworkDspObject = self
        
        
        self.dbgBuf = None
        self.dbgValX = 0
        self.dbgValY = 0
        

    def reInitDisplay(self):
        ln = len(Display.sigPosPixel)
        for i in reversed(range(ln)):
            Display.sigPosPixel.pop(i)       # a list of Rect objects.
        
        ln = len(Display.sigLightState)
        for i in reversed(range(ln)):
            Display.sigLightState.pop(i)
        
        ln = len(Display.sigNumber)
        for i in reversed(range(ln)):
            Display.sigNumber.pop(i)          # a list of integers.

        ln = len(Display.trainPos)
        for i in reversed(range(ln)):
            Display.trainPos.pop(i)           # a list of 'Location' objects

        ln = len(Display.trainPosExtraStep)
        for i in reversed(range(ln)):
            Display.trainPosExtraStep.pop(i)  # a list of integers.
        
        ln = len(Display.trainNumber)
        for i in reversed(range(ln)):
            Display.trainNumber.pop(i)        # a list of integers.
        
        ln = len(Display.bTrainPosChanged)
        for i in reversed(range(ln)):
            Display.bTrainPosChanged.pop(i)   # a list of booleans
        
        ln = len(Display.trPosPixel)
        for i in reversed(range(ln)):
            Display.trPosPixel.pop(i)         # a list of Rect objects.
        
        ln = len(Display.trPosNewPixel)
        for i in reversed(range(ln)):
            Display.trPosNewPixel.pop(i)

        Sif.emptyJcNumList()

        for i in range(len(Display.jcNeckPosPixel)):
            Display.jcNeckPosPixel.pop()


        for i in range(len(Display.jcTinePosPixelRect)):
            Display.jcTinePosPixelRect.pop()

        for i in range(len(Display.jcSwIdx)):
            Display.jcSwIdx.pop()
        
        for i in range(len(Display.jcNewSwIdx)):
            Display.jcNewSwIdx.pop()
            
        Sif.emptyJcTsROrientation()
        Sif.emptyBjcReverse()

        ln = len(self.trainImg)
        for i in range(ln):
            self.trainImg.pop()


    def addNewTrainLocation(self, trainNo, location):
        
        bNew = True
        for n in Display.trainNumber:
            if n == trainNo:
                bNew = False

        if bNew == True:
            Display.trainNumber.append(trainNo)
            Display.trainPos.append(location)
            Display.trainPosExtraStep.append(0)
            Display.bTrainPosChanged.append(False)



    @classmethod
    def updateTrainLocation(cls, trainNo, location, extraStep, bForward, rOrientation):
        for ix, n in enumerate(cls.trainNumber):
            if n == trainNo:
                cls.trainPos[ix] = location
                cls.trainPosExtraStep[ix] = extraStep

                r = cls.getPixelXY(location)

                # #if r[0] != cls.trPosPixel[ix].x or r[1] != (cls.trPosPixel[ix].y + Size.trainLengthPixel) or cls.trainPosExtraStep[ix] != extraStep:
                # if r[0] != cls.trPosPixel[ix].x or r[1] != cls.trPosPixel[ix].y or cls.trainPosExtraStep[ix] != extraStep:
                cls.bTrainPosChanged[ix] = True                    
                #cls.trPosPixel[ix].topleft = (r[0], r[1])
                
                x = (extraStep * Size.numPixelXPerMoveCount)
                if bForward == False:
                    x = -x

                y = 0
                if rOrientation != TrackSegLayout.HORIZONTAL:
                    y = (extraStep * Size.numPixelYPerMoveCount)

                    if bForward == True:
                        if rOrientation == TrackSegLayout.UP:
                            y = -y
                    else:
                        # Don't be confused with this orientation.
                        # the orientation is about the right end of the track segment.
                        # So, when the train moves reverse direction, the train
                        # goes down hill.
                        if rOrientation == TrackSegLayout.UP:
                            y -= Size.numPixelPerGridY
                        if rOrientation == TrackSegLayout.DOWN:
                            y = Size.numPixelPerGridY - y

                cls.trPosNewPixel[ix].idX = r[0] + x
                cls.trPosNewPixel[ix].idY = r[1] + y
    

    @classmethod
    def updateSignalLightState(cls, sigNo, light, location=None):
        for ix, n in enumerate(cls.sigNumber):
            if n == sigNo:                
                cls.sigLightState[ix] = light                

    @classmethod
    def updateDspOnJcSwitchState(cls, jcNo, swIx, location=None) -> Tuple[bool, int]:
        for ix, n in enumerate(Sif.jcNumList):
            if n == jcNo:
                if swIx != None:
                    if cls.bJcSwChangeReq[ix] == False or swIx == Param.JC_SW_ARROW_HIDDEN:   # '-1' for arrow hide request
                        if swIx != cls.jcSwIdx[ix]:
                            cls.jcNewSwIdx[ix] = swIx
                            cls.bJcSwChangeReq[ix] = True
                            if swIx == Param.JC_SW_ARROW_HIDDEN:
                                # To notify 'Switch arrow hide request' has been received.
                                return [True, Result.JC_SW_ARROW_HIDE_REQ_RECEIVED]
                            
                            return [False, cls.jcSwIdx[ix]]
                        else:
                            #cls.bJcSwChangeReq[ix] = None
                            cls.__jcSwRefreshIx = ix
                            cls.__bJcSwRefresh = True

                        return [True, cls.jcSwIdx[ix]]
                    return [False, Result.ERR_NEED_CONFIRM_FIRST]  # the caller need to call getServiceResultFromDsp to acknowledge earlier request result.
                    
        return [False, Result.ERR_NO_MATCH_FOUND ] # '-l00' to let the junction knows that the junction number was not found.


    @classmethod
    def getServiceResultFromDsp(cls, jcNo) -> Tuple[bool, int]:
        for ix, n in enumerate(Sif.jcNumList):
            if n == jcNo:
                if cls.bJcSwChangeReq[ix] == None: # or cls.bJcSwChangeReq[ix] == None
                    cls.bJcSwChangeReq[ix] = False
                    return [True, cls.jcSwIdx[ix]]

                return [False, cls.jcSwIdx[ix]]
        return [False, Result.ERR_NO_MATCH_FOUND]  # to let caller know that there is no match junction number.
    
    @classmethod
    # def getJunctionSwitchStatus(cls, jcNo) -> int:
    #     for ix, n in enumerate(Sif.jcNumList):
    #         if n == jcNo:
    #             return cls.jcSwIdx[ix]
    #     return -1

    @classmethod
    def getPixelXY(cls, pos, comp=ComponentId.ID_TRAIN, orientation=None, bCompensate=True) -> Tuple[int, int]:
        r = []
        x = pos.idX
        y = pos.idY

        if x == 0:
            x = 1
            print(f"Warning! The X axis component location ID '{x}' must be greater than 0. It has been set to 1 by this s/w.")
        if y == 0:
            y = 1
            print(f"Warning! The Y axis component location ID '{y}' must be greater than 0. It has been set to 1 by this s/w.")
        
        r.append(((x - 1) * Size.numPixelPerGridX) + Size.numPixelGridStartX)
        y1 = (y * Size.numPixelPerGridY) + Size.numPixelGridStartY

        if bCompensate == True:
            if comp == ComponentId.ID_TRACK_SEG:
                if orientation == TrackSegLayout.UP:
                    adj = Size.trackSegUpPosAdj # last on to bring the segment onto the track.
                else:
                    adj = Size.trackSegHPosAdj  # last on to bring the segment onto the track.
            elif comp == ComponentId.ID_SIG:
                adj = Size.sigPosYAdj           # last on to bring the component off the track.    
                r[0] += Size.sigPosXAdj         # to bring the traffic signal to the center of vertical gird line.
            else:
                adj = Size.trainPosAdj          # last on to bring the train onto the track.

        else:
            adj = 0

        r.append(y1 - adj)      # last on to bring the component onto the track or off the track if it is a traffic signal.

        return r
    




    @classmethod
    def getPixelXYRect(cls, pos, orientation, bCompensate=True) -> Rect:
        r = []
        x = pos.idX
        y = pos.idY

        if x == 0:
            x = 1
            print(f"Warning! The X axis component location ID '{x}' must be greater than 0. It has been set to 1 by this s/w.")
        if y == 0:
            y = 1
            print(f"Warning! The Y axis component location ID '{y}' must be greater than 0. It has been set to 1 by this s/w.")
        
        x1 = ((x - 1) * Size.numPixelPerGridX) + Size.numPixelGridStartX
        y1 = (y * Size.numPixelPerGridY) + Size.numPixelGridStartY

        if bCompensate == True:
            if orientation == TrackSegLayout.HORIZONTAL:
                x2 = x1 + Size.numPixelPerGridX * 2
                tmp = y1 - Size.numPixelTsHeight
                y2 = y1
                y1 = tmp
                #w = Size.numPixelPerGridX * 2
                #h = Size.numPixelTsHeight
            elif orientation == TrackSegLayout.UP:
                x2 = x1 + Size.numPixelPerGridX * 2
                tmp = y1 - Size.numPixelPerGridY
                y2 = y1
                y1 = tmp

            elif orientation == TrackSegLayout.DOWN:
                x2 = x1 + Size.numPixelPerGridX * 2
                y2 = y1 + Size.numPixelPerGridY
        else:
            # this is only for junction switch arrows
            x2 = x1 + Size.numPixelJunctionSwWidth
            y2 = y1 + Size.numPixelJunctionSwHeight

        return Rect(x1, y1, (x2-x1), (y2-y1))
    


    @classmethod
    def poll(cls) -> bool:
        if cls.trafficNetworkDspObject == None:
            return False
        else:
            return True



    def addTrackSegmentComponent(self, pos, orientation):
        
        loc = Display.getPixelXY(pos, ComponentId.ID_TRACK_SEG, orientation)
        icon = None
        if orientation == TrackSegLayout.UP:
            icon = self.trackSegUp

        elif orientation == TrackSegLayout.DOWN:                        
            icon = self.trackSegDwn
        else:
            icon = self.trackSegH
        
        self.trfNetwork.blit(icon, (loc[0], loc[1]))

    
    def addSignalComponent(self, ix, pos):
        loc = Display.getPixelXY(pos, ComponentId.ID_SIG)
        
        if Display.bSimulating == True:
            lgt = Light.RED
        else:
            lgt = Light.GREEN_RED_ON

        self.trfNetwork.blit(self.signalImg[lgt], (loc[0], loc[1]))
        Display.sigLightState.append(lgt)
        Display.sigNumber.append(ix + 1)
        Display.sigPosPixel.append(self.signalImg[lgt].get_rect())
        Display.sigPosPixel[ix] = Display.sigPosPixel[ix].move(loc[0], loc[1])


    def addTrainComponent(self, ix, pos):
        
        fn = f".\img\Train_{ix+1}.png"
        # following 3 statements must be executed before invoking addTrainComponent method.
        trn = pygame.image.load(fn).convert_alpha()
        trn.set_colorkey((255,255,255))
        self.trainImg.append(trn)
        
        loc = Display.getPixelXY(pos)
        #Display.trPosPixel.append(self.train.get_rect())

        self.trfNetwork.blit(self.trainImg[ix], (loc[0], loc[1]))
        Display.trPosNewPixel.append(Location(loc[0], loc[1]))
        Display.trPosPixel.append(self.trainImg[ix].get_rect())
        

        #ix = len(Display.trPosPixel)
        Display.trPosPixel[ix] = Display.trPosPixel[ix].move(loc[0], loc[1])
        #Log.print(f"train location: ({pos.idX}, {pos.idY}) {loc[0]},{loc[1]} {Display.trPosPixel[ix].left},{Display.trPosPixel[ix].y}", 50)
        
    
    def addJunctionInfo(self, num, swIx, bReverse, jcLoc, nextTs, rOrient):
        try:
            # if len(nextTs) > 0:
            #     #rect1 = Display.getPixelXYRect(nextTs[0].lConnector[0], nextTs[0].rOrientation)
            #     if bReverse == False:
            #         rect1 = Display.getPixelXYRect(jcLoc, nextTs[0].rOrientation, False)
            #     else:
            #         rect1 = Display.getPixelXYRect(Location(jcLoc.idX - Size.trackSegmentLength, jcLoc.idY), nextTs[0].rOrientation, False)
            # else:
            #     rect1 = None

            # if len(nextTs) > 1:
            #     if bReverse == False:
            #         rect2 = Display.getPixelXYRect(jcLoc, nextTs[1].rOrientation, False)
            #     else:
            #         rect2 = Display.getPixelXYRect(Location(jcLoc.idX - Size.trackSegmentLength, jcLoc.idY), nextTs[1].rOrientation, False)
            # else:
            #     # As an walk around, single tine fork will be handled this way in order not to get the exception thrown.
            #     #rect2 = None
            #     #rect2 = Display.getPixelXYRect(nextTs[0].lConnector[0], nextTs[0].rOrientation)
            #     if bReverse == False:
            #         rect2 = Display.getPixelXYRect(jcLoc, nextTs[0].rOrientation, False)
            #     else:
            #         rect2 = Display.getPixelXYRect(Location(jcLoc.idX - Size.trackSegmentLength, jcLoc.idY), nextTs[0].rOrientation, False)

            pos = Display.getPixelXY(jcLoc, ComponentId.ID_TRACK_SEG, TrackSegLayout.HORIZONTAL, False)
            
            if bReverse == True:
                #pos[0] -= Size.numPixelPerGridX * 2
                if pos[0] <= 0:
                    pos[0] = Size.numPixelGridStartX
            
            Display.jcNeckPosPixel.append(pos)

            rect = []
            for ix, ro in enumerate(rOrient):

                if ro == None:
                    if ix > 0:
                        rect.append(rect[0])
                    continue

                x, y = self.adjustArrowImageLocation(pos[0], pos[1], rOrient[ix], bReverse)

                if TrackSegLayout.DOWN - ro < 3: 
                    rect.append( self.jcArrowImg[ro].get_rect() )
                    # if ro == TrackSegLayout.HORIZONTAL:
                    #     rect.append( self.jcArrowImg[0].get_rect() )
                    # elif ro == TrackSegLayout.UP:
                    #     rect.append( self.jcArrowImg[1].get_rect() )

                    # elif ro == TrackSegLayout.DOWN:
                    #     rect.append( self.jcArrowImg[2].get_rect() )
                    # elif ix > 0:
                    #     rect.append(rect[0])
                    
                    if rect[ix] != None:
                        rect[ix] = rect[ix].move(x, y)
                    #rect[ix] = Rect(rect[ix].x + x, rect[ix].y + y, rect[ix].w, rect[ix].h)
                        # rect[ix].x = x
                        # rect[ix].y = y

                    # if rect1 != None:
                    #     rect1.y -= Size.numPixelPerGridY
                    # #pos[1] -= Size.numPixelPerGridY
            
            if len(rect) < 2:
                rect.append(rect[0])

            Sif.appendJcNumList(num)
            
            Display.jcTinePosPixelRect.append([rect[0], rect[1]])
            del rect

            # both arrays need to be filled with each default and the bJcSwChangeReq to True.
            # this way, this object can set each junction switch to its default one.
            Display.jcSwIdx.append(swIx)    # saving the default switch index.
            #Display.jcSwIdx.append(None)    # saving the default switch index.
            Display.jcNewSwIdx.append(Param.JC_SW_ARROW_HIDDEN)
            #Display.jcNewSwIdx.append(None)
             
            # Each junction switch must be set to its default as soon as it is powered up.
            # So its initial value must be True to get the first setting is done.            
            Display.bJcSwChangeReq.append(True) 
            # As an walk around, single tine fork will be handled this way in order not to get the exception thrown.
            if len(rOrient) == 1:
                rOrient.append(rOrient[0])
            elif rOrient[1] == None:
                rOrient[1] = rOrient[0]

            Sif.appendJcTsROrientation(rOrient)
            Sif.appendBjcReverse(bReverse)            

        except Exception:
            Log.printException( traceback.print_exc() ) 


    def captureBackgroundImage(self):
        #bgRect = pygame.Rect(Size.numPixelGridStartX, Size.numPixelGridStartY, self.width - Size.numPixelGridStartX, self.height - Size.numPixelGridStartY)
        bgRect = pygame.Rect(0, 0, self.width, self.height)
        self.bgSurface = self.trfNetwork.subsurface(bgRect).convert() # don't miss this 'convert()' otherwise followed blit will get crashed.
        
        self.trfNetwork.blit(self.bgSurface, bgRect)

        #pygame.image.save(self.bgSurface, "bgSurface.png")
        #newBackground = pygame.image.load("bgSurface.png").convert()
        #newBackground = self.bgSurface

        #self.trfNetwork.blit(self.bgSurface, 0, 0)

    def killDrawWIndow(self):
        self.running = False

    def sendEvent(self):
        pygame.event.post(pygame.event.Event(self.CLOSE_APP_CMD_EVT))
        #self.running = False

    @classmethod
    def emergencyKill(cls):
        pygame.event.post(pygame.event.Event(cls.CLOSE_APP_CMD_EVT))
        

    
    def debugCommand(self, cmd, arg1=None, arg2=None, arg3=None):
        try:
            if cmd.find("jc") == 0:
                c = cmd.split(" ")
                ln = len(c)
                
                Display.bPause = True

                if ln > 1:
                    if c[1]  == "show" or c[1] == "add":
                        if ln > 3:
                            jcId = int(c[2])
                            arrIx = int(c[3])
                            
                            if ln > 4:
                                self.dbgValX = int(c[4])
                            else:
                                self.dbgValX = 0

                            if ln > 5:
                                self.dbgValY = int(c[5])
                            else:
                                self.dbgValY = 0
                            
                            Log.print(F"\t{cmd}")
                            
                            
                            Log.print(F"\tcmd: {cmd}, args: {jcId}, {arrIx}", MsgLvl.CORE_MSG)

                            if jcId < len(Sif.jcTsROrientation):
                                if arrIx < len(Sif.jcTsROrientation[jcId]) and Sif.jcTsROrientation[jcId] != None:
                                    Display.jcNewSwIdx[jcId] = arrIx
                                    if Display.jcSwIdx[jcId] == None:
                                        Display.jcSwIdx[jcId] = arrIx

                                    Display.bJcSwChangeReq[jcId] = True
                                    print(f"\t* Orientation: {Sif.jcTsROrientation[jcId][arrIx]}")                                    
                                    self.paintJunctionSwitch()
                                    pygame.draw.circle(self.trfNetwork, self.circle_color, (Display.jcNeckPosPixel[jcId][0], Display.jcNeckPosPixel[jcId][1]), 5)
                                    pygame.display.update()

                                else:
                                    Log.print(F"  Th 2nd value {arrIx} is out of range...", MsgLvl.CORE_MSG)
                            else:
                                Log.print(F" The first value {jcId} is out of range...", MsgLvl.CORE_MSG)

                    elif c[1] == "clear":

                        for ix in range(len(Display.bJcSwChangeReq)):
                            Display.bJcSwChangeReq[ix] = True
                            Display.jcNewSwIdx[ix] = 1

                        self.paintJunctionSwitch(True)

                        for ix in range(len(Display.bJcSwChangeReq)):
                            Display.bJcSwChangeReq[ix] = True
                            Display.jcNewSwIdx[ix] = 0

                        self.paintJunctionSwitch(True)
                        pygame.display.update()

                    elif c[1] == "xy":
                        
                        print(" * Each junction location:")

                        for ix, xy in enumerate(Display.jcNeckPosPixel):
                            if len(Display.jcNeckPosPixel[ix]) > 1:
                                print(f"{ix}: ({xy[0]}, {xy[1]})")
                            else:
                                print(f"{ix}: ({xy[0]}, n/a)")

                        print(" * Each arrows' background location:")
                        print(f"{Display.jcNeckPosPixel}")

                
        except Exception:
            Log.printException( traceback.print_exc() )
        
        finally:
            Display.bPause = False


    def paintJunctionSwitch(self, bCleanOnly=False):
        try:
            # TODO: to be completed soon.
            for ix in range(len(Display.jcNewSwIdx)):
                if Display.jcSwIdx[ix] != Display.jcNewSwIdx[ix] or Display.bJcSwChangeReq[ix] == True or Display.__jcSwRefreshIx == ix:

                    i = Display.jcSwIdx[ix]

                    if Display.jcNewSwIdx[ix] == None:
                        continue

                    if len(Sif.jcTsROrientation) == 0:
                        break

                    if i != Param.JC_SW_ARROW_HIDDEN:     # if '-1', it means that last command with this jcSwIdx was for hiding the given image. No more action possible because it has -1.
                        self.trfNetwork.blit(self.bgSurface, Display.jcTinePosPixelRect[ix][i], Display.jcTinePosPixelRect[ix][i])
                    
                    i = Display.jcSwIdx[ix] = Display.jcNewSwIdx[ix]

                    if bCleanOnly == False:

                        if i != Param.JC_SW_ARROW_HIDDEN: # 1 means hide request.
                            imgIx = Sif.jcTsROrientation[ix][i]
                            img = self.jcArrowImg[imgIx]

                            x = self.dbgValX + Display.jcTinePosPixelRect[ix][i].x
                            y = self.dbgValY + Display.jcTinePosPixelRect[ix][i].y

                            self.trfNetwork.blit( img,  (x, y) )

                    if Display.bJcSwChangeReq[ix] == True:
                        Display.bJcSwChangeReq[ix] = None
                    
                    if Display.__jcSwRefreshIx == ix:
                        Display.__bJcSwRefresh = False
                        Display.__jcSwRefreshIx = None
                

        except Exception:
            Log.printException( traceback.print_exc() )



    def adjustArrowImageLocation(self, x, y, orientation, bReverse):
        '''
            
        '''
        #c = self.circle_color

        if orientation == TrackSegLayout.UP:
            if bReverse == False:
                x = x + 19  #x = x + Size.numPixelPerGridX/4 + 10
                y = y - 66 #y = y - Size.numPixelPerGridY - Size.numPixelPerGridY/5 + 6
                
            else:   # It is still UP for the reverse move side junction as well even though the fork tine is the down the hill. 
                x = x - 80 #x = x - (Size.numPixelPerGridX * 2) + (Size.numPixelPerGridX/4) + 7
                y = y - 6  #y = y - Size.numPixelPerGridY + Size.numPixelPerGridY/4 + 47 
                        
            
        elif orientation == TrackSegLayout.DOWN:
            if bReverse == False:
                x = x + Size.numPixelPerGridX/4
                y = y + Size.numPixelPerGridY/3
                y -= 5
            else: # It is still DOWN for the reverse move side junction as well even though the fork tine is the up the hill.
                x = x - 88  # -13
                y = y - 45  # -33

            
        else:
            if bReverse == False:
                x = x + Size.numPixelPerGridX/4
            else:
                x = x + Size.numPixelPerGridX/4 - (Size.numPixelPerGridX * 2)

            y = y - Size.numPixelPerGridY/2

        return [x, y]
    


    def updateXyVal(self, x1, y1, x2, y2, bDraw=False):    
                
        self.line_x1 = x1
        self.line_y1 = y1

        self.line_x2 = x2
        self.line_y2 = y2

        self.bRedraw = bDraw
    

    
    def drawGrid(self, canvas):
        ''' This method draws the grid on the traffic network '''

        color = [self.grid_line_color_b, self.grid_line_color]

        if Display.bInitialized == False:
           
            canvas.fill(self.background_color)
            
            Display.bInitialized = True        
        
        i = 1
        
        maxY = self.height - Size.numPixelPerGridY + 20
        maxX = self.width - Size.numPixelPerGridX + 10
        for x in range(Size.numPixelGridStartX, self.width - Size.numPixelPerGridY + 10, Size.numPixelPerGridX):
            i += 1
            i %=2
            pygame.draw.line(canvas, color[i], (x, Size.numPixelGridStartY), (x, maxY), 2 - i)

        i = 1
        for y in range(Size.numPixelGridStartY, self.height - Size.numPixelPerGridY + 10, Size.numPixelPerGridY):
            i += 1
            i %=2
            #pygame.draw.line(canvas, color[i], (Size.numPixelGridStartX, y), (maxX, y), 2 - i)
            pygame.draw.line(canvas, color[0], (Size.numPixelGridStartX, y), (maxX, y), 2)


    def keyHandleForJswControl(self, evt_type):
        
        pygame.event.pump()

        key= pygame.key.get_pressed()

        if key[pygame.K_a]:
            print("A pressed")
        if key[pygame.K_F2]:
            print("F1 pressed")





    def buildTrafficNetwork(self, tsList, sigList, trainList, jcList=None):
        
        try:        
            if Display.bInitialized == True:
                Display.bPause = True
                self.reInitDisplay()
                
            

            if Display.bInitialized == False:
                Display.bInitialized = True

                pygame.init()
                # Create the canvas
                flags = pygame.NOFRAME  # Flag to remove window frame
                self.trfNetwork = pygame.display.set_mode((self.width, self.height))
                #self.bgSurface = pygame.display.set_mode((self.width, self.height))
                pygame.display.set_caption("Case Study (Train Signaling System Simulator)")
                
                # # Create the canvas
                # flags = pygame.NOFRAME  # Flag to remove window frame
                # self.trfNetwork = pygame.display.set_mode((self.width, self.height))
                # #self.bgSurface = pygame.display.set_mode((self.width, self.height))
                # pygame.display.set_caption("Case Study (Train Signaling System Simulator)")
                #editorXaxes = pygame.image.load(".\editorXaxes.png")
                self.buildingYard = pygame.image.load(".\img\Traffic_Simulator_Background.png").convert()
                    
                # Make the image transparent. 1 step is to use convert_alpha to use per-pixel alpha.            
                self.trackSegH = pygame.image.load(".\img\Track_SegmentH_II.png").convert_alpha()
                # set the color key to transparent (I'm using white color as a transparent color in this example)
                self.trackSegH.set_colorkey((255,255,255))

                self.trackSegUp = pygame.image.load(".\img\Track_SegmentUp_II.png").convert_alpha()
                self.trackSegUp.set_colorkey((255,255,255))

                self.trackSegDwn = pygame.image.load(".\img\Track_SegmentDown_II.png").convert_alpha()
                self.trackSegDwn.set_colorkey((255,255,255))

                self.signalImg.append(pygame.image.load(".\img\Traffic_Light_Red.png").convert())
                self.signalImg.append(pygame.image.load(".\img\Traffic_Light_Green.png").convert())
                self.signalImg.append(pygame.image.load(".\img\Traffic_Light.png").convert())

                ## NOTE: Do Not Change the order of image loading. The horizontal arrow first, Up the hill, and the Down the hill direction arrow.
                self.jcArrowImg.append(pygame.image.load(".\img\Arrow_LeftRight.png").convert_alpha())
                self.jcArrowImg.append(pygame.image.load(".\img\Arrow_Up_II.png").convert_alpha())
                self.jcArrowImg.append(pygame.image.load(".\img\Arrow_Down_II.png").convert_alpha())

                for i in range (len(self.jcArrowImg)):
                    self.jcArrowImg[i].set_colorkey((255,255,255))

            self.trfNetwork.blit(self.buildingYard, (0, 0))

            if len(tsList) > 0:
                if isinstance(tsList[0], list) == True:
                    # This method was called by the simulator control algorithm.
                    for tsa in tsList:
                        for ts in tsa:
                            self.addTrackSegmentComponent(ts.lConnector[0], ts.rOrientation)
                else:
                # This method was called by the editor.
                    for ts in tsList:
                        self.addTrackSegmentComponent(ts.lConnector[0], ts.rOrientation)
                    

            if len(sigList) > 0:
                for ix, sg in enumerate(sigList):
                    self.addSignalComponent(ix, sg.location)
            
            self.captureBackgroundImage()

            if jcList != None:
                if len(jcList) > 0:
                    for jc in jcList:
                        self.addJunctionInfo(jc.num, jc.nextIndex[0], jc.bReverse, jc.location, jc.trackSeg, jc.rOrientation)


            if len(trainList) > 0:
                for ix, tr in enumerate(trainList):
                    self.addTrainComponent(ix, tr.currentLocation)
                    self.addNewTrainLocation(ix + 1, tr.currentLocation)

            
            
            # Update the self.trfNetwork
            pygame.display.flip()
            
            # Bring the window on top
            #pygame.event.post(pygame.event.Event(ACTIVEEVENT, gain=1, state=1))
            

            #self.drawGrid(self.trfNetwork)

            Display.bPause = False

        except Exception:
            Log.printException( traceback.print_exc() )
        


    def run(self):
        try:
            # if following method call is done outside this run method,
            # the screen becomes unresponsive.
            self.buildTrafficNetwork(self.tsList, self.sigList, self.trainList, self.jcList)

            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                        self.running = False

                    if event.type == self.JSW_CTRL_CMD_EVT:
                        self.keyHandleForJswControl(event.type)

                    if event.type == self.CLOSE_APP_CMD_EVT:
                        self.running = False
                        #raise SystemExit
                #pygame.event.pump()
                if Display.bPause == False:
                    if self.bRedraw == True:
                        pygame.draw.line(self.trfNetwork, self.line_color, (self.line_x1, self.line_y1), (self.line_x2, self.line_y2), 5)
                        pygame.display.flip()
                        self.bRedraw = False

                    if Display.bSimulating == True:
                        
                        self.paintJunctionSwitch()


                        bNew = False
                        for ix in range(len(Display.trPosPixel)):

                            if Display.trPosNewPixel[ix].idX != Display.trPosPixel[ix].x or Display.trPosNewPixel[ix].idX != Display.trPosPixel[ix].y:
                                if ix < len(Display.bTrainPosChanged):
                                    Display.bTrainPosChanged[ix] = False
                                    if Display.trPosNewPixel[ix].idX >= Size.numPixelGridStartX and Display.trPosNewPixel[ix].idY <= (Size.canvasWidth - Size.numPixelGridStartX):
                                        bNew = True
                                        self.trfNetwork.blit(self.bgSurface, Display.trPosPixel[ix], Display.trPosPixel[ix])

                                        Display.trPosPixel[ix].topleft = (Display.trPosNewPixel[ix].idX, Display.trPosNewPixel[ix].idY)
                                        
                                        self.trfNetwork.blit(self.trainImg[ix],  Display.trPosPixel[ix])
                                else:
                                    a = 30

                        for ix in range(len(Display.sigPosPixel)):
                            
                            self.trfNetwork.blit(self.bgSurface, Display.sigPosPixel[ix], Display.sigPosPixel[ix])
                            if Display.sigLightState[ix] == Light.GREEN:
                                i = Light.GREEN
                                self.trfNetwork.blit(self.signalImg[i],  Display.sigPosPixel[ix])
                            elif Display.sigLightState[ix] == Light.RED:
                                i = Light.RED
                                self.trfNetwork.blit(self.signalImg[i],  Display.sigPosPixel[ix])

                        pygame.display.update()

        except Exception:
            Log.printException( traceback.print_exc() )

        finally: 
            # Quit Pygame
            pygame.quit()


    