# INstall VPP

export UBUNTU="xenial"

unset -v RELEASE

export RELEASE=".stable.1807"

sudo rm /etc/apt/sources.list.d/99fd.io.list

echo "deb [trusted=yes] https://nexus.fd.io/content/repositories/fd.io$RELEASE.ubuntu.$UBUNTU.main/ ./" | sudo tee -a /etc/apt/sources.list.d/99fd.io.list

printf 'y' | sudo apt-get update

printf 'y' | sudo apt-get install vpp vpp-lib

printf 'y' | sudo apt-get --fix-missing install vpp-plugins vpp-dbg vpp-dev vpp-dpdk-dkms vpp-dpdk-dev vpp-api-java vpp-api-python vpp-api-lua vpp-nsh-plugin-dev vpp-nsh-plugin-dbg vpp-nsh-plugin

echo "****Installing vpp-config****"

printf 'y' | sudo apt-get install python-pip
sudo pip install vpp-config

