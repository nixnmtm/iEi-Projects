# Follow below steps for NIC Performance Testing
1. Intel virtualization extensions (VT – for VT-x) and VT-d (for direct IO) and DMA remapping (DMAR) must be turned on in BIOS.
2. [Enable IOMMU](http://40.74.91.221/Nixon/NIC_Performance_testing/wikis/enable-iommu)
3. [Install DPDK](http://40.74.91.221/Nixon/NIC_Performance_testing/blob/master/dpdk_setup.sh)
4. [Install VPP](http://40.74.91.221/Nixon/NIC_Performance_testing/blob/master/vpp_setup.sh)
(This script also installs VPP-Config tool)
5. [Load Module and Bind Interfaces](http://40.74.91.221/Nixon/NIC_Performance_testing/wikis/load-module-and-bind-interfaces) 
6. [Set IP and UP Interfaces ](http://40.74.91.221/Nixon/NIC_Performance_testing/wikis/vpp-set-ip-and-state-up)
7. [SPIRENT Setup](http://40.74.91.221/Nixon/NIC_Performance_testing/blob/master/SPIRENT%20Test%20Center%20Set%20UP.pptx)

# VPP-Config 
1. Easy way to handle vpp commands
2. VPP can be installed or uninstalled using this tool also

# Mellanox DPDK-L3FWD setup and Performance 

Note: :star:
For Mellanox NICs, the testing is done with L3FWD tool in DPDK. VPP is not used.
(Reason is, they use Kernel Space(kernel driver) and hence L3 layer can be accessed directly) 

The complete setup and performance reports can be found in the below links.

[Setup Mellanox_DPDK](http://40.74.91.221/Nixon/NIC_Performance_testing/wikis/mellanox-and-dpdk-setup)

[Mellanox_L3FWD_SPIRENT_Performance_report](http://40.74.91.221/Nixon/NIC_Performance_testing/wikis/mellanox/dpdk-performance-reports)


# AMD NIC DPDK/VPP Performance Report
[AMD 3201(10GbE NIC)](http://40.74.91.221/Nixon/NIC_Performance_testing/wikis/amd-nic-performance) 
[AMD 3151(10GbE NIC)](http://40.74.91.221/Nixon/NIC_Performance_testing/wikis/amd-3151)


# BROADCOM NIC(Broadcom NetXtreme Gigabit Ethernet)

**PCIe id BCM5720/BCM95720 not supported by DPDK and VPP**

1. 1G Ports (BROADCOM NIC NetXtreme BCM5720) can bind with DPDK. But cannot run any of its application.
[Ref 1](http://mails.dpdk.org/archives/dev/2017-March/060767.html)
[Ref 2](http://git.dpdk.org/dpdk-stable/tree/drivers/net/bnxt/bnxt_ethdev.c?h=v16.07.2#n72)

2. Not supported yet by VPP also. Query raised and confirmed for **BCM95720**
[Query Ref](https://lists.fd.io/g/vpp-dev/topic/brodcom_iterfaces_bcm95720/28790956?p=,,,20,0,0,0::recentpostdate%2Fsticky,,,20,2,0,28790956)

