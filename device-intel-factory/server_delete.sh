#!/bin/sh

# remove the service file and project files

serviceName="sScanning"
projectPath="/home/test/EdgeServer/"$serviceName"Server"
servicePath="/etc/systemd/system"
rm -rf $projectPath
rm -rf $servicePath/${serviceName}@.service

