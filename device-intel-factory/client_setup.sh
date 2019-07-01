#!/bin/sh

# install the dependencies for dScanning to run
pip3 install -r requirements.txt

# Copy script to service path and grant permission
serviceName="dScanning"
projectPath="/home/puzzle/"$serviceName"Client"
servicePath="/etc/systemd/system"
rm -rf $projectPath
mkdir $projectPath
cp -R device_client $projectPath
chmod 777 -R $projectPath
cp ./${serviceName}.service $servicePath
chmod 777 $servicePath/${serviceName}.service

# reload system control to include the changes
systemctl daemon-reload
