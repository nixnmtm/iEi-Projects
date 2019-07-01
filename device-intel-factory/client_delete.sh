#!/bin/sh

# remove the service file and project files
serviceName="dScanning"
projectPath="/home/puzzle/"$serviceName"Client"
servicePath="/etc/systemd/system"
rm -rf $projectPath
rm -rf $servicePath/${serviceName}.service