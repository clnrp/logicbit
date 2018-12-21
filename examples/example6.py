#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.logic import *
from logicbit.clock import *
from logicbit.utils import *
from logicbit.keyboard import *


class PC4bTris8b: # Program counter of 4 bits with tri-state
    def __init__(self):
        self.__pc4b = Counter4b()
        self.__tristate = TristateBuffer()

    def Act(self, Bus, EInc, EOut, Load, Reset, Clk):
        [q0, q1, q2, q3] = self.__pc4b.Act(Bus[0:4], EInc, Load, Reset, Clk)
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
        self.__CycleDec = BinaryDecoder()
        self.__InstrDec = BinaryDecoder()
        self.__cnt = Counter4b()
        self.__EndCycle = LogicBit(1)

    def Act(self, Word, Code, Clk):
        nClk = LogicBit(Clk).Not()
        Input = [LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0)]
        CntBits = self.__cnt.Act(Input, LogicBit(1), LogicBit(0), self.__EndCycle, nClk) # EndCycle reset Counter
        Cycle = self.__CycleDec.Act(CntBits)
        [NOP,LDA,SUM,SUB,LDC] = self.__InstrDec.Act(Code)[:5]
        self.__EndCycle = Cycle[5]+Cycle[4]*LDA+Cycle[3]*LDC   # Reset counter
        Word.PcOut  = Cycle[0]
        Word.IrOut = Cycle[2]*(LDA + SUM)
        Word.MarIn = Cycle[0] + Cycle[2]*(LDA + SUM)
        Word.RamOut = Cycle[1] + Cycle[3]*(LDA + SUM)
        Word.IrIn = Cycle[1]
        Word.PcInc = Cycle[1]
        Word.AccIn = Cycle[3]*LDA+Cycle[4]*SUM
        Word.AccOut = Cycle[2]*LDC
        Word.BIn = Cycle[3]*SUM
        Word.CIn = Cycle[2]*LDC
        Word.AluOut = Cycle[4]*SUM
        Word.SumSub = Cycle[4]*(SUM.Not()+SUB)
        Word.Alu0 = LogicBit(0)
        Word.Alu1 = LogicBit(0)
        ''' Cycle 0 -> PcOut e MarIn
            Cycle 1 -> RamOut, IrIn e PcInc.
            The control bits will be triggered on the falling edge of the clock.
            NOP 0000
            LDA 0001, 2 -> IrOut, MarIn; 3 -> RamOut, AccIn
            SUM 0010, 2 -> IrOut, MarIn; 3 -> RamOut, BIn; 4 -> SumSub=0, AluOut, AccIn
            SUB 0011, 2 -> IrOut, MarIn; 3 -> RamOut, BIn; 4 -> SumSub=1, AluOut, AccIn
            LDC 0100, 2 -> AccOut, CIn
        '''
        print("Cycles:")
        Printer(Cycle)
        return Word

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
        self.Alu0 = LogicBit(0)     #
        self.Alu1 = LogicBit(0)     #
        self.AluOut = LogicBit(0)   # Puts ALU data into Bus
        self.We = LogicBit(0)       # Write/Read Ram
        self.MarIn = LogicBit(0)    # Load Bus into MAR register
        self.RamOut = LogicBit(0)   # Puts Ram data into Bus
        self.IrIn = LogicBit(0)     # Load Bus into IR register
        self.IrOut = LogicBit(0)    # Puts IR register into Bus


def flogic(clock):

    Bus = [LogicBit(0) for bit in range(8)] # initializes bits of the Bus with 0
    Pc = PC4bTris8b()         # program counter of 4 bits with tri-state of 8-bits
    Mar = MarRegister()       # memory address register
    Ram = RAMTris(4,8)        # RAM memory, 4 bits address and 8 bits of data
    A = RegTris8b()           # Accumulator register
    B = Register8b()          # B register
    C = Register8b()          # C register
    Alu = ALU8bTris()         # 8-bit arithmetic and logic unit
    Ir = IR()                 # instruction register
    InstDec = InstDecoder()   # instruction decoder

    w = Word() # Control word

    # test -> write program in ram
    byte00 = Utils.VecBinToPyList([0,0,0,1,1,0,1,0]) # 0000 LDA 0Ah
    byte01 = Utils.VecBinToPyList([0,0,1,0,1,0,1,1]) # 0001 SUM 0Bh
    byte02 = Utils.VecBinToPyList([0,1,0,0,0,0,0,0]) # 0010 LDC
    byte03 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0]) # 0011
    byte04 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0]) # 0100
    byte05 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0]) # 0101
    byte06 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0]) # 0110
    byte07 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0]) # 0111
    byte08 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0]) # 1000
    byte09 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0]) # 1001
    byte10 = Utils.VecBinToPyList([0,0,0,1,0,1,0,1]) # 1010
    byte11 = Utils.VecBinToPyList([0,0,0,0,0,1,1,0]) # 1011
    byte12 = Utils.VecBinToPyList([0,0,1,0,0,1,1,0]) # 1100
    data = [byte00, byte01, byte02, byte03, byte04, byte05, byte06, byte07, byte08, byte09, byte10, byte11, byte12]
    for value, addr in zip(data, range(len(data))):
        addr = Utils.BinValueToPyList(addr,4)
        for Clk in range(2):
            Ram.Act(value, addr, LogicBit(1), LogicBit(0), LogicBit(0), Clk)

    cnt=0
    while(clock.GetState()):
        Clk = clock.GetClock()
        cnt+=1
        print("Clock:"+str(Clk)+", cnt="+str(cnt))

        Bus = Pc.Act(Bus, w.PcInc, w.PcOut, w.Jump, w.Reset, Clk)           # Program counter
        Mar.Act(Bus[0:4], w.MarIn, w.Reset, Clk)                            # Memory address register
        Bus = Ram.Act(Bus, Mar.Read(), w.We, w.RamOut, LogicBit(0), Clk)
        Bus = A.Act(Bus, w.AccIn, w.AccOut, w.Reset, Clk)
        B.Act(Bus, w.BIn, w.Reset, Clk)
        C.Act(Bus, w.CIn, w.Reset, Clk)
        Bus = Alu.Act(Bus, A.Read(), B.Read(), w.SumSub, w.Alu0, w.Alu1, w.AluOut)
        Bus, Code = Ir.Act(Bus, w.IrIn, w.IrOut, w.Reset, Clk)
        InstDec.Act(w, Code, Clk)

        #if (Clk == 1):
        Printer(A.Read(),"A")
        Printer(C.Read(),"C")
        Printer(Bus,"Bus")

clk = Clock(flogic,1,3) # two samples per state
clk.start() # initialize clock
#key = Keyboard(clk)
#key.start() # initialize keyboard