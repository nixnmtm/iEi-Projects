import time
import os,serial
import threading
import termios
import codecs

class fanComport(object):
    def __init__(self):
        self.stopflag=True
        self.portPath="/dev/ttyS1"
        self.ser=None
        self.readFan=b'@FF\x40'
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

    def GETFAN(self):
        cmd=self.readFan
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

        myFan=[]
        myFanOriData=None
        myflag=False
        self.stopflag=False
        if self.ser is not None:
            try:
                self.GETFAN()
                while self.stopflag==False:
                    data=self.ser.readline()
                    if len(data)>0:
                        myFanOriData=data
                        # print("myFanOriData {}".format(myFanOriData))
                        break;

            except Exception as e:
                print("exception: read Exception error {}".format(e))
                self.ser=None
                self.errorMsg=e
                self.stop()
        if myFanOriData is not None:
            data3=list(myFanOriData)
            print("myFanOriData {} ".format(myFanOriData))
            print("data3 {} ".format(len(data3)))
            if len(data3) > 4:
                print("myFanOriData {} ".format(myFanOriData))
                print("data3 {} ".format(data3))
                fanNum=int(chr(data3[3]))
                if len(data3) >= 4+fanNum*2:
                    if fanNum > 4:
                        fanNum=4
                    for loop in range(0,fanNum):
                        fan1=int((data3[loop*2+4]*256+data3[loop*2+4+1])/2)
                        fan1=fan1*60;
                        # print(fan1)
                        myFan.append(fan1)
        return myFan



    def stop(self):
        self.stopflag=True
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception as e:
                print("exception: read Exception error {}".format(e))
