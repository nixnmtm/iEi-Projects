#!/usr/bin/env python

import sys
import pika
import json
import logging
import requests
import time
#from device_client.utils import pzlutils, hwinfo
from utils import pzlutils, hwinfo

pzl = pzlutils.PZLutils()

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s',
               datefmt='%m/%d/%Y %I:%M:%S %p',
               filename='dScanning.log',
               filemode='w',
               level=logging.ERROR)

def populate_data(data):
    hw_info = {}
    #get_dev_slno = pzl.this_device_slno()
    get_dev_slno = sn
    logging.info("Populating hardware datas from device ===> Sl.No: {}".format(get_dev_slno))
    hw_info["operationId"] = data["operationId"]
    hw_info["operatorId"] = data["operatorId"]
    hw_info["scanMode"] = data["scanMode"]
    hw_info["sn"] = get_dev_slno
    hw_info["ip"] = pzl.get_own_ip()
    temp = hwinfo.pci_info()
    hw_info["macinfo"] = {}
    for k in temp["pciinfo"].keys():
        hw_info["macinfo"][temp["pciinfo"][k]["interface"]] = {}
        hw_info["macinfo"][temp["pciinfo"][k]["interface"]]["macaddr"] = temp["pciinfo"][k]["macaddr"]
    print(hw_info)
    return hw_info

def callback(ch, method, properties, body):
    data = pzl.read_json(body)
    print(data)
    try:
        if data["action"] == 1: # configured with assumption that only start action is available
            logging.info("{}Scanning Initiated{}".format("-"*10, "-"*10))
            hw_info = populate_data(data)
            ch.queue_declare(queue='hwinfo_queue', durable=True)
            if not hw_info: # if dictionary is empty
                pass
                logging.warning("No hw_info fetched from local device")
            else: # publishing to server from client only if the device is present

                logging.info("Publishing to device server side")
                ch.basic_publish(exchange='',
                                  routing_key='hwinfo_queue',
                                  body=json.dumps(hw_info))
                                  #properties=pika.BasicProperties(delivery_mode=2))
    except Exception as e:
        logging.error("**Scanning not initiated. " + str(e))

def run(host, ex_name, ex_type, username, password, port):
    while True:
        try:
            credentials = pika.PlainCredentials(username=username, password=password)
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
            channel = connection.channel()
            channel.exchange_declare(exchange=ex_name,
                                     exchange_type=ex_type)
            result = channel.queue_declare(exclusive=True)
            queue_name = result.method.queue
            channel.queue_bind(exchange=ex_name, queue=queue_name)
            logging.info('[*] Waiting to start scan. To exit press CTRL+C')
            channel.basic_consume(callback, queue=queue_name, no_ack=True)
            channel.start_consuming()
        except pika.exceptions.ConnectionClosed as e:
            # print("ConnectionClosed error:{}".format(e))
            logging.error("Unexpected error {}...{}".format(ex_name, sys.exc_info()))
            continue


def calldeviceInfoApi(data):
    retData = {}
    while True:
        try:
            url = 'http://{}:{}/deviceInfo'.format("localhost", 8882)
            headers = {'Content-type': 'application/json'}
            r = requests.post(url, data, headers=headers)
            print('Response Code: ', r.status_code)
            if r.status_code == 200:
                retData["result"] = 1
                retData["data"] = json.loads(r.text)
            else:
                retData["result"] = 2
            break
        except requests.exceptions.ConnectionError as e:
            print("API ConnectionError error:{} {}...{}".format(url, data, e))
            time.sleep(1)
        except:
            print("callapi Unexpected error {}...{}".format(data, sys.exc_info()))
            time.sleep(1)

    return retData

def myInput():
    retData = {}
    inputdata = {
        "config": {
            "name": [1] # 1 is for RabbitMQ, refer http://40.74.91.221/puzzle/device-all-factory/tree/master/deviceAgent
        },
        "device": {
            "name": [0]
        }
    }
    tmp = json.dumps(inputdata)
    tmpapi = calldeviceInfoApi(tmp)
    if tmpapi["result"] == 1: # PASS:
        rabbitMQ = {}
        sn = None
        flag = 0
        apidata = tmpapi["data"]
        tmp = apidata["config"]
        for loop in tmp:
            data = loop["data"]
            if loop["name"] == 1:
                if isinstance(data, dict):
                    flag = flag + 1
                    rabbitMQ["username"] = data["user"]
                    rabbitMQ["password"] = data["password"]
                    rabbitMQ["host"] = data["ip"]
                    rabbitMQ["port"] = data["port"]
        tmp = apidata["device"]
        for loop in tmp:
            data = loop["data"]
            if loop["name"] == 0:
                if len(data) > 0:
                    flag = flag + 1
                    sn = data
        if flag == 2:
            retData["result"] = 1 # PASS
            retData["rabbitMQ"] = rabbitMQ
            retData["sn"] = sn
        else:
            retData["result"] = 2
        print("myInput retData {}".format(data))
    else:
        retData["result"] = 2
    return retData


if __name__ == '__main__':

    myInputData = myInput()
    if myInputData["result"] == 1:
        mqdata = myInputData["rabbitMQ"]
        sn = myInputData["sn"]
        print(mqdata)

        # mqhost = "10.10.70.89"
        # mqport = 5672
        # mqusername = "rmquser"
        # mqpassword = "123456"

        ex_name = "devicescan"
        ex_type = 'fanout'
        mqhost = mqdata['host']
        mqport = int(mqdata['port'])
        mqusername = mqdata["username"]
        mqpassword = mqdata["password"]

        run(mqhost, ex_name, ex_type, mqusername, mqpassword, mqport)
