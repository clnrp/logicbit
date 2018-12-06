#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.logic import *
from logicbit.clock import *
from logicbit.keyboard import *

def flogic(clock):

    Alu = ALU8b()             # 8-bit arithmetic and logic unit
    Ram = RAM(2,8)            # 2 bits address and 8 bits of data

    AddSub = LogicBit(1)
    Alu0 = LogicBit(0)
    Alu1 = LogicBit(0)

    A = [LogicBit(1), LogicBit(0), LogicBit(1), LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(1), LogicBit(0)]
    B = [LogicBit(1), LogicBit(1), LogicBit(1), LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0)]

    #Ad0 = LogicBit(0)
    #Ad1 = LogicBit(1)
    #D0 = LogicBit(1)
    #D1 = LogicBit(0)
    We = LogicBit(1)
    Reset = LogicBit(0)

    Addr = [LogicBit(0), LogicBit(1)]
    Data = [LogicBit(1), LogicBit(1), LogicBit(1), LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0)]

    cnt = 0
    while(clock.GetState()):
        Clk = clock.GetClock()
        if(Clk==1):
            cnt+=1
            if(cnt>=4): # read memory
                We = LogicBit(0)

        C = Alu.Act(A, B, AddSub, Alu0, Alu1)
        C = Ram.Act(Addr, Data, We, Reset, Clk)

        if (Clk == 1):
            print(str(C[7]), str(C[6]), str(C[5]), str(C[4]), str(C[3]), str(C[2]), str(C[1]), str(C[0]))

clk = Clock(flogic,1,2)
clk.start() # initialize clock
#key = Keyboard(clk)
#key.start() # initialize keyboard