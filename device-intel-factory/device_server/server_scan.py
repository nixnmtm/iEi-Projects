#!/usr/bin/env python

import pika
import json
import logging
import requests
import more_itertools as mit
import sys

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s',
               datefmt='%m/%d/%Y %I:%M:%S %p',
               filename='sScanning.log',
               filemode='w',
               level=logging.WARNING)

all_dev = []
devfound = []
devsucess = {}
post_api = 1  # if (0: dont POST, 1: POST)

def read_json(json_data):
    """Convert bytes datatype to str"""

    if type(json_data) == bytes:
        data = json_data.decode('ascii')
        data = json.loads(data)
        return data
    if type(json_data) == str:
        data = json.loads(json_data)
        return data


def get_mesdevinfo(devid):

    """Get MES device info from deviceinfo API"""

    devid = str(devid)
    querystring = {"serialNo": devid}
    headers = {
        'Cache-Control': "no-cache",
        'Postman-Token': "4e74f131-a27f-4aa1-82da-54fa4d646344"
    }
    devinfo_url = "http://" + apihost + ":" + str(apiport) + "/puzzle/api/v1/deviceInfo/getById"
    mesdevinfo = requests.request("GET", devinfo_url, params=querystring, headers=headers)

    try:
        mesdevinfo = json.loads(mesdevinfo.text)
        if mesdevinfo["info"] == "Device is not registered":
            logging.error("{} is not registered".format(devid))
            devfound.remove(devid) # if not registrered remove from devices found
            return None
        elif mesdevinfo["info"]["vpdInfo"] and mesdevinfo["info"]["serialNo"] == devid:
            return mesdevinfo
        else:
            return mesdevinfo
    except RuntimeWarning:
        logging.error("No device info found")

def notify(devs, oprerationId):

    """
    Notify to notification API

    dev     : device id or operation id
            : datatype: String
    status  : error or success message
            : datatype: String

    """
    if post_api == 1:
        try:
            headers = {'Content-Type': "application/json"}
            note = {}
            note["operationId"] = oprerationId
            note["scanMode"] = all_dev[0]["scanMode"]
            note["scanInfo"] = []
            if len(list(devs.keys())) > 0:
                for sdev in list(devs.keys()):
                    dev_status = dict()
                    dev_status["serialNo"] = sdev
                    dev_status["ip"] = devs[sdev]["ip"]
                    dev_status["productName"] = devs[sdev]["productName"]
                    dev_status["result"] = "Success"
                    note["scanInfo"].append(dev_status)
            senddata = json.dumps(note)
            print("NOTIFICATION:\n", senddata)
            logging.info("Sending notification of {}".format(oprerationId))
            notifyurl = "http://" + apihost + ":" + str(notifyport) + "/puzzle/api/v1/notifications/devicescan"
            r = requests.post(url=notifyurl, headers=headers, data=senddata)
            logging.info('Notification Response Code: {}'.format(r.status_code))

        except Exception as e:
            logging.error("Damn, error in posting notification")

def postlog_deviceinfo(info):

    """Post compared data with status to device info API"""
    if post_api == 1:
        try:
            headers = {'Content-Type': "application/json"}
            senddata = json.dumps(info)
            print("LOG DATA:\n", senddata)
            # print("Final Data:\n{}".format(json.dumps(finaldict, sort_keys=True, indent=4, separators=(',', ': '))))
            logging.info("Posting device info")
            log_url = "http://" + apihost + ":" + str(apiport) + "/puzzle/api/v1/log/deviceScan"
            r = requests.post(url=log_url, headers=headers, data=senddata)
            logging.info('Log Response Code: {}'.format(r.status_code))

        except Exception as e:
            logging.error("Damn, error in posting device info")

def post2pair(devs, operationid):

    """Post the devices that has scanned successfull to Pair API (PUZZLE MODE)"""

    pairdevs = {}
    pairdevs["operationId"] = operationid
    pairdevs["snArray"] = list(devs.keys())

    try:
        headers = {'Content-Type': "application/json"}
        if len(pairdevs["snArray"]) >= 2:
            senddata = json.dumps(pairdevs)
            logging.warning("Devices passed scanning and sent to pairing: {}".format(devs))
            pair_url = "http://" + apihost + ":" + str(apiport) + "/puzzle/api/v1/operations/pair"
            r = requests.post(url=pair_url, headers=headers, data=senddata)
            logging.info('Pair Response Code: {}'.format(r.status_code))
        else:
            logging.warning("Devices passed scanning is less than 2")

    except Exception as e:
        logging.error("Damn, error in posting devices to pair")

def post2directburn(devs, operationid, operatorid, scanmode):

    """Post the devices that has scanned successfull direct to burn (GRAND MODE)"""

    scandevs = {}
    scandevs["operationId"] = operationid
    scandevs["operatorId"] = operatorid
    scandevs["scanMode"] = scanmode
    scandevs["snArray"] = devs

    try:
        headers = {'Content-Type': "application/json"}
        senddata = json.dumps(scandevs)
        print(senddata)
        logging.info("Devices passed scanning and sent to burning: {}".format(devs)) # this mode skips pairing
        directburn_url = "http://" + apihost + ":" + str(apiport) + "/puzzle/api/v1/operations/burn"
        r = requests.post(url=directburn_url, headers=headers, data=senddata)
        logging.info('directBurn Response Code: {}'.format(r.status_code))

    except Exception as e:
        logging.error("Damn, error in posting devices to pair")

# def post2setconfig(devs, operationid):
#
#     """Post the devices that has scanned successfull to Pair API (PUZZLE MODE)"""
#
#     try:
#         headers = {'Content-Type': "application/json"}
#         senddata = json.dumps(pairdevs)
#         pair_url = "http://" + apihost + ":" + str(apiport) + "/puzzle/api/v1/operations/setburnconfig"
#         r = requests.post(url=pair_url, headers=headers, data=senddata)
#         logging.info('Pair Response Code: {}'.format(r.status_code))
#
#     except Exception as e:
#         logging.error("Damn, error in posting devices to pair")


def accumulate_all(all_dev):
    try:
        alldevresponse = {}
        scaninfo = []
        for num, devs in enumerate(all_dev):
            info = {}
            for k, v in devs.items():
                if k == "sn":
                    devsucess[devs[k]] = {}
                    info["sn"] = devs[k]
                    info["macInfo"] = {}
                    info["productName"] = devs["productName"]
                    devsucess[devs[k]]["productName"] = devs["productName"]
                    info["ip"] = devs["ip"]
                    devsucess[devs[k]]["ip"] = devs["ip"]
            scaninfo.insert(num, info)

        alldevresponse["operationId"] = all_dev[0]["operationId"]
        alldevresponse["operatorId"] = all_dev[0]["operatorId"]
        alldevresponse["scanMode"] = all_dev[0]["scanMode"]
        alldevresponse["scanInfo"] = scaninfo
        alldevresponse["pairInfo"] = []

        return alldevresponse
    except Exception as e:
        logging.error("Error in accumulating data ---> " + str(e))

def scanningReal():

    """ ** Real scanning that calls all the functions
    """
    global all_dev
    global devfound
    global devsucess

    try:
        logging.info("Devices Scanned: {}".format(devfound))
        if all_dev:  # if all_dev is not empty, enter
            alldevinfo = accumulate_all(all_dev)
            if alldevinfo:  # if alldevinfo is not empty, enter
                #if alldevinfo["scanMode"] == 0:
                postlog_deviceinfo(alldevinfo)
                post2pair(devsucess, alldevinfo["operationId"])
                notify(devsucess, alldevinfo["operationId"]) # Notify the device status
                # else:
                #     logging.error("Unknown scanMode: {}".format(alldevinfo["scanMode"]))
        logging.info("Resume consuming")
        all_dev = []
        devfound = []
        devsucess = {}

    except Exception as e:
        logging.error("Real scanning failed ---> " + str(e))


def get_burnstatus(devid):
    querystring = {"serialNo": devid}
    headers = {'Content-Type': "application/json"}
    devburnurl = "http://" + apihost + ":" + str(apiport) + "/puzzle/api/v1/deviceStatus/getBurningStatus"
    r = requests.get(url=devburnurl, headers=headers, params=querystring)
    resp = r.json()
    return resp["info"]["burnInStatus"]


timer_id = None
def callback(ch, method, properties, body):

    """Receive local_device info and
    do compare and send number of devices found"""
    try:
        # Timer for stop receiving
        global timer_id
        if timer_id is not None:
            ch.connection.remove_timeout(timer_id)
        data = read_json(json_data=body)
        logging.info("Received in server:\n{}".format(data))
        local_devid = data["sn"]
        burnin = get_burnstatus(local_devid)
        if not burnin: # if burnIn Status is false, then proceed
            logging.info("{} --> burnInStatus: {}".format(local_devid, burnin))
            devfound.append(local_devid) # collect the devices replied
            #  mesinfo comparision
            mesinfo = get_mesdevinfo(devid=local_devid)
            if not mesinfo:  # if mesinfo is None
                print("{} -- > MES info is none".format(local_devid))
                timer_id = ch.connection.add_timeout(5, scanningReal)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                data["productName"] = mesinfo["info"]["vpdInfo"]["productName"]
                timer_id = ch.connection.add_timeout(5, scanningReal)  # timeout, send received details and resume consuming
                all_dev.append(data)
                print("all_dev:\n", all_dev)
                ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            logging.info("{} is in Burn-In Stage. Skipping".format(local_devid))
            timer_id = ch.connection.add_timeout(5, scanningReal)
            ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.warning("Some internal error has occured --> " + str(e))
        ch.basic_ack(delivery_tag=method.delivery_tag)


def run(host, queue_name, username, password, port):

    """Establish connection and run"""
    pcount = 0
    ncount = 0
    while True:
        try:
            credentials = pika.PlainCredentials(username=username, password=password)
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,
                                                                           port=port,
                                                                           credentials=credentials))
            channel = connection.channel()
            print("RMq connected count: ", pcount)
            channel.queue_declare(queue=queue_name, durable=True)
            logging.info('[*] Waiting for client device information. To exit press CTRL+C')
            print('[*] Waiting for client device information. To exit press CTRL+C')
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(callback, queue=queue_name)
            channel.start_consuming()
            pcount += 1
        except Exception as e:
            print("RMq not connected. Attempting to connect, count:", ncount)
            ncount += 1
            #logging.error("Connection to server not established")
            pass


if __name__ == '__main__':

    if len(sys.argv) > 1:
        mqhost = str(sys.argv[1])
        mqport = int(sys.argv[2])
        mqusername = str(sys.argv[3])
        mqpassword = str(sys.argv[4])
        apihost = str(sys.argv[5])
        apiport = int(sys.argv[6])
        notifyport = int(sys.argv[7])

    else:
        mqhost = "10.10.70.151"
        mqport = 5672
        mqusername = "rmquser"
        mqpassword = "123456"
        apihost = "10.10.70.151"
        apiport = 3000
        notifyport = 3000

    queue_name = 'hwinfo_queue'



    run(mqhost, queue_name,  mqusername, mqpassword, mqport)


