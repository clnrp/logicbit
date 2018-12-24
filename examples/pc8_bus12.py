#!/usr/bin/python
# -*- coding: UTF-8 -*-

from logicbit.logic import *
from logicbit.clock import *
from logicbit.utils import *
from logicbit.keyboard import *

class Reg8bTris12b:
    def __init__(self):
        self.__reg = Register8b()
        self.__tristate = TristateBuffer()

    def Act(self, Bus, EIn, EOut, Reset, Clk):
        A = self.__reg.Act(Bus[0:8], EIn, Reset, Clk)
        Dir = LogicBit(1)
        A = A + [LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0)]
        [A,B] = self.__tristate.Buffer(A, Bus, Dir, EOut) # Dir=1 and EOut=1 -> put A in B
        return B

    def Read(self):
        return self.__reg.Read()

class PC8bTris: # Program counter of 8 bits with tri-state
    def __init__(self):
        self.__pc8b = Counter8b()
        self.__tristate = TristateBuffer()

    def Act(self, Bus, EInc, EOut, Load, Reset, Clk):
        A = self.__pc8b.Act(Bus[0:8], EInc, Load, Reset, Clk)
        Dir = LogicBit(1)
        A = A + [LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0)]
        [A,B] = self.__tristate.Buffer(A, Bus, Dir, EOut) # Dir=1 and EOut=1 -> put A in B
        return B

    def Read(self):
        return self.__pc8b.Read()

class ALU8bTris12b:
    def __init__(self):
        self.__Alu = ALU8b()
        self.__tristate = TristateBuffer()

    def Act(self, Bus, A, B, Flags, SumSub, Alu0, Alu1, AluOut):
        A = self.__Alu.Act(A, B, SumSub, Alu0, Alu1)
        Dir = LogicBit(1)
        A = A + [LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0)]
        [A,B] = self.__tristate.Buffer(A, Bus, Dir, AluOut) # Dir=1 and EOut=1 -> put A in B
        return B

class MarRegister: # memory address register
    def __init__(self):
        self.__reg = Register8b() # 8-bits register

    def Act(self, Bus, MarIn, Reset, Clk):
        value = self.__reg.Act(Bus, MarIn, Reset, Clk)
        return value

    def Read(self):
        return self.__reg.Read()

class IR: # instruction register
    def __init__(self):
        self.__reg = Register(12) # 12 bits register
        self.__tristate = TristateBuffer()

    def Act(self, Bus, IRIn, IROut, Reset, Clk):
        Out = self.__reg.Act(Bus, IRIn, Reset, Clk)
        Dir = LogicBit(1)
        LSB = Out[0:8]  # 8 bits
        MSB = Out[8:12] # 4 bits
        A = LSB + [LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0)]
        [A,B] = self.__tristate.Buffer(A, Bus, Dir, IROut) # Dir=1 and IROut=1 -> put A in B
        return B,MSB # B=Bus, MSB goes to the instruction decoder

    def Read(self):
        return self.__reg.Read()

class InstDecoder: # instruction decoder
    def __init__(self):
        self.__CycleDec = BinaryDecoder()
        self.__InstrDec = BinaryDecoder()
        self.__cnt = Counter4b()
        self.__EndCycle = LogicBit(1)

    def Act(self, Word, Code, Flags, Clk):
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
        self.PcOut = LogicBit(0)    # Put PC on Bus
        self.Jump = LogicBit(0)     # Load Bus into PC
        self.AccIn = LogicBit(0)    # Load Bus into accumulator register
        self.AccOut = LogicBit(0)   # Put Acc into Bus
        self.BIn = LogicBit(0)      # Load Bus into B register
        self.CIn = LogicBit(0)      # Load Bus into C register
        self.SumSub = LogicBit(0)   # Enable sum operation in 0, and subtraction in 1
        self.Alu0 = LogicBit(0)     #
        self.Alu1 = LogicBit(0)     #
        self.AluOut = LogicBit(0)   # Put ALU data into Bus
        self.We = LogicBit(0)       # Write/Read Ram
        self.MarIn = LogicBit(0)    # Load Bus into MAR register
        self.RamOut = LogicBit(0)   # Put Ram data into Bus
        self.IrIn = LogicBit(0)     # Load Bus into IR register
        self.IrOut = LogicBit(0)    # Put IR register into Bus


def flogic(clock):

    Bus = [LogicBit(0) for bit in range(12)] # initializes 12 bits of the Bus with 0
    Pc = PC8bTris()           # program counter of 8 bits with tri-state
    Mar = MarRegister()       # memory address register
    Ram = RAMTris(8,12)       # RAM memory, 8 bits address and 12 bits of data
    A = Reg8bTris12b()        # Accumulator register
    B = Register8b()          # B register
    F = Register8b()          # Flag register
    C = Register8b()          # C register
    Alu = ALU8bTris12b()      # 8-bit arithmetic and logic unit
    Ir = IR()                 # instruction register
    InstDec = InstDecoder()   # instruction decoder

    w = Word() # Control word

    # test -> write program in ram
    byte00 = Utils.VecBinToPyList([0,0,0,1,0,0,0,0,1,0,1,0]) # 0000 LDA 0Ah
    byte01 = Utils.VecBinToPyList([0,0,1,0,0,0,0,0,1,0,1,1]) # 0001 SUM 0Bh
    byte02 = Utils.VecBinToPyList([0,1,0,0,0,0,0,0,0,0,0,0]) # 0010 LDC
    byte03 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,0,0,0]) # 0011
    byte04 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,0,0,0]) # 0100
    byte05 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,0,0,0]) # 0101
    byte06 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,0,0,0]) # 0110
    byte07 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,0,0,0]) # 0111
    byte08 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,0,0,0]) # 1000
    byte09 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,0,0,0]) # 1001
    byte10 = Utils.VecBinToPyList([0,0,0,0,0,0,0,1,0,1,0,1]) # 1010
    byte11 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,1,1,0]) # 1011
    byte12 = Utils.VecBinToPyList([0,0,0,0,0,0,1,0,0,1,1,0]) # 1100
    data = [byte00, byte01, byte02, byte03, byte04, byte05, byte06, byte07, byte08, byte09, byte10, byte11, byte12]
    for value, addr in zip(data, range(len(data))):
        addr = Utils.BinValueToPyList(addr,8)
        for Clk in range(2):
            Ram.Act(value, addr, LogicBit(1), LogicBit(0), LogicBit(0), Clk)

    cnt=0
    while(clock.GetState()):
        Clk = clock.GetClock()
        cnt+=1
        print("Clock:"+str(Clk)+", cnt="+str(cnt))

        Bus = Pc.Act(Bus, w.PcInc, w.PcOut, w.Jump, w.Reset, Clk)           # Program counter, 8 bits
        Mar.Act(Bus[0:8], w.MarIn, w.Reset, Clk)                            # Memory address 8 bits register
        Bus = Ram.Act(Bus, Mar.Read(), w.We, w.RamOut, LogicBit(0), Clk)    # RAM memory, 8 bits address and 12 bits of data
        Bus = A.Act(Bus, w.AccIn, w.AccOut, w.Reset, Clk)
        B.Act(Bus[0:8], w.BIn, w.Reset, Clk)
        C.Act(Bus[0:8], w.CIn, w.Reset, Clk)
        Bus = Alu.Act(Bus, A.Read(), B.Read(), F, w.SumSub, w.Alu0, w.Alu1, w.AluOut)
        Bus, Code = Ir.Act(Bus, w.IrIn, w.IrOut, w.Reset, Clk)             # Instruction register, 12 bits
        InstDec.Act(w, Code, F, Clk)

        #if (Clk == 1):
        Printer(A.Read(),"A")
        Printer(C.Read(),"C")
        Printer(Bus,"Bus")

clk = Clock(flogic,1,3) # two samples per state
clk.start() # initialize clock
#key = Keyboard(clk)
#key.start() # initialize keyboard