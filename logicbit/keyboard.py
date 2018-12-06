#!/usr/bin/python
# encoding: utf-8

from threading import Thread
import sys

# Author Cleoner S. Pietralonga
# e-mail: cleonerp@gmail.com
# Apache License

try:
    import tty, termios
except ImportError:
    try: # try on windows
        import msvcrt
    except ImportError:
        raise ImportError('msvcrt not available!')
    else:
        getch = msvcrt.getch
else:
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class Keyboard(Thread):
    def __init__(self, Clock):
        Thread.__init__(self)
        self.__th_key = True
        self.__Clock = Clock

    def run(self):
        while (self.__th_key):
            try:
                key = self.GetKey()
                if(key == 32): # space
                    self.__Clock.Next() # next clock
                elif(key == 112): # p
                    self.__Clock.Pause() # pause clock
                elif(key == 13): # enter
                    self.__Clock.Run() # stand-alone mode
                elif(key == 27): # exit
                    self.__th_key = False
                    self.__Clock.TurnOff()
            except Exception as ex:
                print(str(ex))

    def GetKey(self): # get the key pressed
        key = getch()
        return ord(key)