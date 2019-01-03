#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.logic import *
from logicbit.clock import *
from logicbit.keyboard import *

LogicBit.Symbolic = True

a=LogicBit(0,"a")
b=LogicBit(1,"b")
c=LogicBit(0)
d=a+b+c.Not()
print(d.Not().GetSymbol())
