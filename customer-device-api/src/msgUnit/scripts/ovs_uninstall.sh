#!/bin/bash
cd /usr/src/openvswitch-2.9.2
make uninstall
cd /usr/src
rm dpdk-17.11.2.tar.xz
rm -rf dpdk-stable-17.11.2
rm openvswitch-2.9.2.tar.gz
rm -rf openvswitch-2.9.2
sed -i '/export DPDK.*/d' ~/.bashrc
sed -i '/export OVS.*/d' ~/.bashrc
sed -i '/export PATH.*/d' ~/.bashrc
sed -i '/export VHOST.*/d' ~/.bashrc
sed -i '/export DB_SOCK.*/d' ~/.bashrc