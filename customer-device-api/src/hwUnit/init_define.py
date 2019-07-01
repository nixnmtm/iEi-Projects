"""
class actionDefine(object):
    def __init__(self):
        self.SET=0
        self.GET=1

class configDefine(object):
    def __init__(self):
        self.Server=0
        self.RabbitMQ=1

class deviceDefine(object):
    def __init__(self):
        self.SN=0
        self.MACs=1
        self.VPD=2
"""


class main(object):
    """docstring for Define Type action/config/device ."""
    def __init__(self):
        #=== user:test  ===
        self.user = "test"
        self.pwd = "8888"
        #=== networkChipType  ===
        self.networkChipType = ["I211","others"]
        #=== deviceType ===
        self.deviceType = [0,1] #hw,eth
        #=== status ===
        self.result = {}
        self.result["none"] = 0
        self.result["pass"] = 1
        self.result["error"] = 2
        #=== action ===
        self.action = {}
        self.action[0] = "set"
        self.action[1] = "get"
        #=== config ===
        self.config = {}
        self.config[0] = ["Server",["ip","port"]]
        self.config[1] = ["RabbitMQ",["ip","port","user","password"]]
        #=== device ===
        self.device = {}
        self.device[0] = [self.deviceType[0],"SN"] #hw:set/get
        self.device[1] = [self.deviceType[1],"MACs"] #eth:set/get
        self.device[2] = [self.deviceType[0],"VPD"] #hw:set/get
        
        self.device[20] = [self.deviceType[0],"Platform"] #hw:get
        self.device[21] = [self.deviceType[1],"Interfaces"] #eth:get
        self.device[22] = [self.deviceType[1],"EthCount"] #eth:get
        #self.device[23] = [self.deviceType[1],"MAC"] #eth:set/get
        #self.device[24] = [self.deviceType[1],"IntelNIC"] #eth:get

        #=== VPD Define ===
        # "data":{
        #   "mfgDateTime":"2018/06/29-00:42",
        #   "boardManufacturer":"QNAP Systems",
        #   "boardProductName":"QNAP Systems",
        #   "boardSerialNumber":"70-0QY630120",
        #   "boardPartNumber":"11807008071",
        #   "sasAddress":"",
        #   "manufacturerName":"QNAP Systems",
        #   "productName":"NONE",
        #   "productPartModelNumber":"NONE",
        #   "productVersion":"004",
        #   "productSerialNumber":"Q186I15815"
        # }
        self.VPD = {}
        self.VPDrequired = ["productSerialNumber"]
        self.VPD["mfgDateTime"] = "0:0"
        self.VPD["boardManufacturer"] = "0:1"
        self.VPD["boardProductName"] = "0:2"
        self.VPD["boardSerialNumber"] = "0:3"
        self.VPD["boardPartNumber"] = "0:4"
        self.VPD["boardSasAddress"] = "0:5"
        self.VPD["productManufacturer"] = "0:6"
        self.VPD["productName"] = "0:7"
        self.VPD["productPartModelNumber"] = "0:8"
        self.VPD["productVersion"] = "0:9"
        self.VPD["productSerialNumber"] = "0:10"

    def getConfigFunction (self,actionType,nameType):
        #print("actionType: {},nameType: {}".format(self.action[actionType],self.config[nameType]))
        mFunctionName = self.action[actionType] + self.config[nameType][0]
        #print("call Config Fuction : {}".format(mFunctionName))
        return mFunctionName

    def getDeviceFunction (self,actionType,nameType):
        #print("actionType: {},nameType: {}".format(actionType,nameType))
        mFunctionName = []
        mFunctionName.append(self.device[nameType][0])
        mFunctionName.append(self.action[actionType] + self.device[nameType][1])
        #print("call Device Fuction : {}".format(repr(mFunctionName)))
        return mFunctionName
