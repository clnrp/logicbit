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

    def Act(self, Bus, A, B, Word, F, SumSub, Alu0, Alu1, AluOut, Clk):
        A,CarryBorrow = self.__Alu.Act(A, B, SumSub, Alu0, Alu1)
        Dir = LogicBit(1)
        A = A + [LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0)]

        # Update F register
        Zero = A[7].Not()*A[6].Not()*A[5].Not()*A[4].Not()*A[3].Not()*A[2].Not()*A[1].Not()*A[0].Not()
        Mask = Utils.VecBinToPyList([0, 0, 0, 0, 0, 0, 1, 1])
        Flags = [Zero,CarryBorrow]+Utils.VecBinToPyList([0, 0, 0, 0, 0, 0])
        F.Act(Flags, Mask, Word.FIn, LogicBit(0), Clk)

        [A,B] = self.__tristate.Buffer(A, Bus, Dir, AluOut) # Dir=1 and EOut=1 -> put A in B
        return B

class MarRegister: # Memory address register
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
        Code = Out
        A = LSB + [LogicBit(0), LogicBit(0), LogicBit(0), LogicBit(0)]
        [A,B] = self.__tristate.Buffer(A, Bus, Dir, IROut) # Dir=1 and IROut=1 -> put A in B
        return B,Code # B=Bus, Code go to instruction decoder

    def Read(self):
        return self.__reg.Read()

class InstDecoder: # instruction decoder
    def __init__(self):
        self.__CycleDec = BinaryDecoder()
        self.__InstrDec = BinaryDecoder()
        self.__cnt = Counter4b()
        self.__EndCycle = LogicBit(1)

    def Act(self, Word, Code, F, Clk):
        nClk = Clk.Not()
        Flag = F.Read()
        OpCode = Code[8:12]
        Input = [LogicBit(0),LogicBit(0),LogicBit(0),LogicBit(0)]
        CntBits = self.__cnt.Act(Input, LogicBit(1), LogicBit(0), self.__EndCycle, nClk) # EndCycle reset Counter
        Cycle = self.__CycleDec.Act(CntBits)
        [NOP,JUMP,LDA,SUM,SUB,LDC,BTR] = self.__InstrDec.Act(OpCode)[:7]
        self.__EndCycle = Cycle[5] + Cycle[3]*(JUMP + LDA + LDC + BTR)   # Reset counter
        Word.PcOut  = Cycle[0]
        Word.IrOut = Cycle[2]*(JUMP + LDA + SUM + SUB)
        Word.MarIn = Cycle[0]
        Word.Jump = Cycle[2]*JUMP
        Word.RamOut = Cycle[1]
        Word.IrIn = Cycle[1]
        Word.PcInc = Cycle[1] + Cycle[2]*JUMP + Cycle[2]*BTR*(Code[0]*Flag[0]+Code[1]*Flag[1]+Code[2]*Flag[2]+Code[3]*Flag[3]+Code[4]*Flag[4]+Code[5]*Flag[5]+Code[6]*Flag[6]+Code[7]*Flag[7])
        Word.AccIn = Cycle[2]*LDA + Cycle[4]*(SUM + SUB)
        Word.AccOut = Cycle[2]*LDC
        Word.BIn = Cycle[2]*(SUM + SUB)
        Word.CIn = Cycle[2]*LDC
        Word.FIn = Cycle[3]*(SUM + SUB)
        Word.AluOut = Cycle[4]*(SUM + SUB)
        Word.SumSub = Cycle[4]*(SUM.Not() + SUB)
        Word.Alu0 = LogicBit(0)
        Word.Alu1 = LogicBit(0)

        ''' Cycle 0 -> PcOut e MarIn
            Cycle 1 -> RamOut, IrIn e PcInc.
            The control bits will be triggered on the falling edge of the clock.
            NOP  0000
            JUMP 0001, 2 -> IrOut, PcInc, Jump
            LDA  0010, 2 -> IrOut, AccIn
            SUM  0011, 2 -> IrOut, BIn; 3 -> FIn; 4 -> SumSub=0, AluOut, AccIn
            SUB  0100, 2 -> IrOut, BIn; 3 -> FIn; 4 -> SumSub=1, AluOut, AccIn
            LDC  0101, 2 -> AccOut, CIn
            BTR  0110, 2 -> PcInc # Opcode = 4bits, Register=4bits, Bit=3bits, SetClear=1  Max 16 register
        '''
        #Printer(Cycle,"Cycles")
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
        self.FIn = LogicBit(0)      # Change F register
        self.FOut = LogicBit(0)     # Put F register into Bus
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
    F = Register8b_Sb()       # Flag register
    C = Register8b()          # C register
    Alu = ALU8bTris12b()      # 8-bit arithmetic and logic unit
    Ir = IR()                 # instruction register
    InstDec = InstDecoder()   # instruction decoder

    w = Word() # Control word

    # test -> write program in ram
    byte00 = Utils.VecBinToPyList([0,0,1,0,1,1,1,1,1,1,0,0]) # 00 LDA fch
    byte01 = Utils.VecBinToPyList([0,0,1,1,0,0,0,0,0,0,0,1]) # 01 SUM 01h
    byte02 = Utils.VecBinToPyList([0,1,1,0,0,0,0,0,0,0,0,1]) # 03 BTR 01h
    byte03 = Utils.VecBinToPyList([0,0,0,1,0,0,0,0,0,0,0,1]) # 04 JUMP 01h
    byte04 = Utils.VecBinToPyList([0,0,1,1,0,0,0,0,0,0,1,1]) # 02 SUM 03h
    byte05 = Utils.VecBinToPyList([0,1,0,1,0,0,0,0,0,0,0,0]) # 05 LDC
    byte06 = Utils.VecBinToPyList([0,0,0,1,0,0,0,0,0,0,0,0]) # 06 JUMP 00h
    byte07 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,0,0,0]) # 07
    byte08 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,0,0,0]) # 08
    byte09 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,0,0,0]) # 09
    byte10 = Utils.VecBinToPyList([0,0,0,0,0,0,0,0,0,0,0,0]) # 0A
    data = [byte00, byte01, byte02, byte03, byte04, byte05, byte06, byte07, byte08, byte09, byte10]
    for value, addr in zip(data, range(len(data))):
        addr = Utils.BinValueToPyList(addr,8)
        for Clk in [LogicBit(0),LogicBit(1)]:
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
        Bus = Alu.Act(Bus, A.Read(), B.Read(), w, F, w.SumSub, w.Alu0, w.Alu1, w.AluOut, Clk)
        Bus, Code = Ir.Act(Bus, w.IrIn, w.IrOut, w.Reset, Clk)             # Instruction register, 12 bits
        InstDec.Act(w, Code, F, Clk)

        #if (Clk == 1):
        Printer(A.Read(),"A")
        Printer(B.Read(),"B")
        Printer(C.Read(),"C")
        Printer(F.Read(),"F")
        Printer(Pc.Read(),"Pc")
        Printer(Bus, "Bus")

clk = Clock(flogic,1,2) # two samples per state
clk.start() # initialize clock
#key = Keyboard(clk)
#key.start() # initialize keyboard