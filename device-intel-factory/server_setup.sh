#!/bin/sh

# install the dependencies for SScanning to run
pip3 install more-itertools

# Copy script to service path and grant permission
serviceName="sScanning"
projectPath="/home/test/EdgeServer/"$serviceName"Server"
servicePath="/etc/systemd/system"
rm -rf $projectPath
mkdir $projectPath
cp -R ./device_server/server_scan.py $projectPath
chmod 777 -R $projectPath
cp ./${serviceName}@.service $servicePath
chmod 777 $servicePath/${serviceName}@.service

# reload system control to include the changes
systemctl daemon-reload
