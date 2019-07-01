#!/bin/bash
sudo apt-get update
wget https://launchpad.net/ubuntu/+source/docker.io/17.03.2-0ubuntu3/+build/14377888/+files/docker.io_17.03.2-0ubuntu3_arm64.deb
sudo dpkg -i docker.io_17.03.2-0ubuntu3_arm64.deb
DEBIAN_FRONTEND=noninteractive sudo apt-get -qq install --fix-broken
sudo apt-get update
systemctl enable docker
systemctl start docker