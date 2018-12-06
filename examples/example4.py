#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.logic import *
from logicbit.clock import *
from logicbit.keyboard import *

def flogic(clock):

    pc = Counter4b()           # 4-bit instruction counter with 8-bit tri-state
    Bus = [LogicBit(0) for bit in range(8)] # bits of the line
    EIn = LogicBit(1)           # enable counter
    EOut = LogicBit(1)
    Load = LogicBit(1)          # load bits into 0
    Clr = LogicBit(1)           # clear counter at 0

    cnt = 0
    while(clock.GetState()):
        Clk = clock.GetClock()
        if(Clk==1):
            cnt+=1
            if(cnt>=8): # load bits
                cnt = 0
                Clr = LogicBit(0)
                Load = LogicBit(0)
                Bus = [LogicBit(0),LogicBit(1),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(1),LogicBit(0)]
            else:
                Clr = LogicBit(1)
                Load = LogicBit(1)
        #[q0, q1, q2, q3] = pc.Act(En ,In, Load, Clr, Clk)
        Bus = pc.Act(EIn, EOut, Bus, Load, Clr, Clk)

        if (Clk == 1):
            print(str(Bus[7]), str(Bus[6]), str(Bus[5]), str(Bus[4]), str(Bus[3]), str(Bus[2]), str(Bus[1]), str(Bus[0]))

clk = Clock(flogic,1,1)
clk.start() # initialize clock
#key = Keyboard(clk)
#key.start() # initialize keyboard