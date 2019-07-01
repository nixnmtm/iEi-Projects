#!/usr/bin/env python
import pika
import json

data = {}
def scan():
    """To start scan"""
    credentials = pika.PlainCredentials(username="rmquser", password="123456")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="10.10.70.89", port=5672, credentials=credentials))
    channel = connection.channel()
    # connection = pika.BlockingConnection(
    #     pika.ConnectionParameters(host="192.168.0.118", port=5672, credentials=credentials))
    # if connection.is_open:
    #     print('OK')
    # else:
    #     print("NOt OK")
    # channel = connection.channel()
    # channel.queue_declare(queue='hwinfo_queue', durable=True)
    # channel.basic_publish(exchange='',
    #                  routing_key='hwinfo_queue',
    #                  body="HI dear friends")
    channel.exchange_declare(exchange='devicescan', exchange_type='fanout')
    data["operationId"] = "shgbshjhdstiuy978677"
    data["action"] = 1
    json_data = json.dumps(data)
    channel.basic_publish(exchange='devicescan',
                          routing_key='',
                          body=json_data)
    print(" [x] Sent from dummy server {}".format(json_data))
    connection.close()
scan()


