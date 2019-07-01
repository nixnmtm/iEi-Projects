from flask import request, jsonify

import os

from config.normal import workDefine,actionDefine,resultDefine
from hwUnit.dev_hwinfo import device as HWinfo
actionDef=actionDefine()
resultDef=resultDefine()
workBoxs=workDefine().data

deviceHWinfo=HWinfo()
deviceHWinfo.initVPDdata()

class main:
    def __init__(self,app):
        app.add_url_rule('/deviceAgent', 'deviceAgent', self.deviceAgent, methods=['POST'])
        app.add_url_rule('/deviceInfo', 'deviceInfo', self.deviceInfo, methods=['POST'])


    def deviceAgent(self):
        content = request.json
        data={}
        resultkey="result"
        result=resultDef.NONE
        for key, value in content.items():
            tmp=workBoxs[key]
            if tmp is not None:
                mod = __import__(tmp['dir'],fromlist=[*workBoxs])
                mod2=getattr(mod,tmp['pythonfile'])
                func=getattr(mod2,tmp['classname'])()
                tmpvalue={
                    "action":actionDef.SET,
                    "data":value
                 }
                resp=func.start(tmpvalue)
                data[key]=resp
                result=self.reportresult(result,resp)
        data.update({resultkey:result})

        tmp=jsonify(data)

        return tmp
    def reportresult(self,real,data):
        resultkey="result"
        for loop in data:
            result=loop[resultkey]
            tmp=real
            if tmp==resultDef.FAIL:
                return real
            if tmp==resultDef.PASS and result==resultDef.FAIL:
                real=result
            if tmp==resultDef.NONE:
                real=result
        return real
    def deviceInfo(self):
        content = request.json
        data={}
        for key, value in content.items():
            tmp=workBoxs[key]
            if tmp is not None:
                mod = __import__(tmp['dir'],fromlist=[*workBoxs])
                mod2=getattr(mod,tmp['pythonfile'])
                func=getattr(mod2,tmp['classname'])()
                tmpvalue={
                    "action":actionDef.GET,
                    **value
                }
                resp=func.start(tmpvalue)
                data[key]=resp

        tmp=jsonify(data)
        return tmp
