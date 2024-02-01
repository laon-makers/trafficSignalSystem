

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
import sys, os, traceback
from utils import Util, Result
from log import Log, printColorId, MsgLvl

###############
def main(argv:list) -> Result:

    try:

        arg = argv[0]
        if len(argv) > 1:
            opts = argv[1:]
        else:
            opts = []


        Log.enLog = Util.GetCfgValue('log')        
                
        try:
            if os.path.isdir('data') == False:
                os.mkdir('data')        
        except OSError:
            pass

        #*****************************************
        r = Result.NO_RESULT_YET
        
        if arg == 'help':        
            Util.PrintHelp()
            r = Result.OK
        elif arg == 'track':
            
            if len(opts) > 0:
                dev = "SIM_" + opts[0]            
            else:
                dev = "All"

            r = Result.OK  

        elif r == Result.NO_RESULT_YET:
            r = Result.OK
            
            if r == Result.OK:
                if arg == "menu":
                    from menuSimulator import Menu
                    conmenu = Menu()
                    r = conmenu.consoleMenuSim()
                #}
            #}      'if r == rlt.OK:'
        #}
        
    except Exception: 
        Log.printException( traceback.print_exc() )     
    
#}  End of 'def main(argv):'




#######
if __name__=="__main__":
    if len(sys.argv) > 1:     # check if there is any argument.
        main(sys.argv[1:])    # pass arguments only; not 'simulator.py' itself.
    else:        
        main(["menu"])
