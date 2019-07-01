import paho.mqtt.client as mqtt
import json
import threading
import datetime
import requests
import signal
import logging,errno
import time

class CollectdMessage:
    def __init__(self, servername):
        self.servername = servername
        self.infoJar = {}
        self.callback=None

    # def start(self):
    #     thread = threading.Thread(target=self.startMQTT, args=())
    #     thread.daemon = True
    #     thread.start()

    def start(self,callback):
        self.callback=callback
        while True:
            try:
                client = mqtt.Client()
                client.on_connect = self.on_connect
                client.on_message = self.on_message
                client.username_pw_set("rmquser", "123456")
                client.connect(self.servername, 1883, 60)
                client.loop_forever()
                break
            except EnvironmentError as exc:
                logging.error("exc.errno {}".format(exc.errno))
                print("exc.errno {}".format(exc.errno))
                if exc.errno == errno.ECONNREFUSED:
                    time.sleep(3)
                    continue
                else:
                    raise # re-raise otherwise
                    break
            except Exception as error:
                print("error {}".format(error))
                logging.error("error {}".format(error))
                break


    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        logging.info("Connected with result code "+str(rc))
        client.subscribe("collectd/#")

    def on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        # print(type(msg.topic))
        # print(msg.topic)
        # print(type((msg.payload).decode("utf-8")))
        # print((msg.payload))
        # print((msg.payload).decode("utf-8"))
        # print("--------------")

        ## Main Course start here
        topic = msg.topic
        payload = str((msg.payload).decode("utf-8"))
        curHost = topic.split('/')[1]

        if 'cpu' in topic and 'active' in topic:
            value = payload.split(':')[1]
            timeStamp = payload.split(':')[0]
            self.checkHostExist(curHost)
            self.infoJar[curHost]["information"]["cpu"] = {
                "used" : format(float(value.rstrip('\x00')), '.2f')
            }
            self.checkTime(timeStamp, curHost)
        elif 'memory' in topic and 'used' in topic:
            value = payload.split(':')[1]
            timeStamp = payload.split(':')[0]
            self.checkHostExist(curHost)
            self.infoJar[curHost]["information"]["memory"] = {
                "used" : format(float(value.rstrip('\x00')), '.2f')
            }
            self.checkTime(timeStamp, curHost)
        elif 'thermal' in topic:
            value = payload.split(':')[1]
            timeStamp = payload.split(':')[0]
            self.checkHostExist(curHost)
            self.infoJar[curHost]["information"]["cpuTemperature"] = {
                "used" : format(float(value.rstrip('\x00')), '.2f')
            }
            self.checkTime(timeStamp, curHost)
        elif 'df' in topic:
            deviceName = topic.split('/')[2].replace('df-', '')
            dataType = topic.split('/')[3].split("-")[0]
            dataType_instance = topic.split('/')[3].split("-")[1]
            value = payload.split(':')[1].rstrip('\x00')
            timeStamp = payload.split(':')[0]
            self.checkHostExist(curHost)
            if self.infoJar[curHost]["information"].get("diskUsage") == None:
                self.infoJar[curHost]["information"]["diskUsage"] = {}

            if self.infoJar[curHost]["information"]["diskUsage"].get(deviceName) == None:
                self.infoJar[curHost]["information"]["diskUsage"][deviceName] = {
                    'ValuesPercentage' : {},
                    'valuesAbsolute' : {},
                    "capcity" : None
                }
                if dataType == 'percent_bytes':
                    self.infoJar[curHost]["information"]["diskUsage"][deviceName]['ValuesPercentage'] = {
                        dataType_instance : format(float(value), '.2f')
                    }
                elif dataType == 'df_complex':
                    self.infoJar[curHost]["information"]["diskUsage"][deviceName]['valuesAbsolute'] = {
                        dataType_instance : value
                    }
            else:
                if dataType == 'percent_bytes':
                    self.infoJar[curHost]["information"]["diskUsage"][deviceName]['ValuesPercentage'][dataType_instance] = format(float(value), '.2f')
                elif dataType == 'df_complex':
                    self.infoJar[curHost]["information"]["diskUsage"][deviceName]['valuesAbsolute'][dataType_instance] = value
            self.checkTime(timeStamp, curHost)
        elif 'interface' in topic:
            # print(msg.topic+" "+str(msg.payload))
            # print(type(msg.topic))
            # print(msg.topic)
            # print(type((msg.payload).decode("utf-8")))
            # print((msg.payload).decode("utf-8"))
            # print("--------------")

            interfaceName = topic.split('/')[2].replace('interface-', '')
            dataType = topic.split('/')[3]

            valueRx = payload.split(':')[1].rstrip('\x00')
            valueTx = payload.split(':')[2].rstrip('\x00')
            timeStamp = payload.split(':')[0]
            # print(interfaceName)
            # print(topic)
            # print(payload)
            # print(dataType)
            # print(timeStamp)
            # print(valueRx)
            # print(valueTx)
            # print("--------------")
            self.checkHostExist(curHost)
            if self.infoJar[curHost]["information"].get("interfaces") == None:
                self.infoJar[curHost]["information"]["interfaces"] = {
                    interfaceName : {
                        dataType : {
                            "rx" : valueRx,
                            "tx" : valueTx
                        }
                    }
                }
            else:
                if self.infoJar[curHost]["information"]["interfaces"].get(interfaceName) == None:
                    self.infoJar[curHost]["information"]["interfaces"][interfaceName] = {
                        dataType : {
                            "rx" : valueRx,
                            "tx" : valueTx
                        }
                    }
                else:
                    self.infoJar[curHost]["information"]["interfaces"][interfaceName][dataType] = {
                        "rx" : valueRx,
                        "tx" : valueTx
                    }
            self.checkTime(timeStamp, curHost)

    def checkoutResult(self, hostName):
        srtEmpty = "0"
        info=self.infoJar[hostName]["information"]
        result = {
            "hostName" : "sampleName",
            "serialno" : hostName,
            "timeStamp" : "{}.000000".format(self.infoJar[hostName]["timeStamp"]),
            "information" : {
                "cpu" : info["cpu"] if "cpu" in info else srtEmpty,
                "memory" : info["memory"] if "memory" in info else srtEmpty,
                "cpuTemperature" : info["cpuTemperature"] if "cpuTemperature" in info else srtEmpty,
                "diskUsage" : {
                    "usage" : []
                },
                "interfaces" : {
                    "usage" : []
                }
            }
        }
        if self.infoJar[hostName]["information"].get("diskUsage") != None:
            deviceNumber = 0
            totalCapcity = 0
            totalFree = 0
            totalUsed = 0
            totalReserve = 0

            for device in self.infoJar[hostName]["information"]["diskUsage"]:
                # if device.find('boot') is -1:
                values = self.infoJar[hostName]["information"]["diskUsage"][device]['valuesAbsolute']
                capcity = int(values['used']) + int(values['free']) + int(values['reserved'])
                totalCapcity = totalCapcity + capcity
                deviceNumber = deviceNumber + 1
                totalFree = totalFree + int(values['free'])
                totalUsed = totalUsed + int(values['used'])
                totalReserve = totalReserve + int(values['reserved'])
                self.infoJar[hostName]["information"]["diskUsage"][device]['capcity'] = capcity
                self.infoJar[hostName]["information"]["diskUsage"][device]['deviceName'] = device
                result["information"]["diskUsage"]["usage"].append(self.infoJar[hostName]["information"]["diskUsage"][device])

            result["information"]["diskUsage"]["deviceNumber"] = deviceNumber
            result["information"]["diskUsage"]["totalCapcity"] = totalCapcity
            result["information"]["diskUsage"]["totalFree"] = totalFree
            result["information"]["diskUsage"]["totalUsed"] = totalUsed
            result["information"]["diskUsage"]["totalReserve"] = totalReserve
            result["information"]["diskUsage"]["totalFreePercent"] = format(totalFree / totalCapcity, '.4f')
            result["information"]["diskUsage"]["totalUsedPercent"] = format(totalUsed / totalCapcity, '.4f')
            result["information"]["diskUsage"]["totalReservePercent"] = format(totalReserve / totalCapcity, '.4f')
        if self.infoJar[hostName]["information"].get("interfaces") != None:
            for interfaceName in self.infoJar[hostName]["information"]["interfaces"]:
                self.infoJar[hostName]["information"]["interfaces"][interfaceName]["interfaceName"] = interfaceName
                result["information"]["interfaces"]["usage"].append(self.infoJar[hostName]["information"]["interfaces"][interfaceName])

        # print("Collected Result:")
        # print(result)
        # self.reportAbnormal(result)
        self.generalInfoSend(result)

    def checkHostExist(self, newHost):
        if self.infoJar.get(newHost) == None:
            self.infoJar[newHost] = {
                "timeStamp" : "",
                "information" : {}
            }

    def checkTime(self, timeStamp, curHost):
        newTime = datetime.datetime.fromtimestamp(
                    int(float(timeStamp))
                ).strftime('%Y-%m-%d %H:%M:%S')
        if newTime != self.infoJar[curHost]["timeStamp"]:
            self.infoJar[curHost]["timeStamp"] = newTime
            threading.Timer(1, self.checkoutResult, [curHost]).start()

    def generalInfoSend(self, result):
        result["timeStamp"] = result["timeStamp"][:-3]
        self.callback(result)

    # http://10.10.70.89:3000/puzzle/api/v1/log/usage
    def reportAbnormal(self, result):
        if (float(result["information"]["cpu"]["used"]) >= 75):
            data = {
                "serialno" : result["serialno"],
                "name" : "cpuHigh",
                "timeStamp" : result["timeStamp"],
                "usage" : result["information"]["cpu"]["used"]
            }
            dataRabbit = json.dumps(data)
            data["timeStamp"] = data["timeStamp"][:-3]
            dataMQTT = json.dumps(data)
            # urlRabbit = 'http://10.10.70.89:3000/puzzle/api/v1/log/usage'
            urlRabbit = 'http://127.0.0.1:3000/puzzle/api/v1/log/usage'
            # urlMQTT = 'http://127.0.0.1:5001/alarmlog'
            url = 'http://{}:{}/alarmlog'.format("localhost", 8882)
            # self.postData(urlRabbit, dataRabbit)
            self.postData(urlMQTT, dataMQTT)
            # headers = {'Content-type': 'application/json'}
            # responseRabbit = requests.post(urlRabbit, dataRabbit, headers=headers, timeout=2)
            # responseMQTT = requests.post(urlMQTT, dataMQTT, headers=headers, timeout=2)
            # print('Response Code: ', responseRabbit.status_code)
            # print('Response Code: ', responseMQTT.status_code)

    # url = 'http://10.10.70.89:4000/notifications/usage'
    def notifyAbnormal(self, result):
        if (float(result["information"]["cpu"]["used"]) >= 75):
            data = {
                "serialno" : result["serialno"],
                "name" : "cpuHigh",
                "timeStamp" : result["timeStamp"],
                "usage" : result["information"]["cpu"]["used"]
            }
            dataRabbit = json.dumps(data)
            data["timeStamp"] = data["timeStamp"][:-3]
            dataMQTT = json.dumps(data)
            url = 'http://10.10.70.89:4000/notifications/usage'
            urlRabbit = 'http://127.0.0.1:3000/puzzle/api/v1/log/usage'
            # urlMQTT = 'http://127.0.0.1:3000/puzzle/api/v1/log/usage'
            headers = {'Content-type': 'application/json'}
            responseRabbit = requests.post(urlRabbit, dataRabbit, headers=headers)
            responseMQTT = requests.post(urlMQTT, dataMQTT, headers=headers)
            print('Response Code: ', responseRabbit.status_code)
            print('Response Code: ', responseMQTT.status_code)

    def postData(self, url, data):
        try:
            headers = {'Content-type': 'application/json'}
            response = requests.post(url, data, headers=headers, timeout=1)
            print('Response Code: ', response.status_code)
        except Exception as error:
            print(error)

# def quit_gracefully(*args):
#     print ('quitting loop')
#     exit(0);
#
# if __name__ == "__main__":
#     # CollectdMessage("10.10.70.91").start()
#     ipArray = ["127.0.0.1"]
#
#     for ipAddr in ipArray:
#         CollectdMessage(ipAddr).start()
#
#     signal.signal(signal.SIGINT, quit_gracefully)
#
#     try:
#         print ('start loop')
#         while True:
#             pass
#     except KeyboardInterrupt:
#         quit_gracefully()
