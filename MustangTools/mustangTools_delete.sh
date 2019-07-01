#!/bin/sh
# remove the service file and project files
serviceName="mustangTools"
projectPath="/home/test/EdgeServer/mustangTools"
servicePath="/etc/systemd/system"
rm -rf $projectPath
rm -rf $servicePath/${serviceName}.service