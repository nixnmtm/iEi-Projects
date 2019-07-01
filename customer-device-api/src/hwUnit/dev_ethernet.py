#!/usr/bin/python3
from hwUnit import execute_cmd,dev_hwinfo,init_define
import os, sys, stat
import json

class device:
    def __init__(self):
        """"get ethernet info ()

        :param cmd: Command to run locally.
        :type ethInterfaces: array
        :type timeout: int
        :return resultTag, stderr, ethInterfaces
        :rtype: tuple(int, str, str)
        """
        self.hw = dev_hwinfo.device()
        self.ethKey="Ethernet"
        self.ethAllInterfaceName=[]
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.myDefine = init_define.main()
        self.mPlatform=self.hw.getPlatform()
    def getInterfaces(self):
        self.ethAllInterfaceName.clear()
        cmd = 'ifconfig -a | grep {} | grep -v docker'.format(self.ethKey)
        (ret, stdout, stderr) = execute_cmd.execute_cmd(cmd)
        if len( stderr ) >= 1:
            print ("Get Ethernet confing error:\n" + stderr)
        else:
            temp=stdout.splitlines()
            for eth in temp:
                res = list(filter(str.strip,eth.split(" ")))
                self.ethAllInterfaceName.append(res[0])
            return self.ethAllInterfaceName
    def getEthCount(self):
        cmd = 'ifconfig -a | grep {} | grep -v docker'.format(self.ethKey)
        (ret, stdout, stderr) = execute_cmd.execute_cmd(cmd)
        if len( stderr ) >= 1:
            print ("Get Ethernet Count error:\n" + stderr)
        else:
            temp=stdout.splitlines()
            return len(temp)
    def getMACs(self):
        mAllEthHWAddress={}
        cmd = 'ifconfig -a | grep {} | grep -v docker'.format(self.ethKey)
        (ret, stdout, stderr) = execute_cmd.execute_cmd(cmd)
        if len( stderr ) >= 1:
            print ("Get Ethernet HWAddress error:\n" + stderr)
        else:
            temp=stdout.splitlines()
            for eth in temp:
                res = list(filter(str.strip,eth.split(" ")))
                mAllEthHWAddress[res[0]]=res[len(res)-1].strip()
        # self.ethAllHWAddress=json.dumps(mAllEthHWAddress)
        #self.ethAllHWAddress=[(k,mAllEthHWAddress[k]) for k in sorted(mAllEthHWAddress.keys())]
        return mAllEthHWAddress
    def getMAC(self,strInterface):
        cmd = 'cat /sys/class/net/' + strInterface + '/address'
        (ret, stdout, stderr) = execute_cmd.execute_cmd(cmd)
        if len( stderr ) >= 1:
            print ("Get network HWAddress error:\n" + stderr)
        else:
            return stdout.strip()
