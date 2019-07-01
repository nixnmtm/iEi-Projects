#!/bin/bash
checkport=$(sudo netstat -tulp | grep kubectl)
if [ "${checkport}" = " " ]; then
    systemctl start launchkubedb@\"$1\".service
else
    lsof -i tcp:8001 | grep LISTEN | awk '{print $2}' | xargs kill
    echo "Restarting launchkubedb service"
    systemctl start launchkubedb@\"$1\".service
fi