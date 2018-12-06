#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.quine_mccluskey import *

trueTable = ['0000','0001','0100','0101','1111']
#trueTable = ['0011','0000','0110','1011']

quine_mcCluskey = Quine_mcCluskey(trueTable)
quine_mcCluskey.Compute()