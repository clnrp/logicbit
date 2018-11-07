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
    
    def __mul__(self, other): # logica E
        value = self.value and other.value
        return LogicBit(value)
    
    def __add__(self, other): # logica OU
        value = self.value or other.value
        return LogicBit(value)
    
    def __xor__(self, other): # logica OU-Exclusivo
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
    
    def Get(self):
        return self.value


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

    def Act(self, Input = None, Clk=None, Reset=None):
        if (Reset == 1):
            self.Reset()
        elif(Input != None):
            if(self.Type == "D"):
                if('list' in str(type(Input)) and len(Input) == 1): # verifica se e uma lista
                    D = Input[0]
                else:
                    D = Input
                self.__D(D, Clk)
            elif(self.Type == "T"): # Flip-flop Toggle
                if('list' in str(type(Input)) and len(Input) == 1): # verifica se e uma lista
                    T = Input[0]
                else:
                    T = Input
                self.__T(T, Clk)
            elif(self.Type == "SR" and len(Input) == 2):
                S,R = Input
                self.__SR(S, R, Clk) # S = input[0] e R = input[1]
            elif(self.Type == "JK" and len(Input) == 2):
                J,K = Input
                self.__JK(J, K, Clk) # J = input[0] e K = input[1]
        return self.Q, self.NotQ

    def Operate(self, Input = None, Clk=None, Reset=None): # retorna apenas Q
        return self.Act(Input, Clk, Reset)[0]

    def Set(self, Input = None, Clk=None, Reset=None):
        self.Act(Input, Clk, Reset)[0]

    def GetQ(self, Reset=None):
        return self.Act(None, None, Reset)[0]

    def GetNotQ(self, Reset=None):
        return self.Act(None, None, Reset)[1]

    def Reset(self):
        self.Q = LogicBit(0)
        self.NotQ = LogicBit(1)


class TristateBuffer:
    def __init__(self):
        self.Clk = 0

    def Single(self, A, B, Ce = None):
        if(Ce == 1):      # coloca A em B
            B = A
        return B
    
    def DirBuffer(self, A, B, Dir, Ce = None):
        if(Ce == 1):
            if(Dir == 1): # coloca A em B
                B = A
            else:
                A = B     # coloca B em A
        return [A, B]

class Mux:
    def __init__(self, clkType):
        self.clkType = clkType
        self.Clk = 0
    
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

class Register_8bits:
    def __init__(self):
        self.__Ff0= Flipflop("D","UP")
        self.__Ff1= Flipflop("D","UP")
        self.__Ff2= Flipflop("D","UP")
        self.__Ff3= Flipflop("D","UP")
        self.__Ff4= Flipflop("D","UP")
        self.__Ff5= Flipflop("D","UP")
        self.__Ff6= Flipflop("D","UP")
        self.__Ff7= Flipflop("D","UP")

    def Act(self, Input, Clk = None, Clean = None):
        Out = range(8)
        Out[0] = self.__Ff0.Operate(Input[0],Clk,Clean)
        Out[1] = self.__Ff1.Operate(Input[1],Clk,Clean)
        Out[2] = self.__Ff2.Operate(Input[2],Clk,Clean)
        Out[3] = self.__Ff3.Operate(Input[3],Clk,Clean)
        Out[4] = self.__Ff4.Operate(Input[4],Clk,Clean)
        Out[5] = self.__Ff5.Operate(Input[5],Clk,Clean)
        Out[6] = self.__Ff6.Operate(Input[6],Clk,Clean)
        Out[7] = self.__Ff7.Operate(Input[7],Clk,Clean)
        return Out

    def Read(self):
        Out = range(8)
        Out[0] = self.__Ff0.GetQ()
        Out[1] = self.__Ff1.GetQ()
        Out[2] = self.__Ff2.GetQ()
        Out[3] = self.__Ff3.GetQ()
        Out[4] = self.__Ff4.GetQ()
        Out[5] = self.__Ff5.GetQ()
        Out[6] = self.__Ff6.GetQ()
        Out[7] = self.__Ff7.GetQ()
        return Out

class Register:
    def __init__(self, nBits):
        self.__nBits = nBits
        self.__Ffs = [Flipflop("D","UP") for i in range(self.__nBits)]

    def Act(self, Input, Clk = None, Clean = None):
        Out = range(self.__nBits)
        if(len(Input) == self.__nBits):
            for i in range(self.__nBits):
                Out[i] = self.__Ffs[i].Operate(Input[i],Clk,Clean)
        return Out

    def Read(self, Open = None, Own = None):
        Out = range(self.__nBits)
        if(Open == 1 and len(Own) == self.__nBits):
            return Own
        else:
            for i in range(self.__nBits):
                Out[i] = self.__Ffs[i].GetQ()
        return Out

