#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.logic import *
from logicbit.clock import *
from logicbit.utils import *
from logicbit.keyboard import *


class IR: # instruction register
    def __init__(self):
        self.__reg = Register8b()
        self.__tristate = TristateBuffer()

    def Act(self, Bus, IRIn, IROut, Reset, Clk):
        Out = self.__reg.Act(Bus, IRIn, Reset, Clk)
        Dir = LogicBit(1)
        LSB = [Out[0],Out[1],Out[2],Out[3]]
        MSB = [Out[4],Out[5],Out[6],Out[7]]
        A = LSB+[LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0)]
        [A,B] = self.__tristate.Buffer(A, Bus, Dir, IROut) # Dir=1 and IROut=1 -> puts A in B
        return B,MSB # B=Bus, MSB goes to the instruction decoder

    def Read(self):
        return self.__reg.Read()

class InstDecoder: # instruction decoder
    def __init__(self):
        self.__dec = Decoder()
        self.__cnt = Counter4b()
        self.__EndCycle = LogicBit(1)

    def Act(self, Word, Code, Clk):
        nClk = LogicBit(Clk).Not()
        Input = [LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0)]
        CntBits = self.__cnt.Act(Input, LogicBit(1), LogicBit(1), self.__EndCycle, nClk) # EndCycle reset Counter
        Cycles = self.__dec.Act(CntBits)
        self.__EndCycle = Cycles[5].Not() # Reset counter on cycle 5
        Word.PcOut = Word.MarIn = Cycles[0]
        Word.RamOut = Word.IrIn = Word.PcInc = Cycles[1]

        print("Cycles:")
        Printer(Cycles)
        return Word

class PC4bTris8b: # Program counter of 4 bits with tri-state
    def __init__(self):
        self.__pc4b = Counter4b()
        self.__tristate = TristateBuffer()

    def Act(self, Bus, EInc, EOut, nLoad, nReset, Clk):
        [q0, q1, q2, q3] = self.__pc4b.Act(Bus[0:4], EInc, nLoad, nReset, Clk)
        Dir = LogicBit(1)
        A = [q0, q1, q2, q3, Bus[4], Bus[5], Bus[6], Bus[7]]
        [A,B] = self.__tristate.Buffer(A, Bus, Dir, EOut) # Dir=1 and EOut=1 -> puts A in B
        return B

    def Read(self):
        return self.__pc4b.Read()

class MarRegister: # memory address register
    def __init__(self):
        self.__reg = Register4b() # 4-bits register

    def Act(self, Bus, MarIn, Reset, Clk):
        value = self.__reg.Act(Bus, MarIn, Reset, Clk)
        return value

    def Read(self):
        return self.__reg.Read()

class AccRegister: # accumulator register
    def __init__(self):
        self.__reg = RegTris8b()

    def Act(self, Bus, AccIn, AccOut, Reset, Clk):
        Bus = self.__reg.Act(Bus, AccIn, AccOut, Reset, Clk)
        return Bus

    def Read(self):
        return self.__reg.Read()


class Word:
    def __init__(self):
        self.Reset = LogicBit(0)    # Reset all
        self.PcInc = LogicBit(0)    # Enable increment of the Counter
        self.PcOut = LogicBit(0)    # Puts PC on Bus
        self.Jump = LogicBit(0)     # Load Bus into PC
        self.AccIn = LogicBit(0)    # Load Bus into accumulator register
        self.AccOut = LogicBit(0)   # Puts Acc into Bus
        self.BIn = LogicBit(0)      # Load Bus into B register
        self.CIn = LogicBit(0)      # Load Bus into C register
        self.SumSub = LogicBit(0)   # Enable sum operation in 0, and subtraction in 1
        self.Alu0 = LogicBit(0)
        self.Alu1 = LogicBit(0)
        self.AluOut = LogicBit(0)
        self.We = LogicBit(0)
        self.MarIn = LogicBit(0)
        self.RamOut = LogicBit(0)
        self.IrIn = LogicBit(0)
        self.IrOut = LogicBit(0)


def flogic(clock):

    Bus = [LogicBit(0) for bit in range(8)] # initializes bits of the Bus with 0
    Pc = PC4bTris8b()         # program counter of 4 bits with tri-state of 8-bits
    Mar = MarRegister()       # memory address register
    Ram = RAMTris(4,8)        # RAM memory, 4 bits address and 8 bits of data
    Acc = AccRegister()       # accumulator register
    B = Register8b()          # B register
    C = Register8b()          # B register
    Alu = ALU8bTris()         # 8-bit arithmetic and logic unit
    Ir = IR()                 # instruction register
    InstDec = InstDecoder()   # instruction decoder

    w = Word() # Control word

    # test -> write program in ram
    byte0 = [LogicBit(1),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(1),LogicBit(0)]
    byte1 = [LogicBit(0),LogicBit(1),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(1)]
    byte2 = [LogicBit(1),LogicBit(1),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(1),LogicBit(0)]
    byte3 = [LogicBit(0),LogicBit(0),LogicBit(1),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(1)]
    byte4 = [LogicBit(1),LogicBit(0),LogicBit(1),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(1),LogicBit(0)]
    byte5 = [LogicBit(0),LogicBit(1),LogicBit(1),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(1)]
    byte6 = [LogicBit(1),LogicBit(1),LogicBit(1),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(1),LogicBit(0)]
    byte7 = [LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(1),LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(1)]
    data = [byte0, byte1, byte2, byte3, byte4, byte5, byte6, byte7]
    for value, addr in zip(data, range(len(data))):
        addr = Utils.IntToBinList(addr,4)
        for Clk in range(2):
            Ram.Act(value, addr, LogicBit(1), LogicBit(0), LogicBit(0), Clk)

    cnt=0
    while(clock.GetState()):
        Clk = clock.GetClock()
        cnt+=1
        print("Clock:"+str(Clk)+", cnt="+str(cnt))

        ''' Ciclo 1 -> PcOut e MarIn
            Ciclo 2 -> RamOut, IrIn e PcInc.
            The control bits will be triggered on the falling edge of the clock.
        '''
        Bus = Pc.Act(Bus, w.PcInc, w.PcOut, w.Jump.Not(), w.Reset.Not(), Clk) # In Pc, Jump and Reset works in 0
        Mar.Act(Bus[0:4], w.MarIn, w.Reset, Clk)
        Bus = Ram.Act(Bus, Mar.Read(), w.We, w.RamOut, LogicBit(0), Clk)
        Bus = Acc.Act(Bus, w.AccIn, w.AccOut, w.Reset, Clk)
        B.Act(Bus, w.BIn, w.Reset, Clk)
        C.Act(Bus, w.CIn, w.Reset, Clk)
        Bus = Alu.Act(Bus, Acc.Read(), B.Read(), w.SumSub, w.Alu0, w.Alu1, w.AluOut)
        Bus, Code = Ir.Act(Bus, w.IrIn, w.IrOut, w.Reset, Clk)
        InstDec.Act(w, Code, Clk)

        #if (Clk == 1):
        Printer(Bus)

clk = Clock(flogic,1,3) # two samples per state
clk.start() # initialize clock
#key = Keyboard(clk)
#key.start() # initialize keyboard