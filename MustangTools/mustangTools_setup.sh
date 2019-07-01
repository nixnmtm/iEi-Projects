#!/bin/sh
pip3 install -r requirements.txt
# Copy script to service path and grant permission
serviceName="mustangTools"
projectPath="/home/test/EdgeServer/mustangTools"
servicePath="/etc/systemd/system"
rm -rf $projectPath
mkdir $projectPath
cp -R ./mustangTools.py $projectPath
chmod 777 -R $projectPath
cp ./${serviceName}.service $servicePath
chmod 777 $servicePath/${serviceName}.service
# reload system control to include the changes
systemctl daemon-reload