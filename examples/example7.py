#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.logic import *
from logicbit.clock import *
from logicbit.keyboard import *

""""Synchronous counter
0000
1000
0110
0100
0010
0000
"""

def flogic(clock):
    b0 = LogicBit(0,"b0")
    b1 = LogicBit(1,"b1")
    b2 = LogicBit(1,"b2")

    c1 = b0 * b1
    c2 = b1 * b2 + c1
    c3 = LogicBit(1,"m2")

clk = Clock(flogic,1,2)
clk.start() # initialize clock
#key = Keyboard(clk)
#key.start() # initialize keyboard