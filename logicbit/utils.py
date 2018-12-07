#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Author Cleoner S. Pietralonga
# e-mail: cleonerp@gmail.com
# Apache License

from logicbit.logic import *

class Printer:
    def __init__(self, values):
        if ('list' in str(type(values))): # check if it's a list
            values = list(values) # copy list
            values.reverse()
            lstr = [str(value) for value in values]
            print(lstr)

class Utils:
    @staticmethod
    def BinValueToPyList(value, size):
        t = [int(bin(value)[2:].zfill(size)[i]) for i in range(size)] # binary value in list exp: Line=3, size=4 [0,0,1,1]
        bits = [LogicBit(bit) for bit in t] # list of LogicBits
        bits.reverse()
        return bits

    @staticmethod
    def VecBinToPyList(values): #  int(value, base=2)
        bits = [LogicBit(bit) for bit in values] # list of LogicBits
        bits.reverse()
        return bits

    @staticmethod
    def BinListToPyList(values):
        values = list(values)  # copy list
        values.reverse()
        return values
