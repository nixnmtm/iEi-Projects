from hwUnit import dev_ethernet,dev_hwinfo,init_define
import json
import sys

class main(object):
    """ 
    *** initDefine ***
    action:0/1 >>set/get
    deviceType = [0,1] #hw,eth
    self.device[0] = [self.deviceType[0],"SN"] #hw:set/get
    self.device[1] = [self.deviceType[1],"MACs"] #eth:set/get
    self.device[2] = [self.deviceType[0],"VPD"] #hw:set/get
    
    self.device[20] = [self.deviceType[0],"Platform"] #hw:get
    self.device[21] = [self.deviceType[1],"Interfaces"] #eth:get
    self.device[22] = [self.deviceType[1],"EthCount"] #eth:get
    self.device[23] = [self.deviceType[1],"MAC"] #eth:set/get
    self.device[24] = [self.deviceType[1],"IntelNIC"] #eth:get
    
    *** jsonDate Device Sample ***
    {
        action:0/1,  (set/get)
        data:[
            {
                "name":0,
                "data":{
                    "sn":"1234567890"
                }     
            },
            {
                "name":1,
                "data":{
                    "macs":[
                        "CJO39409423FSF",
                        "CJO39409423FS1",
                        "CJO39409423FS2",
                        "CJO39409423FS3",
                        "CJO39409423FS4"
                    ]   
                }
            }
        ]
    }
    """
    def __init__(self):
        #init class.
        self.myEth = dev_ethernet.device()
        self.myHW = dev_hwinfo.device()
        self.myObj = [self.myHW,self.myEth]
        self.myDefine = init_define.main()
        self.actionType = -1
    def str_to_class(self,myObj,str):
        return getattr(myObj,str)
    def start(self,jsonDate):
        self.actionType = jsonDate["action"]
        res = []
        if self.actionType == 1:#get
            for loop in jsonDate["name"]:
                resData = {}
                resData["name"] = loop
                mFunctionName = self.myDefine.getDeviceFunction(self.actionType,loop)
                resData["data"] = self.str_to_class(self.myObj[mFunctionName[0]],mFunctionName[1])()
                res.append(resData)
        return res
        
    