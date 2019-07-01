# uninstall vpp

printf 'y' | sudo dpkg --purge vpp-nsh-plugin-dev vpp-nsh-plugin-dbg vpp-nsh-plugin vpp-api-python vpp-api-java vpp-api-lua vpp-plugins vpp-dpdk-dev vpp-dpdk-dkms vpp-dev vpp-dbg vpp vpp-lib
printf 'y' | sudo pip uninstall vpp_config
