#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Author Cleoner S. Pietralonga
# e-mail: cleonerp@gmail.com
# Apache License

from logicbit.logic import *

class Printer:
    def __init__(self, values=None, name=""):
        if ('list' in str(type(values))): # check if it's a list
            values = list(values)         # copy list
            values.reverse()
            lstr = [str(value) for value in values]
            print(str(name)+"-"+str(lstr))

class Utils:
    @staticmethod
    def BinValueToPyList(value, size):
        t = [int(bin(value)[2:].zfill(size)[i]) for i in range(size)] # binary value in list exp: value=3, size=4 [0,0,1,1]
        bits = [LogicBit(bit) for bit in t] # list of LogicBits
        bits.reverse()
        return bits

    @staticmethod
    def VecBinToPyList(values): # int(value, base=2)
        bits = [LogicBit(bit) for bit in values] # list of LogicBits
        bits.reverse()
        return bits

    @staticmethod
    def BinListToPyList(values): # the bit least significant left
        values = list(values)    # copy list
        values.reverse()
        return values

    @staticmethod
    def TextToBinArray(text):
        list_text = text.split("\n")
        list_text.remove('')
        list = [int(i, base=2) for i in list_text]
        size = len(list_text[0])
        array = [Utils.VecBinToPyList([int(bin(j)[2:].zfill(size)[i]) for i in range(size)]) for j in list]
        return array