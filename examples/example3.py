#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.logic import *
from logicbit.clock import *
from logicbit.utils import *
from logicbit.keyboard import *

def flogic(clock):
    bit0 = LogicBit(1)
    bit1 = LogicBit(0)
    bit2 = LogicBit(0)
    bit3 = LogicBit(0)
    bit4 = LogicBit(0)
    bit5 = LogicBit(0)
    bit6 = LogicBit(0)
    bit7 = LogicBit(1)

    f0 = Flipflop("D", "UP")
    f1 = Flipflop("D", "UP")
    f2 = Flipflop("D", "UP")
    f3 = Flipflop("D", "UP")

    q0 = f0.GetQ()
    q1 = f1.GetQ()
    q2 = f2.GetQ()
    q3 = f3.GetQ()

    reg1 = Register8b_Sb()

    for Clk in [LogicBit(0), LogicBit(1)]:
        reg1.Act(Utils.VecBinToPyList([1,0,0,0,0,1,1,1]), LogicBit(1), LogicBit(0), Clk)
    Printer(reg1.Read())

    Mask = Utils.VecBinToPyList([0,0,0,0,0,0,0,1])
    for Clk in [LogicBit(0), LogicBit(1)]:
        reg1.SetBit(LogicBit(0), Mask, LogicBit(1), Clk)  # Reset bit zero of the register
    Printer(reg1.Read())

    while(clock.GetState()):
        Clk = clock.GetClock()
        clock.Print()

        Q3 = LogicBit(0)
        Q2 = q0.Not()*q1*q2.Not()*q3.Not() + q0*q1.Not()*q2.Not()*q3.Not()
        Q1 = q0.Not()*q1*q2*q3.Not() + q0*q1.Not()*q2.Not()*q3.Not()
        Q0 = q0.Not()*q1.Not()*q2.Not()*q3.Not()

        q0 = f0.Operate(Q0,LogicBit(0),Clk)
        q1 = f1.Operate(Q1,LogicBit(0),Clk)
        q2 = f2.Operate(Q2,LogicBit(0),Clk)
        q3 = f3.Operate(Q3,LogicBit(0),Clk)
        Printer([q0,q1,q2,q3])

        reg1.Act([q0,q1,q2,q3,bit4,bit5,bit6,bit7],LogicBit(1),LogicBit(0),Clk)
        Printer(reg1.Read())

clk = Clock(flogic)
clk.start() # inicializar clock
#key = Keyboard(clk)
#key.start() # inicializar teclado