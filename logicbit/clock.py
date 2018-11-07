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
        self.Th_Clk = True
        self.Clk = 0
        self.CntClk = 0
        self.Frequency = Frequency
        self.Samples = Samples
        self.Method = Method

    def run(self):
        try:
            self.Method(self)
        except Exception as ex:
            print(str(ex))

    def getState(self):
        return  self.Th_Clk

    def getClock(self):
        time.sleep(1./(2*self.Samples*self.Frequency))
        self.CntClk+=1
        if (self.CntClk == self.Samples):
            if(self.Clk  == 0):
                self.Clk = 1
            else:
                self.Clk = 0
            self.CntClk = 0
        return  self.Clk

    def TurnOff(self):
        self.Th_Clk = False