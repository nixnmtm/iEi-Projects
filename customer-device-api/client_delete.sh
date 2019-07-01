#!/bin/bash
serviceName="customerDevice"
servicePath="/home/puzzle/"$serviceName"API"
rm -r $servicePath
rm /etc/systemd/system/$serviceName.service
