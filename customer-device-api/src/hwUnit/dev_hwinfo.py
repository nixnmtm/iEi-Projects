#!/usr/bin/python3
from hwUnit import execute_cmd,init_define
import platform, os, stat
import json
from config.normal import toolsDefine
toolsDef=toolsDefine()
class device:
    def __init__(self):
        """"get hwinfo ()
        """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.vpdPath = "{}".format("/tmp/.vpd.txt")
        self.fakePath = "{}{}".format(dir_path,"/../config/fakeData.json")
        self.intelEEtool= toolsDef.vpd
        self.myDefine = init_define.main()
        self.platform=self.getPlatform()
    def getPlatform(self):
        return platform.machine()
    def initVPDdata(self):
        if os.path.exists(self.vpdPath):
            os.remove(self.vpdPath)
            print("\n** initVPD removefile : {}.".format(self.vpdPath))
        tmpData = self.readJsonFile()
    def getSN(self):
        mSNname = self.myDefine.VPDrequired[0]
        resData = ""
        tmpData = self.readJsonFile()
        resData = tmpData[mSNname]
        return resData
    def getProductName(self):
        vpdName = "productName"
        resData = ""
        tmpData = self.readJsonFile()
        resData = tmpData[vpdName]
        return resData
    def getVPD(self):
        tmpData = self.readJsonFile()
        mVPDDate = tmpData
        return mVPDDate
    def readJsonFile(self):
        content = {}
        if os.path.exists(self.vpdPath):
            with open(self.vpdPath, "r") as outfile:
                content = json.load(outfile)
        else:
            resData = {}
            print("** {} is not exists, read from eeprom and create vpd file.".format(self.vpdPath))
            # read from eeprom
            mVPDkeys = self.myDefine.VPD.keys()
            for key in mVPDkeys:
                mVPDindex = self.myDefine.VPD[key]
                resData[key] = self.readEEprom("{}".format(mVPDindex))
            # write to vpd file
            self.writeJsonFile(resData)
            with open(self.vpdPath, "r") as outfile:
                content = json.load(outfile)
        # print("readJsonFile date : {} \n".format(content))
        return content
    def writeJsonFile(self,mData):
        with open(self.vpdPath, "w") as outfile:
            json.dump(mData,outfile,sort_keys=True,indent=4)
    def readEEprom(self,id):
        os.chmod(self.intelEEtool, stat.S_IRWXU)
        # sudo ./hal_app --vpd_get_field obj_index=1:4
        # ./vpd 1:4
        cmd = "sudo {} '{}'".format(self.intelEEtool,id)
        (ret, stdout, stderr) = execute_cmd.execute_cmd(cmd)
        # print("readEEprom cmd : {}".format(cmd))
        # print("readEEprom cmd : {}\nresult : {}".format(cmd,stdout.rstrip()))
        if ret==0:
            return stdout
        else:
            return ""
