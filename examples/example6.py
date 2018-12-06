#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.logic import *
from logicbit.clock import *
from logicbit.keyboard import *

class IR: # instruction register
    def __init__(self):
        self.__reg = Register8b()
        self.__tristate = TristateBuffer()

    def Act(self, Bus, IRIn, IROut, Clr, Clk):
        Out = self.__reg.Act(Bus, IRIn, Clk, Clr)
        Dir = LogicBit(1)
        LSB = [Out[0],Out[1],Out[2],Out[3]]
        MSB = [Out[4],Out[5],Out[6],Out[7]]
        A = LSB+[LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0)]
        [A,B] = self.__tristate.Buffer(A, Bus, Dir, IROut) # Dir=1 and IROut=1 -> puts A in B
        return B,MSB # B=Bus, MSB goes to the instruction decoder

    def Read(self):
        return self.__reg.Read()

class PC4bTris8b: # Program counter of 4 bits with tri-state
    def __init__(self):
        self.__pc4b = Counter4b()
        self.__tristate = TristateBuffer()

    def Act(self, EInc, EOut, Bus, Load, Clr, Clk):
        [q0, q1, q2, q3] = self.__pc4b.Act(EInc, Bus[0:4], Load, Clr, Clk)
        Dir = LogicBit(1)
        A = [q0, q1, q2, q3, Bus[4], Bus[5], Bus[6], Bus[7]]
        [A,B] = self.__tristate.Buffer(A, Bus, Dir, EOut) # Dir=1 and EOut=1 -> puts A in B
        return B

class MarRegister: # memory address register
    def __init__(self):
        self.__reg = Register4b() # 4-bits register

    def Act(self, Bus, MarIn, Clr, Clk):
        value = self.__reg.Act(Bus, MarIn, Clk, Clr)
        return value

    def Read(self):
        return self.__reg.Read()

class AccRegister: # accumulator register
    def __init__(self):
        self.__reg = RegTris8b()

    def Act(self, Bus, AccIn, AccOut, Clr, Clk):
        Bus = self.__reg.Act(Bus, AccIn, AccOut, Clr, Clk)
        return Bus

    def Read(self):
        return self.__reg.Read()

class B_Register: # B register
    def __init__(self):
        self.__reg = RegTris8b()

    def Act(self, Bus, AccIn, AccOut, Clr, Clk):
        Bus = self.__reg.Act(Bus, AccIn, AccOut, Clr, Clk)
        return Bus

    def Read(self):
        return self.__reg.Read()

def flogic(clock):

    Bus = [LogicBit(0) for bit in range(8)] # initializes bits of the Bus with 0
    Pc = PC4bTris8b()         # program counter of 4 bits with tri-state of 8-bits
    Mar = MarRegister()       # memory address register
    Ram = RAMTris(4,8)        # RAM memory, 4 bits address and 8 bits of data
    Acc = AccRegister()       # accumulator register
    B = B_Register()          # B register
    Ir = IR()                 # instruction register
    Alu = ALU8bTris()         # 8-bit arithmetic and logic unit

    # Word
    PcInc = LogicBit(0)       # enable counter
    PcOut = LogicBit(0)
    Jump = LogicBit(0)        # load bits into 0
    AccIn = LogicBit(0)
    AccOut = LogicBit(0)
    AddSub = LogicBit(0)
    Alu0 = LogicBit(0)
    Alu1 = LogicBit(0)
    AluOut = LogicBit(0)
    We = LogicBit(0)
    RamOut = LogicBit(0)
    Reset = LogicBit(0)
    MarIn = LogicBit(0)

    #t1 = [LogicBit(1), LogicBit(0), LogicBit(1), LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(1), LogicBit(0)]
    #t2 = [LogicBit(1), LogicBit(1), LogicBit(1), LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(1), LogicBit(0)]
    #S = Alu.Act(A,B,1)

    while(clock.GetState()):
        Clk = clock.GetClock()

        Bus = Pc.Act(PcInc, PcOut, Bus, Jump, Reset, Clk)
        Mar.Act(Bus[0:4], MarIn, Reset, Clk)
        Bus = Ram.Act(Mar.Read(), Bus, We, RamOut, Reset, Clk)
        Bus = Acc.Act(Bus, AccIn, AccOut, Reset, Clk)
        Bus = Alu.Act(Acc.Read(), B.Read(), Bus, AddSub, Alu0, Alu1, AluOut)

        if (Clk == 1):
            print(str(Bus[7]), str(Bus[6]), str(Bus[5]), str(Bus[4]), str(Bus[3]), str(Bus[2]), str(Bus[1]), str(Bus[0]))

clk = Clock(flogic,1,2)
clk.start() # initialize clock
#key = Keyboard(clk)
#key.start() # initialize keyboard