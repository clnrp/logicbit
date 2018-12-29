#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.logic import *
from logicbit.clock import *
from logicbit.utils import *
from logicbit.keyboard import *

def flogic(clock):

    Alu = ALU8b()             # 8-bit arithmetic and logic unit
    Ram = RAM(2,8)            # 2 bits address and 8 bits of data

    AddSub = LogicBit(0)
    Alu0 = LogicBit(0)
    Alu1 = LogicBit(0)

    A = Utils.VecBinToPyList([1, 1, 1, 1, 1, 1, 1, 1])
    B = Utils.VecBinToPyList([0, 0, 0, 0, 0, 0, 0, 1])
    Printer(A,"A")
    Printer(B,"B")

    #Ad0 = LogicBit(0)
    #Ad1 = LogicBit(1)
    #D0 = LogicBit(1)
    #D1 = LogicBit(0)
    We = LogicBit(1)
    Reset = LogicBit(0)

    vect =[A,B,A,B] # test mux
    sel = [LogicBit(1), LogicBit(0)]
    mux = Mux(32,8)
    res = mux.Act(vect,sel)
    Printer(res)

    Addr = Utils.BinListToPyList([LogicBit(1), LogicBit(1), LogicBit(1)])
    Dec = BinaryDecoder()
    dec = Dec.Act(Addr)
    Printer(dec)

    Data = [LogicBit(1), LogicBit(1), LogicBit(1), LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0)]

    cnt = 0
    while(clock.GetState()):
        Clk = clock.GetClock()
        if(Clk==1):
            cnt+=1
            if(cnt>=4): # read memory
                We = LogicBit(0)

        C,Carry = Alu.Act(A, B, AddSub, Alu0, Alu1)
        #C = Ram.Act(Addr, Data, We, Reset, Clk)

        #if (Clk == 1):
        Printer(C)

clk = Clock(flogic,1,2)
clk.start() # initialize clock
#key = Keyboard(clk)
#key.start() # initialize keyboard