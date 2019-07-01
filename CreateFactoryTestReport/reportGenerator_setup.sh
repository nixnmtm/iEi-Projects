#!/bin/sh
# install the dependencies for SScanning to run
sudo pip3 install -r requirements.txt
sudo apt-get install python3-tk
# Copy script to service path and grant permission
serviceName="reportGenerator"
projectPath="/home/test/EdgeServer/FactoryTestReport"
servicePath="/etc/systemd/system"
rm -rf ${projectPath}
mkdir ${projectPath}
cp -R generateReport ${projectPath}
chmod 777 -R ${projectPath}
cp ./${serviceName}.service ${servicePath}
chmod 777 ${servicePath}/${serviceName}.service
mkdir -p /home/test/reports
chmod 777 /home/test/reports

# reload system control to include the changes
systemctl daemon-reload