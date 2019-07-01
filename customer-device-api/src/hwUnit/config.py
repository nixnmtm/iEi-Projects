import json
import os
import sys
from hwUnit import init_define
class main(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))        
        self.configPath = "{}{}".format(dir_path,"/../config/config.json")
        self.myDefine = init_define.main()
        self.ServerRequire = self.myDefine.config[0][1]
        self.RabbitMQRequire =self.myDefine.config[1][1]
        self.actionType = -1
    def str_to_class(self,str):
        return getattr(self,str)
    def start(self,jsonDate):
        self.actionType = jsonDate["action"]
        res = []
        if self.actionType == 1:#get
            for loop in jsonDate["name"]:
                resData = {}
                resData["name"] = loop
                mFunctionName = self.myDefine.getConfigFunction(self.actionType,loop)
                resData["data"] = self.str_to_class(mFunctionName)()
                res.append(resData)
        else:#get
            for loop in jsonDate["data"]:
                resData = {}
                resData["name"] = loop["name"]
                mFunctionName = self.myDefine.getConfigFunction(self.actionType,loop["name"])
                resultData = self.str_to_class(mFunctionName)(loop["data"])
                resData.update(resultData)
                res.append(resData)
        return res
    def readJsonFile(self):
        content = {}
        if os.path.exists(self.configPath):
            with open(self.configPath, "r") as outfile:
                content = json.load(outfile)

        return content
    def writeJsonFile(self,mData):
        with open(self.configPath, "w") as outfile:
            json.dump(mData,outfile,sort_keys=True,indent=4)
    def getServer(self):
        tmpData = self.readJsonFile()
        mServerDate = tmpData[self.myDefine.config[0][0]]
        #print("getServer :{}".format(mServerDate))
        return mServerDate
    def setServer(self,mServerDate):
        resData = {}
        checkResult = self.checkNecessary(mServerDate,self.ServerRequire)
        if checkResult[0] == True:
            tmpData = self.readJsonFile()
            tmpData[self.myDefine.config[0][0]] = mServerDate
            self.writeJsonFile(tmpData)
            #print("setServerIP :{}".format(self.readJsonFile()))
            if len(self.readJsonFile()) >= 1:#pass
                resData["result"] = self.myDefine.result["pass"]
            else:
                resData["result"] = self.myDefine.result["error"]
                resData["msg"] = "setServer is error."
        else:
            resData["result"] = self.myDefine.result["error"]
            resData["msg"] = ', '.join(checkResult[1:]) + " is required."
        return resData
    def getRabbitMQ(self):
        tmpData = self.readJsonFile()
        mRabbitMQDate = tmpData[self.myDefine.config[1][0]]
        #print("getRabbitMQ :{}".format(mRabbitMQDate))
        return mRabbitMQDate
    def setRabbitMQ(self,mRabbitMQDate):
        resData = {}
        checkResult = self.checkNecessary(mRabbitMQDate,self.RabbitMQRequire)
        if checkResult[0] == True:
            tmpData = self.readJsonFile()
            tmpData[self.myDefine.config[1][0]] = mRabbitMQDate
            self.writeJsonFile(tmpData)
            #print("setRabbitMQIP :{}".format(self.readJsonFile()))
            if len(self.readJsonFile()) >= 1:#pass
                resData["result"] = self.myDefine.result["pass"]
            else:
                resData["result"] = self.myDefine.result["error"]
                resData["msg"] = "setRabbitMQ is error."
        else:
            resData["result"] = self.myDefine.result["error"]
            resData["msg"] = ', '.join(checkResult[1:]) + " is required."
        return resData
    def checkNecessary(self,mData,mRequire):
        resMsg = []
        resTag = True
        dataKeys = list(mData.keys())
        for loop in mRequire:
            if loop not in mData:
                resMsg.append(loop)
                resTag = False
        resMsg.insert(0, resTag)
        return resMsg
