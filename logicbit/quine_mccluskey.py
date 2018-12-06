#!/usr/bin/python
# -*- coding: UTF-8 -*-

import numpy as np

# Author Cleoner S. Pietralonga
# e-mail: cleonerp@gmail.com
# Apache License

class Quine_mcCluskey:
    def __init__(self, trueTable):
        self.trueTable = trueTable

    def BinList(self, n):
        list = []
        for i in xrange(2**n):
            b = bin(i)[2:].zfill(n) # value in binary, ex: i=1, n=4 -> '0001'
            list.append(b)
        return list

    def TextToArrayBin(self, table):
        list=[int(i, base=2) for i in table]
        size = len(table[0])
        tmp = sorted(list, key=int, reverse=False) # values in ascending order
        array = [np.array([int(bin(j)[2:].zfill(size)[i]) for i in range(size)]) for j in tmp] # binary value in list exp: Line=3, size=4 [0,0,1,1]
        return array

    def Count(self, result):
        cnt=0
        for value in result:
            if(value == -1 or value == 2):
                cnt+=1
        return cnt

    def RemoveIndex(self, listIndex, i):
        try:
            listIndex.remove(i)
        except:
            pass

    def Interaction(self, num):
        count = 0
        tmp = []
        index = list(range(len(self.trueTable)))
        for i in range(len(self.trueTable)):
            for j  in range(i,len(self.trueTable)):
                result = self.trueTable[i]-self.trueTable[j]+self.trueTable[i] # value0-value1+value0
                if(self.Count(result)==num):
                    #if(not any(np.array_equal(result, j) for j in tmp)):
                    tmp.append(result)
                    count+=1
                    self.RemoveIndex(index, i)
                    self.RemoveIndex(index, j)
                    print(i,j,result)
        print(index)
        for i in index:
            self.minTable.append(self.trueTable[i])
        if(count == 0):
            tmp = self.trueTable
        return tmp,count

    def Compute(self):
        inter = 0
        self.trueTable = self.TextToArrayBin(self.trueTable)
        self.minTable = []
        while True:
            inter+=1
            self.trueTable, count = self.Interaction(inter)
            print(inter)
            if (count == 0):
                break;
        print(self.minTable)

