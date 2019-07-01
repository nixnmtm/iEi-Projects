#!/usr/bin/env bash

# Install VPP
echo "****Setting up for vpp installation****"
export UBUNTU="xenial"

### If you need specific version uncomment below and input version needed
#unset -v RELEASE
#export RELEASE=".stable.1807"
#sudo rm /etc/apt/sources.list.d/99fd.io.list
#echo "deb [trusted=yes] https://nexus.fd.io/content/repositories/fd.io$RELEASE.ubuntu.$UBUNTU.main/ ./" | sudo tee -a /etc/apt/sources.list.d/99fd.io.list

### This will install latest Release, if using specific version comment next 2 lines
sudo rm /etc/apt/sources.list.d/99fd.io.list
echo "deb [trusted=yes] https://nexus.fd.io/content/repositories/fd.io.ubuntu.$UBUNTU.main/ ./" | sudo tee -a /etc/apt/sources.list.d/99fd.io.list

sudo apt-get -y update
sudo apt-get -y --fix-missing install vpp vpp-plugins vpp-api-java vpp-api-lua vpp-api-python vpp-dbg vpp-dev

# Install vpp-config tool (Easy to handle)
echo "****Installing vpp-config tool****"
sudo apt-get -y install python-pip
sudo pip install vpp-config