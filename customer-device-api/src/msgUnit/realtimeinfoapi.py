from flask import  request, jsonify
from datetime import datetime
import os, platform
import threading
import subprocess
from msgUnit.marvell_temp import devComport as temp
from msgUnit.marvell_fan import fanComport as fan
from msgUnit.mqttClient import CollectdMessage
from msgUnit.realtimeInfo import puzzleDevices, mqttConnList
import copy


class main:
    def __init__(self,app):
        self.startMQTT()
        app.add_url_rule('/realtimeInfo', 'realtimeInfo', self.realtimeInfo, methods=['GET'])
        self.myfan=fan()
        self.myTemp=temp()

    def startMQTT(self):
        print("MQTT START")
        thread = threading.Thread(target=CollectdMessage("127.0.0.1").start, args=(self.collectdMessageCallback,))
        thread.daemon = True
        thread.start()
        return "startMQTT"
    def collectdMessageCallback(self,infoJar):
        fans = self.getFan()
        temp = self.getTemp()
        timeInterval = None
        if puzzleDevices.get(infoJar["serialno"]) != None:
            if puzzleDevices[infoJar["serialno"]]["infoJar"] == None:
                infoJar["information"]["fans"] = fans
                infoJar["information"]["cpuTemperature"] = temp
                infoJar["prevTimeStamp"] = infoJar["timeStamp"]
                newUsage = copy.deepcopy(infoJar["information"]["interfaces"]["usage"])
                for item in newUsage:
                    item["speed"] = {
                        "inSpeed"  : 0,
                        "outSpeed" : 0
                    }
                infoJar["information"]["interfaces"]["usage"] = newUsage
            else:
                prevTime = puzzleDevices[infoJar["serialno"]]["infoJar"]["prevTimeStamp"]
                curTime = infoJar["timeStamp"]
                infoJar["prevTimeStamp"] = infoJar["timeStamp"]
                FMT = '%Y-%m-%d %H:%M:%S.%f'
                timeDiff = datetime.strptime(curTime, FMT) - datetime.strptime(prevTime, FMT)
                timeInterval = timeDiff.seconds
                prevUsage = copy.deepcopy(puzzleDevices[infoJar["serialno"]]["infoJar"]["information"]["interfaces"]["usage"])
                newUsage = copy.deepcopy(infoJar["information"]["interfaces"]["usage"])
                for i in range(len(newUsage)):
                    try:
                        inSpeed = int( (int(newUsage[i]["if_octets"]["rx"]) - int(prevUsage[i]["if_octets"]["rx"]) ) / timeInterval)
                        outSpeed = int( (int(newUsage[i]["if_octets"]["tx"]) - int(prevUsage[i]["if_octets"]["tx"]) ) / timeInterval)
                        newUsage[i]["prevOctets"] = newUsage[i]["if_octets"]
                        newUsage[i]["speed"] = {
                            "inSpeed"  : inSpeed * 8,
                            "outSpeed" : outSpeed * 8
                        }
                    except Exception as e:
                        print("Exception:")
                        print(str(e))
                infoJar["information"]["interfaces"]["usage"] = newUsage
                infoJar["information"]["fans"] = fans
                infoJar["information"]["cpuTemperature"] = temp
            puzzleDevices[infoJar["serialno"]]["infoJar"] = infoJar
            return {"message" : "Info Recorded"}
        else:
            puzzleDevices[infoJar["serialno"]] = {
                "ipAddr" : "127.0.0.1",
                "minMax" : {
                    "history" : [],
                    "curMin" : 100,
                    "curMax" : 0
                },
                "infoJar" : None
            }
            return {"message" : "Device not Recorded"}

    def realtimeInfo(self):
        info = None
        for puzzle in puzzleDevices:
            # print("--- puzzleDevices puzzleSN :  {}".format(puzzle))
            if puzzleDevices[puzzle]["infoJar"] != None:
                info = puzzleDevices[puzzle]["infoJar"]
                # print("*** puzzleDevices info:  {}".format(info))
        return jsonify(info)

    def getFan(self):
        myPlatform = platform.machine()
        pwd = os.path.dirname(os.path.realpath(__file__))
        myFan = []
        if myPlatform != "aarch64":
            exe_path = pwd + "/tools/fan"
            if os.path.exists(exe_path):
                cmdFan = subprocess.Popen(exe_path, stdout=subprocess.PIPE)
                stdoutFan = cmdFan.stdout.read().decode("utf-8").strip()
                myFan = list(stdoutFan.split(" "))
                # print("getFan : {}".format(stdoutFan))
        else:
            myFan=self.myfan.start()
            print("myFan in realtime {}".format(myFan))

        return myFan
    def getTemp(self):
        myPlatform = platform.machine()
        pwd = os.path.dirname(os.path.realpath(__file__))
        myTemp = 0
        if myPlatform != "aarch64":
            exe_path = pwd + "/tools/cpu"
            if os.path.exists(exe_path):
                cmdTemp = subprocess.Popen(exe_path, stdout=subprocess.PIPE)
                stdoutTemp = cmdTemp.stdout.read().decode("utf-8").strip()
                myTemp = int(stdoutTemp)
                # print("get CPU temperature : {}".format(stdoutTemp))
        else:
            myTemp=self.myTemp.start()
            print("myTemp in realtime {}".format(myTemp))
        return myTemp
