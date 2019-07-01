#!/bin/sh
# remove the service file and project files
serviceName="reportGenerator"
projectPath="/home/test/EdgeServer/FactoryTestReport"
servicePath="/etc/systemd/system"
rm -rf ${projectPath}
rm -rf ${serviceName}/${serviceName}.service

