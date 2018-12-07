#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.logic import *
from logicbit.clock import *
from logicbit.utils import *
from logicbit.keyboard import *

class PC4bTris8b: # Program counter of 4 bits with tri-state
    def __init__(self):
        self.__pc4b = Counter4b()
        self.__tristate = TristateBuffer()

    def Act(self, Bus, EInc, EOut, NLoad, NReset, Clk):
        [q0, q1, q2, q3] = self.__pc4b.Act(Bus[0:4], EInc, NLoad, NReset, Clk)
        Dir = LogicBit(1)
        A = [q0, q1, q2, q3, Bus[4], Bus[5], Bus[6], Bus[7]]
        [A,B] = self.__tristate.Buffer(A, Bus, Dir, EOut) # Dir=1 and EOut=1 -> puts A in B
        return B

def flogic(clock):

    pc = PC4bTris8b()           # 4-bit instruction counter with 8-bit tri-state
    Bus = [LogicBit(0) for bit in range(8)] # bits of the line
    EIn = LogicBit(1)           # enable counter
    EOut = LogicBit(1)
    Load = LogicBit(1)          # load bits into 0
    Reset = LogicBit(1)           # Reset counter at 0

    cnt = 0
    while(clock.GetState()):
        Clk = clock.GetClock()
        if(Clk==1):
            cnt+=1
            if(cnt>=8): # load bits
                cnt = 0
                Reset = LogicBit(1)
                Load = LogicBit(0)
                Bus = [LogicBit(0),LogicBit(1),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(1),LogicBit(0)]
            else:
                Reset = LogicBit(1)
                Load = LogicBit(1)

        Bus = pc.Act(Bus, EIn, EOut, Load, Reset, Clk) # Load and Reset works in No

        if (Clk == 1):
            Printer(Bus)

clk = Clock(flogic,1,1)
clk.start() # initialize clock
#key = Keyboard(clk)
#key.start() # initialize keyboard