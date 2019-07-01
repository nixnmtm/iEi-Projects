
#!/usr/bin/env bash
# Prequisites to follow before installation
# sudo su before running

# install basic packages
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt -y install net-tools
sudo apt-get -y install ethtool
sudo apt -y install make

echo "****Setting up for DPDK installation****"
# install packages needed for DPDK
sudo apt -y install gcc
sudo apt-get install libpcap-dev
sudo apt-get install libnuma-dev

# DPDK Installation
echo "****Installing DPDK****"
dpdk_ver=19.02
wget https://fast.dpdk.org/rel/dpdk-${dpdk_ver}.tar.xz
tar xf dpdk-${dpdk_ver}.tar.xz -C ../
cd ../dpdk-${dpdk_ver}
export RTE_SDK=$PWD

make config T=x86_64-native-linuxapp-gcc
sed -ri 's,(PMD_PCAP=).*,\1y,' build/.config
make

# set hugepages

sudo mkdir -p /mnt/huge
sudo mount -t hugetlbfs nodev /mnt/huge
echo 1024 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages

# install L3FWD
echo "***Installing L3FWD Tool***"
cd $RTE_SDK
export RTE_TARGET=build
mkdir my_apps
cp -r ./examples/l3fwd ./my_apps
cd $RTE_SDK/my_apps/l3fwd
make
cd $RTE_SDK