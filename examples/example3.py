from logicbit.logic import *
from logicbit.clock import *


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

    reg1 = Register_8bits()

    while(clock.getState()):
        Clk = clock.getClock()

        Q3 = LogicBit(0)
        Q2 = q0.Not()*q1*q2.Not()*q3.Not() + q0*q1.Not()*q2.Not()*q3.Not()
        Q1 = q0.Not()*q1*q2*q3.Not() + q0*q1.Not()*q2.Not()*q3.Not()
        Q0 = q0.Not()*q1.Not()*q2.Not()*q3.Not()

        q0 = f0.Operate(Q0,Clk)
        q1 = f1.Operate(Q1,Clk)
        q2 = f2.Operate(Q2,Clk)
        q3 = f3.Operate(Q3,Clk)
        print(Clk,str(q0),str(q1),str(q2),str(q3))

        reg1.Act([q0,q1,q2,q3,bit4,bit5,bit6,bit7],Clk)
        print(str(reg1.Read()[0]), str(reg1.Read()[1]), str(reg1.Read()[2]), str(reg1.Read()[3])) # leitura do registrador

clk = Clock(flogic)
clk.start()
