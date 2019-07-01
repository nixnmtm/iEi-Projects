#!/bin/bash
# Setup environment variables
export DPDK_DIR=/usr/src/dpdk-stable-17.11.2
export DPDK_TARGET=x86_64-native-linuxapp-gcc
export DPDK_BUILD=$DPDK_DIR/$DPDK_TARGET
export DB_SOCK=/usr/local/var/run/openvswitch/db.sock
export PATH=$PATH:/usr/local/share/openvswitch/scripts
export OVS_DIR=/usr/src/openvswitch-2.9.2
export VHOST_USER_SOCK_DIR=/usr/local/var/run/openvswitch

echo "export DPDK_DIR=/usr/src/dpdk-stable-17.11.2" >> ~/.bashrc
echo "export DPDK_TARGET=x86_64-native-linuxapp-gcc" >> ~/.bashrc
echo "export DPDK_BUILD=$DPDK_DIR/$DPDK_TARGET" >> ~/.bashrc
echo "export PATH=$PATH:/usr/local/share/openvswitch/scripts" >> ~/.bashrc
echo "export DB_SOCK=/usr/local/var/run/openvswitch/db.sock" >> ~/.bashrc
echo "export OVS_DIR=/usr/src/openvswitch-2.9.2" >> ~/.bashrc
echo "export VHOST_USER_SOCK_DIR=/usr/local/var/run/openvswitch" >> ~/.bashrc
source ~/.bashrc

sudo apt-get -y install m4 bison flex
wget http://www.tcpdump.org/release/libpcap-1.8.1.tar.gz
tar -xvf libpcap-1.8.1.tar.gz
cd libpcap-1.8.1
./configure
make
make install
sudo ln -s /usr/local/lib/libpcap.so.1 /usr/lib/libpcap.so.1
apt-get -y install libnuma-dev
cd /usr/src/
wget http://fast.dpdk.org/rel/dpdk-17.11.2.tar.xz
tar xf dpdk-17.11.2.tar.xz
cd $DPDK_DIR
make install T=$DPDK_TARGET DESTDIR=install
mkdir -p /mnt/huge
mount -t hugetlbfs nodev /mnt/huge
echo 4096 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages

apt-get -y install libssl-dev
apt-get -y install libcap-ng-dev
apt-get -y install python-pip
pip install six
apt-get -y install autoconf
apt-get -y install libtool
apt-get -y install python-pyftpdlib
apt-get -y install netcat
apt-get -y install curl
apt-get -y install python-tftpy
apt-get -y install sparse
apt-get -y install clang
apt-get -y install python-flake8
cd /usr/src/
wget http://openvswitch.org/releases/openvswitch-2.9.2.tar.gz
tar -xvf openvswitch-2.9.2.tar.gz
cd openvswitch-2.9.2
./boot.sh
kernelPath="/lib/modules/$(uname -r)/build"
./configure --with-dpdk=$DPDK_BUILD --with-linux=$kernelPath
make
make install
