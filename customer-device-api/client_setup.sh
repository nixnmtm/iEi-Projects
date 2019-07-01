#!/bin/bash
## check platform
platform='unknown'
unamestr=`uname -m`
echo $unamestr
if [[ "$unamestr" == 'aarch64' ]]; then
   platform='arm'
elif [[ "$unamestr" == 'x86_64' ]]; then
   platform='x86_64'
fi

if [[ $platform == 'arm' ]]; then
  sudo pip3 install -r requirements_marvell.txt
elif [[ $platform == 'x86_64' ]]; then
  sudo pip3 install -r requirements.txt
fi



serviceName="customerDevice"
servicePath="/home/puzzle/"$serviceName"API"
rm -r $servicePath
cp -R src $servicePath
chmod 777 -R $servicePath
cp ./$serviceName.service /etc/systemd/system/
chmod 777 /etc/systemd/system/$serviceName.service
systemctl daemon-reload
