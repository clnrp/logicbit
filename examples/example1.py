from logicbit.logic import *
from logicbit.clock import *

""""Contador sincrono
0000
1000
0110
0100
0010
0000
"""

def flogic(clock):
    f0 = Flipflop("D","UP")
    f1 = Flipflop("D","UP")
    f2 = Flipflop("D","UP")
    f3 = Flipflop("D","UP")

    q0 = f0.GetQ()
    q1 = f1.GetQ()
    q2 = f2.GetQ()
    q3 = f3.GetQ()

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

clk = Clock(flogic,1,2)
clk.start()