#!/usr/bin/python
# encoding: utf-8

from threading import Thread
import time

# Author Cleoner S. Pietralonga
# e-mail: cleonerp@gmail.com
# Apache License

class Clock(Thread):
    def __init__(self, Method, Frequency=1, Samples=1):
        Thread.__init__(self)
        self.__th_clk = True
        self.__run = True
        self.__next = False
        self.__Clk = 1
        self.__CntClk = 0
        self.__Frequency = Frequency
        self.__Samples = Samples
        self.__Method = Method

    def run(self):
        try:
            self.__Method(self)
        except Exception as ex:
            print(str(ex))

    def GetState(self):
        return  self.__th_clk

    def GetClock(self):
        time.sleep(1. / (2 * self.__Samples * self.__Frequency)) # sample delays
        if(self.__run):
            self.__CntClk+=1
            if (self.__CntClk == self.__Samples): # number of samples per clock state
                if(self.__Clk  == 0):
                    self.__Clk = 1
                else:
                   self.__Clk = 0
                self.__CntClk = 0
        else:
            while(self.__next == False and not self.__run and self.__th_clk): # keep the method waiting
                 time.sleep(1)
            self.__next = False
        return  self.__Clk

    def TurnOff(self):
        self.__th_clk = False

    def Next(self): # toggle the clock
        self.__next = True
        self.__run = False
        self.__Clk = int(not self.__Clk)

    def Pause(self):
        self.__run = False

    def Run(self): # stand-alone mode
        self.__run = True