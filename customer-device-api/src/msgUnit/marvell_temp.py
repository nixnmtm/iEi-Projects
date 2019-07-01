import time
import os,serial
import threading
import termios
import codecs

class devComport(object):
    def __init__(self):
        self.stopflag=True
        self.portPath="/dev/ttyS1"
        self.ser=None
        self.readTemp=b'@TA\x55'
        self.baudrate=115200 #19200
        self.errorMsg=None
    def openPort(self):
        try:
            ser = serial.Serial(self.portPath,os.O_RDWR | os.O_NOCTTY | os.O_NDELAY, timeout= 0.5)
            ser.baudrate = self.baudrate
            flag=ser.isOpen()
            if flag:
                tio = termios.tcgetattr(ser)
                tio[2]=termios.B115200|termios.CS8|termios.CREAD|termios.CLOCAL;
                tio[6][termios.VTIME]   =0;
                tio[6][termios.VMIN]    =0;
                termios.tcflush(ser, termios.TCIFLUSH);
                termios.tcsetattr(ser, termios.TCSADRAIN, tio)
                self.ser=ser
                return True
            else:
                return False
        except Exception as e:
            print("exception: Exception error {}".format(e))
            return False

    def GETDEVINFO(self):
        cmd=self.readTemp
        print("cmd is {}".format(cmd))
        self.sendCmd(cmd)

    def sendCmd(self,cmd):
        if self.stopflag:
            return
        try:
            if self.ser is not None:
                self.ser.write(cmd)
        except Exception as e:
            print("exception: Exception error {}".format(e))


    def start(self):
        flag=self.openPort()
        if flag==False:
            print("openPort fail")
            return []

        myTemp=[]
        myTempOriData=None
        myflag=False
        self.stopflag=False
        if self.ser is not None:
            try:
                self.GETDEVINFO()
                while self.stopflag==False:
                    data=self.ser.readline()
                    if len(data)>0:
                        myTempOriData=data
                        # print("myTempOriData {}".format(myTempOriData))
                        break;

            except Exception as e:
                print("exception: read Exception error {}".format(e))
                self.ser=None
                self.errorMsg=e
                self.stop()
        if myTempOriData is not None:
            data3=list(myTempOriData)
            print("myOriData {} ".format(myTempOriData))
            print("data3 {} ".format(len(data3)))
            if len(data3) > 4:
                print("myOriData {} ".format(myTempOriData))
                print("data3 {} ".format(data3))
                tempNum=int(chr(data3[3]))
                if len(data3) >= 4+tempNum:
                    if tempNum > 4:
                        tempNum=4
                    for loop in range(0,tempNum):
                        temp1=int((data3[loop+4]-0x80))
                        # print(temp1)
                        myTemp.append(temp1)
        return myTemp



    def stop(self):
        self.stopflag=True
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception as e:
                print("exception: read Exception error {}".format(e))
