#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Author Cleoner S. Pietralonga
# e-mail: cleonerp@gmail.com
# Apache License

class LogicBit:
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __mul__(self, other): # And logic
        value = self.value and other.value
        return LogicBit(value)
    
    def __add__(self, other): # Or logic
        value = self.value or other.value
        return LogicBit(value)
    
    def __xor__(self, other): # OR-Exclusive logic
        value = self.value ^ other.value
        return LogicBit(value)

    def __eq__(self, other):
        return self.value == other
    
    def Not(self):
        value = not self.value
        return LogicBit(int(value))
    
    def Set(self, value):
        self.value = int(value)
        return LogicBit(value)
    
    def Get(self, type = 1): # if type = 0 return Not, otherwise return value
        if(type == 0):
            return self.Not()
        return LogicBit(self.value)

class Flipflop:
    def __init__(self, Type, Level):
        self.map = {"UP": 1, "DOWN": 0}
        self.Q = LogicBit(0)
        self.NotQ = LogicBit(1)
        self.Type = Type
        self.Level = Level
        self.Clk = int(not self.map[self.Level])

    def __D(self, D = None, Clk=None): # Q = D
        if(Clk == self.map[self.Level] and self.Clk == int(not self.map[self.Level]) and self.Clk != Clk):
            self.Q = D
            self.NotQ = D.Not()
            self.Clk = Clk
        elif(Clk == int(not self.map[self.Level])):
            self.Clk = Clk

    def __T(self, T = None, Clk=None): # T = 0 -> Q = Q; T = 1 -> Q = ~Q
        if(Clk == self.map[self.Level] and self.Clk == int(not self.map[self.Level]) and self.Clk != Clk):
            if (T == 1):
                 self.Q = self.NotQ
                 self.NotQ = self.Q.Not()
            self.Clk = Clk
        elif(Clk == int(not self.map[self.Level])):
            self.Clk = Clk

    def __SR(self, S=None, R=None, Clk=None):
        if (Clk == self.map[self.Level] and self.Clk == int(not self.map[self.Level]) and self.Clk != Clk):
            if(S == 1 and R == 0):
                self.Q = 1
                self.NotQ = self.Q.Not()
            elif(S == 0 and R == 1):
                self.Q = 0
                self.NotQ = self.Q.Not()
            elif (Clk == int(not self.map[self.Level])):
                self.Clk = Clk

    def __JK(self, J=None, K=None, Clk=None):
        if (Clk == self.map[self.Level] and self.Clk == int(not self.map[self.Level]) and self.Clk != Clk):
            if(J == 1 and K == 0):
                self.Q = 1
                self.NotQ = self.Q.Not()
            elif(J == 0 and K == 1):
                self.Q = 0
                self.NotQ = self.Q.Not()
            elif(J == 1 and K == 1):
                self.Q = self.NotQ
                self.NotQ = self.Q.Not()
        elif(Clk == int(not self.map[self.Level])):
            self.Clk = Clk

    def Act(self, Input = None, Reset=None, Clk=None):
        if (Reset == 1):
            self.Reset()
        elif(Input != None):
            if(self.Type == "D"):
                if('list' in str(type(Input)) and len(Input) == 1): # check if it's a list
                    D = Input[0]
                else:
                    D = Input
                self.__D(D, Clk)
            elif(self.Type == "T"): # Flip-flop Toggle
                if('list' in str(type(Input)) and len(Input) == 1): # check if it's a list
                    T = Input[0]
                else:
                    T = Input
                self.__T(T, Clk)
            elif(self.Type == "SR" and len(Input) == 2):
                S,R = Input
                self.__SR(S, R, Clk) # S = input[0] and R = input[1]
            elif(self.Type == "JK" and len(Input) == 2):
                J,K = Input
                self.__JK(J, K, Clk) # J = input[0] and K = input[1]
        return self.Q, self.NotQ

    def Operate(self, Input = None, Reset=None, Clk=None): # returns only Q
        return self.Act(Input, Reset, Clk)[0]

    def Set(self, Input = None, Reset=None, Clk=None):
        self.Act(Input, Reset, Clk)[0]

    def GetQ(self, Reset=None):
        return self.Act(None, Reset, None)[0]

    def GetNotQ(self, Reset=None):
        return self.Act(None, Reset, None)[1]

    def Reset(self):
        self.Q = LogicBit(0)
        self.NotQ = LogicBit(1)


class TristateBuffer:
    def Single(self, A, B, Ce = None):
        if(Ce == 1):      # puts A in B
            B = A
        return B
    
    def Buffer(self, A, B, Dir, Ce = None):
        if(Ce == 1):
            if(Dir == 1): # puts A in B
                B = A
            else:
                A = B     # puts B in A
        return [A, B]

class Decoder:
    def Act(self, Input):
        SizeIn = len(Input)
        SizeOut = 2**len(Input)
        Bits = [0]*SizeOut
        for iOut in range(SizeOut):
            t = [int(bin(iOut)[2:].zfill(SizeIn)[i]) for i in range(SizeIn)]  # binary value in list exp: Line=3, size=4 [0,0,1,1]
            value = Input[0].Get(t[SizeIn - 1])
            for i in range(1, SizeIn):
                value = value * Input[i].Get(t[SizeIn - 1 - i]) # product 'And' of LogicBit's
            Bits[iOut]=value
        return Bits

class Mux:
    def Mux16x8(self, Imput, Sel):
        a0,a1,a2,a3,a4,a5,a6,a7 = Imput[0]
        b0,b1,b2,b3,b4,b5,b6,b7 = Imput[1]
        c0 = Sel*a0 + Sel.Not()*b0
        c1 = Sel*a1 + Sel.Not()*b1
        c2 = Sel*a2 + Sel.Not()*b2
        c3 = Sel*a3 + Sel.Not()*b3
        c4 = Sel*a4 + Sel.Not()*b4
        c5 = Sel*a5 + Sel.Not()*b5
        c6 = Sel*a6 + Sel.Not()*b6
        c7 = Sel*a7 + Sel.Not()*b7
        return [c0,c1,c2,c3,c4,c5,c6,c7]

    def Mux24x8(self, Imput, Sel):
        a0,a1,a2,a3,a4,a5,a6,a7 = Imput[0]
        b0,b1,b2,b3,b4,b5,b6,b7 = Imput[1]
        c0,c1,c2,c3,c4,c5,c6,c7 = Imput[2]
        s0 = Sel[1].Not()*Sel[0].Not() # 00
        s1 = Sel[1].Not()*Sel[0]       # 01
        s2 = Sel[1]*Sel[0].Not()       # 10
        d0 = s0*a0 + s1*b0 + s2*c0
        d1 = s0*a1 + s1*b1 + s2*c1
        d2 = s0*a2 + s1*b2 + s2*c2
        d3 = s0*a3 + s1*b3 + s2*c3
        d4 = s0*a4 + s1*b4 + s2*c4
        d5 = s0*a5 + s1*b5 + s2*c5
        d6 = s0*a6 + s1*b6 + s2*c6
        d7 = s0*a7 + s1*b7 + s2*c7
        return [d0,d1,d2,d3,d4,d5,d6,d7]

    def Mux32x8(self, Imput, Sel):
        a0,a1,a2,a3,a4,a5,a6,a7 = Imput[0]
        b0,b1,b2,b3,b4,b5,b6,b7 = Imput[1]
        c0,c1,c2,c3,c4,c5,c6,c7 = Imput[2]
        d0,d1,d2,d3,d4,d5,d6,d7 = Imput[2]
        s0 = Sel[1].Not()*Sel[0].Not() # 00
        s1 = Sel[1].Not()*Sel[0]       # 01
        s2 = Sel[1]*Sel[0].Not()       # 10
        s3 = Sel[1]*Sel[0]             # 11
        e0 = s0*a0 + s1*b0 + s2*c0 + s3*d0
        e1 = s0*a1 + s1*b1 + s2*c1 + s3*d1
        e2 = s0*a2 + s1*b2 + s2*c2 + s3*d2
        e3 = s0*a3 + s1*b3 + s2*c3 + s3*d3
        e4 = s0*a4 + s1*b4 + s2*c4 + s3*d4
        e5 = s0*a5 + s1*b5 + s2*c5 + s3*d5
        e6 = s0*a6 + s1*b6 + s2*c6 + s3*d6
        e7 = s0*a7 + s1*b7 + s2*c7 + s3*d7
        return [e0,e1,e2,e3,e4,e5,e6,e7]

class Register4b: # 4-bits register
    def __init__(self):
        self.__Ff0 = Flipflop("D","UP")
        self.__Ff1 = Flipflop("D","UP")
        self.__Ff2 = Flipflop("D","UP")
        self.__Ff3 = Flipflop("D","UP")

    def Act(self, Input, En, Reset = None, Clk = None):
        Out = list(range(8))
        Out[0] = self.__Ff0.Operate(En*Input[0]+En.Not()*self.__Ff0.GetQ(), Reset, Clk)
        Out[1] = self.__Ff1.Operate(En*Input[1]+En.Not()*self.__Ff1.GetQ(), Reset, Clk)
        Out[2] = self.__Ff2.Operate(En*Input[2]+En.Not()*self.__Ff2.GetQ(), Reset, Clk)
        Out[3] = self.__Ff3.Operate(En*Input[3]+En.Not()*self.__Ff3.GetQ(), Reset, Clk)
        return Out

    def Read(self):
        Out = [0]*4
        Out[0] = self.__Ff0.GetQ()
        Out[1] = self.__Ff1.GetQ()
        Out[2] = self.__Ff2.GetQ()
        Out[3] = self.__Ff3.GetQ()
        return Out

class Register8b: # 8-bits register
    def __init__(self):
        self.__Ff0 = Flipflop("D","UP")
        self.__Ff1 = Flipflop("D","UP")
        self.__Ff2 = Flipflop("D","UP")
        self.__Ff3 = Flipflop("D","UP")
        self.__Ff4 = Flipflop("D","UP")
        self.__Ff5 = Flipflop("D","UP")
        self.__Ff6 = Flipflop("D","UP")
        self.__Ff7 = Flipflop("D","UP")

    def Act(self, Input, En, Reset = None, Clk = None):
        Out = list(range(8))
        Out[0] = self.__Ff0.Operate(En*Input[0]+En.Not()*self.__Ff0.GetQ(), Reset, Clk)
        Out[1] = self.__Ff1.Operate(En*Input[1]+En.Not()*self.__Ff1.GetQ(), Reset, Clk)
        Out[2] = self.__Ff2.Operate(En*Input[2]+En.Not()*self.__Ff2.GetQ(), Reset, Clk)
        Out[3] = self.__Ff3.Operate(En*Input[3]+En.Not()*self.__Ff3.GetQ(), Reset, Clk)
        Out[4] = self.__Ff4.Operate(En*Input[4]+En.Not()*self.__Ff4.GetQ(), Reset, Clk)
        Out[5] = self.__Ff5.Operate(En*Input[5]+En.Not()*self.__Ff5.GetQ(), Reset, Clk)
        Out[6] = self.__Ff6.Operate(En*Input[6]+En.Not()*self.__Ff6.GetQ(), Reset, Clk)
        Out[7] = self.__Ff7.Operate(En*Input[7]+En.Not()*self.__Ff7.GetQ(), Reset, Clk)
        return Out

    def Read(self):
        Out = list(range(8))
        Out[0] = self.__Ff0.GetQ()
        Out[1] = self.__Ff1.GetQ()
        Out[2] = self.__Ff2.GetQ()
        Out[3] = self.__Ff3.GetQ()
        Out[4] = self.__Ff4.GetQ()
        Out[5] = self.__Ff5.GetQ()
        Out[6] = self.__Ff6.GetQ()
        Out[7] = self.__Ff7.GetQ()
        return Out

class RegTris8b:
    def __init__(self):
        self.__reg = Register8b()
        self.__tristate = TristateBuffer()

    def Act(self, B, EIn, EOut, Reset, Clk):
        A = self.__reg.Act(B, EIn, Reset, Clk)
        Dir = LogicBit(1)
        [A,B] = self.__tristate.Buffer(A, B, Dir, EOut) # Dir=1 and EOut=1 -> puts A in B
        return B

    def Read(self):
        return self.__reg.Read()

class Register:
    def __init__(self, nBits):
        self.__nBits = nBits
        self.__Ffs = [Flipflop("D","UP") for i in range(self.__nBits)]

    def Act(self, Input, En, Reset = None, Clk = None):
        Out = list(range(self.__nBits))
        if(len(Input) == self.__nBits):
            for i in range(self.__nBits):
                Out[i] = self.__Ffs[i].Operate(En*Input[i]+En.Not()*self.__Ffs[i].GetQ(), Reset, Clk)
        return Out

    def Read(self, Open = None, Own = None):
        Out = range(self.__nBits)
        if(Open == 1 and len(Own) == self.__nBits):
            return Own
        else:
            for i in range(self.__nBits):
                Out[i] = self.__Ffs[i].GetQ()
        return Out

class RegTris:
    def __init__(self, nBits):
        self.__reg = Register(nBits)
        self.__tristate = TristateBuffer()

    def Act(self, B, EIn, EOut, Reset, Clk):
        A = self.__reg.Act(B, EIn, Reset, Clk)
        Dir = LogicBit(1)
        [A,B] = self.__tristate.Buffer(A, B, Dir, EOut) # Dir=1 and EOut=1 -> puts A in B
        return B

class Counter4b: # Counter of 4 bits
    def __init__(self):
        self.__Ff0 = Flipflop("D", "UP")
        self.__Ff1 = Flipflop("D", "UP")
        self.__Ff2 = Flipflop("D", "UP")
        self.__Ff3 = Flipflop("D", "UP")

    def Act(self, Input, En, nLoad, nReset, Clk): # Load and Reset works in No
        in0,in1,in2,in3 = Input
        q0 = self.__Ff0.GetQ()
        q1 = self.__Ff1.GetQ()
        q2 = self.__Ff2.GetQ()
        q3 = self.__Ff3.GetQ()

        s0 = nLoad + nReset.Not()      # s0.Not()=1 -> Load=0 and Reset=1
        s1 = s0.Not() + nReset.Not()  # s1.Not()=1 -> s1=1 and Reset=1

        Q0 = s0.Not()*in0 + s1.Not()*(q0.Not())
        Q1 = s0.Not()*in1 + s1.Not()*(q1.Not()*q0 + q1*q0.Not())
        Q2 = s0.Not()*in2 + s1.Not()*(q2.Not()*q1*q0 + q2*q1.Not() + q2*q0.Not())
        Q3 = s0.Not()*in3 + s1.Not()*(q3.Not()*q2*q1*q0 + q3*q2.Not() + q3*q1.Not() + q3*q0.Not())

        q0 = self.__Ff0.Operate(En*Q0+En.Not()*self.__Ff0.GetQ(), LogicBit(0), Clk)
        q1 = self.__Ff1.Operate(En*Q1+En.Not()*self.__Ff1.GetQ(), LogicBit(0), Clk)
        q2 = self.__Ff2.Operate(En*Q2+En.Not()*self.__Ff2.GetQ(), LogicBit(0), Clk)
        q3 = self.__Ff3.Operate(En*Q3+En.Not()*self.__Ff3.GetQ(), LogicBit(0), Clk)
        return [q0,q1,q2,q3]

    def Operate(self, Clk):
        In = [LogicBit(0) for bit in range(4)]
        Load = LogicBit(1)
        En = LogicBit(1)
        Reset = LogicBit(1)
        return self.Act(En, In, Load, Reset, Clk)

    def Read(self):
        Out = [0]*4
        Out[0] = self.__Ff0.GetQ()
        Out[1] = self.__Ff1.GetQ()
        Out[2] = self.__Ff2.GetQ()
        Out[3] = self.__Ff3.GetQ()
        return Out

class ALU8b: # 8-bit arithmetic and logic unit
    def __init__(self):
        self.__Mux = Mux()
        self.__tristate = TristateBuffer()

    def __Sum(self, A, B, CarryIn): # full adder
        value = (A^B)^CarryIn
        CarryOut = (A*B) ^ (A*CarryIn) ^ (B*CarryIn)
        return value,CarryOut

    def __Sub(self, A, B, BorrowIn): # full subtractor
        value = (A^B)^BorrowIn
        BorrowOut = (A.Not()*B) ^ (A.Not()*BorrowIn) ^ (B*BorrowIn)
        return value,BorrowOut

    def __Complement2(self, B): # complement 2
        value = B^LogicBit(1)
        return value

    def Act(self, A, B, SumSub, Alu0, Alu1):
        Carry = SumSub
        Sum = [LogicBit(0) for bit in range(8)]
        for i in range(8):
            Sum[i], Carry = self.__Sum(A[i], B[i]^SumSub, Carry) # if SumSub=1 -> subtractor with complement 2

        And = [LogicBit(0) for bit in range(8)]
        for i in range(8):
            And[i] = A[i]*B[i]

        Or = [LogicBit(0) for bit in range(8)]
        for i in range(8):
            Or[i] = A[i]+B[i]

        Xor = [LogicBit(0) for bit in range(8)]
        for i in range(8):
            Xor[i] = A[i]^B[i]

        Dir = LogicBit(1)
        A = self.__Mux.Mux32x8([Sum,And,Or,Xor],[Alu0,Alu1])
        return A

class ALU8bTris:
    def __init__(self):
        self.__Alu = ALU8b()
        self.__tristate = TristateBuffer()

    def Act(self, Bus, A, B, SumSub, Alu0, Alu1, AluOut):
        A = self.__Alu.Act(A, B, SumSub, Alu0, Alu1)
        Dir = LogicBit(1)
        [A,B] = self.__tristate.Buffer(A, Bus, Dir, AluOut) # Dir=1 and EOut=1 -> puts A in B
        return B

class ALU: # Arithmetic and logic unit
    def __init__(self, nBits):
        self.__nBits = nBits
        self.__C = [LogicBit(0) for bit in range(nBits)]

    def __Sum(self, A, B, CarryIn): # full adder
        value = (A^B)^CarryIn
        CarryOut = (A*B) ^ (A*CarryIn) ^ (B*CarryIn)
        return value,CarryOut

    def __Sub(self, A, B, BorrowIn): # full subtractor
        value = (A^B)^BorrowIn
        BorrowOut = (A.Not()*B) ^ (A.Not()*BorrowIn) ^ (B*BorrowIn)
        return value,BorrowOut

    def __Complement2(self, B): # complement 2
        value = B^LogicBit(1)
        return value

    def Act(self, A, B):
        Carry = LogicBit(0)
        Sum = [LogicBit(0) for bit in range(self.__nBits)]
        for i in range(8):
            Sum[i], Carry = self.__Sum(A[i], B[i], Carry) # operation on each bit

        Borrow = LogicBit(0)
        Sub = [LogicBit(0) for bit in range(self.__nBits)]
        for i in range(self.__nBits):
            Sub[i], Borrow = self.__Sub(A[i], B[i], Borrow)

        And = [LogicBit(0) for bit in range(self.__nBits)]
        for i in range(8):
            And[i] = A[i]*B[i]  # And logic

        Or = [LogicBit(0) for bit in range(self.__nBits)]
        for i in range(8):
            Or[i] = A[i]+B[i]   # Or logic

        Xor = [LogicBit(0) for bit in range(self.__nBits)]
        for i in range(8):
            Xor[i] = A[i]^B[i]  # Xor logic

        return Sum

class RAM2x2b: # RAM memory of 2-bits address and 2-bits of data
    def __init__(self):
        self.__Ff00 = Flipflop("D", "UP")
        self.__Ff01 = Flipflop("D", "UP")
        self.__Ff10 = Flipflop("D", "UP")
        self.__Ff11 = Flipflop("D", "UP")
        self.__Ff20 = Flipflop("D", "UP")
        self.__Ff21 = Flipflop("D", "UP")
        self.__Ff30 = Flipflop("D", "UP")
        self.__Ff31 = Flipflop("D", "UP")

    def Act(self, Ad0, Ad1, D0, D1, We, Reset, Clk):
        s0 = Ad1.Not()*Ad0.Not() # 00
        s1 = Ad1.Not()*Ad0       # 01
        s2 = Ad1*Ad0.Not()       # 10
        s3 = Ad1*Ad0             # 11

        # line 0
        w00 = We * s0
        r00 = We.Not() * s0
        ff00 = (w00 * D0).Not() * (w00.Not() * self.__Ff00.GetQ()).Not()
        d00 = self.__Ff00.Operate(ff00.Not(), Reset, Clk)

        w01 = We * s0
        r01 = We.Not() * s0
        ff01 = (w01 * D1).Not() * (w01.Not() * self.__Ff01.GetQ()).Not()
        d01 = self.__Ff01.Operate(ff01.Not(), Reset, Clk)

        # line 1
        w10 = We * s1
        r10 = We.Not() * s1
        ff10 = (w10 * D0).Not() * (w10.Not() * self.__Ff10.GetQ()).Not()
        d10 = self.__Ff10.Operate(ff10.Not(), Reset, Clk)

        w11 = We * s1
        r11 = We.Not() * s1
        ff11 = (w11 * D1).Not() * (w11.Not() * self.__Ff11.GetQ()).Not()
        d11 = self.__Ff11.Operate(ff11.Not(), Reset, Clk)

        # line 2
        w20 = We * s2
        r20 = We.Not() * s2
        ff20 = (w20 * D0).Not() * (w20.Not() * self.__Ff20.GetQ()).Not()
        d20 = self.__Ff20.Operate(ff20.Not(), Reset, Clk)

        w21 = We * s2
        r21 = We.Not() * s2
        ff21 = (w21 * D1).Not() * (w21.Not() * self.__Ff21.GetQ()).Not()
        d21 = self.__Ff21.Operate(ff21.Not(), Reset, Clk)

        d0 = d00 * r00 + d10 * r10 + d20 * r20
        d1 = d01 * r01 + d11 * r11 + d21 * r21

        Out = [d0 ,d1]
        return Out

class RAM: # RAM memory of 4-bits address and 8-bits of data
    def __init__(self, AddrSize, DataSize):
        self.__AddrSize = AddrSize
        self.__DataSize = DataSize
        self.__Ffs = [[Flipflop("D", "UP") for i in range(DataSize)] for j in range(2**AddrSize)]

    def __GetLine(self, Line, Addr):
        size = len(Addr)
        t = [int(bin(Line)[2:].zfill(size)[i]) for i in range(size)]  # binary value in list exp: Line=3, size=4 [0,0,1,1]
        value = Addr[0].Get(t[size - 1])
        for i in range(1, size):
            value = value * Addr[i].Get(t[size - 1 - i]) # product of LogicBit's
        return value

    def Act(self, Addr, DataIn, We, Reset, Clk):
        values = [[LogicBit(0) for i in range(self.__DataSize)] for j in range(2**self.__AddrSize)]
        read = [[0 for i in range(self.__DataSize)] for j in range(2 ** self.__AddrSize)]
        for i in range(2**self.__AddrSize):
            Line = self.__GetLine(i, Addr)
            for j in range(self.__DataSize):
                w = We * Line           # write data
                r = We.Not() * Line     # read data
                read[i][j]=r
                ff = (w * DataIn[j]).Not() * (w.Not() * self.__Ffs[i][j].GetQ()).Not()
                values[i][j] = self.__Ffs[i][j].Operate(ff.Not(), Reset, Clk)

        DataOut = [0 for i in range(self.__DataSize)]
        for i in range(self.__DataSize):
            DataOut[i]=values[0][i]*read[0][i]
            for j in range(1,2 ** self.__AddrSize):
                DataOut[i]=DataOut[i]+values[j][i]*read[j][i] # j is line and i is bit
        return DataOut


class RAMTris: # RAM memory with tri-state
    def __init__(self, AddrSize, DataSize):
        self.__Ram = RAM(AddrSize, DataSize)
        self.__tristate = TristateBuffer()

    def Act(self, Bus, Addr, We, RamOut, Reset, Clk):
        Dir = LogicBit(1)
        A = self.__Ram.Act(Addr, Bus, We, Reset, Clk)
        [A, B] = self.__tristate.Buffer(A, Bus, Dir, RamOut)  # Dir=1 and RamOut=1 -> puts A in B
        return B
