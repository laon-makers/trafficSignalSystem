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

from enum import Enum, IntEnum
from os import write
import sys, traceback
from datetime import datetime

from colorama import Fore, Back, Style, init  #,


#######
#######
class printColorId(IntEnum):
    WHITE_BLACK = 1
    RED_BLACK = 2
    GREEN_BLACK = 3
    BLUE_BLACK = 4
    MAGENTA_BLACK = 5
    WHITE_GREEN = 6
    WHITE_RED = 7
    WHITE_MAGENTA = 8
    RED_WHITE = 9
    CYAN_BLACK = 10
    YELLOW_BLACK = 11

#class MsgLvl:
#class MsgLvl(Enum):
class MsgLvl(IntEnum):
    NO_MSG  = 0
    CORE_MSG = 1    
    INFO_MSG = CORE_MSG + 1
    DBG_MSG  = INFO_MSG + 1
    DBG_MSG_L2 = DBG_MSG + 1

    DBG_MSG_DSP_UPDATE = 1
    DBG_MSG_TABLE      = 1
    DBG_MSG_COMP_TABLE = 100
    DBG_MSG_SIGNALING_TABLE = 100

    ALL_MSG   = 255

class Log:
    logFile = []
    logFileName = ".\log\log_"
    logFilePage = 0
    logEn = False           # it is not directly synched with the 'log' configuration in sim.cfg file.
    logCount = 0
    enDebugMsg = True #True
    logLvl = MsgLvl.DBG_MSG_DSP_UPDATE

    def __init__(self):
        pass

    @staticmethod
    def print(msg, lvl=200):
        if Log.enDebugMsg == True:
            if lvl <= Log.logLvl:
                print(msg)

    init(autoreset=True)    # Do not comment it out. Otherwise consol background color will be massed up.

  #####
    @classmethod
    def OpenLogFile(cls) -> None:

        if cls.logEn == False:
            now = datetime.now()
            cls.logFileName = ".\log\log_" + now.strftime("%Y%m%d_%H_%M_%S")
            cls.logFilePage = 0
            cls.logCount = 0

            cls.logFile = open( cls.logFileName + ".txt", "a")
            cls.logEn = True

  #####
    @classmethod
    def OpenNewLogFile(cls):

        if cls.logEn == True:
            cls.logFile.close()
            cls.logFilePage += 1
            cls.logCount = 0        
        
            fn = cls.logFileName + "_" + str(cls.logFilePage) + ".txt"

            cls.logFile = open( fn, "a")

  #####
    @classmethod
    def CloseLogFile(cls):        
        cls.logFile.close()    
        cls.logEn = False

  #####
    # bForced:
    #   - True: You can get the message logged into the log file
    @classmethod
    def LogMsg(cls, msg, bForced = False, bFlush = False):
            
        #breakpoint()
        cls.logCount += 1

        cls.logFile.write(msg)
        if bFlush == True:
            cls.logFile.flush()
        
        if cls.logCount > 20000:
            cls.OpenNewLogFile()

        
  #####
    # bForced:
    #   - True: You can get the message logged into the log file
    @classmethod
    def PrintBNR(cls, msg, lvl=50, bLogOnly=False, bForced = False):
        '''
        Print a string in Black; No Return escape character at the end of the string.
        '''
        if cls.enDebugMsg == True:
                if lvl <= Log.logLvl:
                    if bLogOnly == False:
                        print(msg, end='')

                    if cls.logEn == True:
                        cls.LogMsg(msg, bForced)



  #####
    # bForced:
    #   - True: You can get the message logged into the log file
    @classmethod
    def PrintC(cls, msg, cIx, bLogOnly=False, bForced = False):
        '''
        Print a string in color. fc: foreground color, bc: background color    
        '''

        try:
            if msg == None:
                msg = "Exception from source which doesn't have 'try-except'"
            elif msg != "":
                msg += f"{Style.RESET_ALL}"

                if bLogOnly == False:
                    bNl = True # New Line
                    if cIx == printColorId.RED_BLACK:
                        bNl = False
                        #print(Fore.RED + Back.BLACK + msg)
                        #m = Fore.RED + Back.BLACK + msg
                        m = f"{Fore.RED}{Back.BLACK}{msg}"
                    elif cIx == printColorId.GREEN_BLACK:
                        bNl = False
                        #print(Fore.GREEN + Back.BLACK + msg)
                        m = f"{Fore.GREEN}{Back.BLACK}{msg}"
                    elif cIx == printColorId.BLUE_BLACK:
                        bNl = False
                        #print(Fore.RED + Back.BLACK + msg)
                        #m = Fore.RED + Back.BLACK + msg
                        m = bColors.CBLUE + msg + bColors.CEND
                    elif cIx == printColorId.WHITE_GREEN:
                        #print(Fore.WHITE + Back.GREEN + msg, end='')
                        #m = Fore.WHITE + Back.GREEN + msg
                        m = f"{Fore.WHITE}{Back.GREEN}{msg}"
                    elif cIx == printColorId.WHITE_RED:
                        #print(Fore.WHITE + Back.RED + msg, end='')
                        #m = Fore.WHITE + Back.RED + msg
                        #m = f"{Fore.WHITE}{Back.RED}{msg}"
                        m = bColors.CBLUE + msg + bColors.CEND
                    elif cIx == printColorId.MAGENTA_BLACK:
                        #print(Fore.MAGENTA + Back.BLACK + msg, end='')
                        #m = Fore.MAGENTA + Back.BLACK + msg
                        m = f"{Fore.MAGENTA}{Back.BLACK}{msg}"
                    elif cIx == printColorId.WHITE_MAGENTA:
                        #print(Fore.WHITE + Back.MAGENTA + msg, end='')
                        #m = Fore.WHITE + Back.MAGENTA + msg
                        m = f"{Fore.WHITE}{Back.MAGENTA}{msg}"
                    elif cIx == printColorId.RED_WHITE:
                        #print(Fore.RED + Back.WHITE + msg, end='')
                        #m = Fore.RED + Back.WHITE + msg
                        m = f"{Fore.RED}{Back.WHITE}{msg}"
                    elif cIx == printColorId.YELLOW_BLACK:
                        #m = Fore.YELLOW + Back.BLACK + msg
                        m = f"{Fore.YELLOW}{Back.BLACK}{msg}"
                    else:
                        bNl = False
                        #m = Fore.WHITE + Back.BLACK + msg
                        m = f"{Fore.WHITE}{Back.BLACK}{msg}"
                    
                    
                    #print(m)
                    print( m )
            else:
                msg = "Empty Message !"

            if cls.logEn == True:
                cls.LogMsg(msg, bForced)
        
        except Exception:
            print(msg)
            traceback.print_exc()

    @classmethod
    def printException(cls, msg):
        print( bColors.CREDBG + "Exception Message !!!" + bColors.CEND )
        print(msg)

class bColors:
    CEND      = '\33[0m'
    CBOLD     = '\33[1m'
    CITALIC   = '\33[3m'
    CURL      = '\33[4m'
    CBLINK    = '\33[5m'
    CBLINK2   = '\33[6m'
    CSELECTED = '\33[7m'
    UNDERLINE = '\033[4m'

    CBLACK  = '\33[30m'
    CRED    = '\33[31m'
    CGREEN  = '\33[32m'
    CYELLOW = '\33[33m'
    CBLUE   = '\33[34m'
    CVIOLET = '\33[35m'
    CBEIGE  = '\33[36m'
    CWHITE  = '\33[37m'

    CBLACKBG  = '\33[40m'
    CREDBG    = '\33[41m'
    CGREENBG  = '\33[42m'
    CYELLOWBG = '\33[43m'
    CBLUEBG   = '\33[44m'
    CVIOLETBG = '\33[45m'
    CBEIGEBG  = '\33[46m'
    CWHITEBG  = '\33[47m'

    CGREY    = '\33[90m'
    CRED2    = '\33[91m'
    CGREEN2  = '\33[92m'
    CYELLOW2 = '\33[93m'
    CBLUE2   = '\33[94m'
    CVIOLET2 = '\33[95m'
    CBEIGE2  = '\33[96m'
    CWHITE2  = '\33[97m'

    CGREYBG    = '\33[100m'
    CREDBG2    = '\33[101m'
    CGREENBG2  = '\33[102m'
    CYELLOWBG2 = '\33[103m'
    CBLUEBG2   = '\33[104m'
    CVIOLETBG2 = '\33[105m'
    CBEIGEBG2  = '\33[106m'
    CWHITEBG2  = '\33[107m'


    WARNING = '\033[93m'
    FAIL = CRED

