#!/bin/bash
systemctl stop docker
systemctl disable docker
dpkg --purge docker.io
rm docker.io_17.03.2-0ubuntu3_arm64.deb
sudo groupdel docker
sudo apt-get -y autoremove
sudo apt-get clean all
sudo apt-get update