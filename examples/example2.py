#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.quine_mccluskey import *

trueTable = ['0000', '0001', '0100', '0101', '1111']

qmc = Quine_McCluskey(trueTable)
qmc.Compute()

def v(a1, a2, a3, a4): # antes
    return bool(((not a1) and (not a2) and (not a3) and (not a4)) or ((not a1) and (not a2) and (not a3) and a4) or (
                (not a1) and a2 and (not a3) and (not a4)) or ((not a1) and a2 and (not a3) and a4) or (
                            a1 and a2 and a3 and a4))

def v(a1, a2, a3, a4): # depois
    return bool((a1 and a2 and a3 and a4) or ((not a1) and (not a3)))

for i in range(16):
    print(qmc.Bin2(i,4), v((i >> 3) & 0x1, (i >> 2) & 0x1, (i >> 1) & 0x1, (i >> 0) & 0x1))