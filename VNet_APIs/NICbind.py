import PKGManager, HWInfo
from flask import Flask, Response, request, jsonify
import os, re

DPDK_SCRIPT = "/vpp/vpp-config/scripts/dpdk-devbind.py"
rootdir = "/usr/local"
PCI_DEV_ID_REGEX = '[0-9A-Fa-f]+:[0-9A-Fa-f]+:[0-9A-Fa-f]+.[0-9A-Fa-f]+'
devices = {}


def vpp_start():
    """Start VPP with current settings"""
    cmd = "service vpp start"
    (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
    if ret != 0:
        raise RuntimeError('{} failed {} {}'.format(
            cmd, stdout, stderr))
    return stdout

def vpp_stop():
    """Start VPP with current settings"""
    cmd = "service vpp stop"
    (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
    if ret != 0:
        raise RuntimeError('{} failed {} {}'.format(
            cmd, stdout, stderr))
    return stdout

def vpp_restart():
    """Start VPP with current settings"""
    cmd = "service vpp restart"
    (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
    if ret != 0:
        raise RuntimeError('{} failed {} {}'.format(
            cmd, stdout, stderr))
    return stdout

def device_status():
    """Check status of devices"""

    dpdk_script = rootdir + DPDK_SCRIPT
    cmd = dpdk_script + ' -s '
    (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
    if ret != 0:
        raise RuntimeError('{} failed {} {}'.format(
            cmd, stdout, stderr))
    return stdout


def bind_pci_device(driver, device):
    """
    bind the device specified

    :param driver: The driver
    :param device: The device id or device_name
    :type driver: string
    :type device: string
    """

    dpdk_script = rootdir + DPDK_SCRIPT
    cmd = dpdk_script + ' -b ' + driver + ' ' + device
    (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
    if ret != 0:
        raise RuntimeError('{} failed {} {}'.format(
            cmd, stdout, stderr))

    info = HWInfo.pci_info()
    print (info)

    if stdout is '':
        return "{} bound successfully \n {}".format(device, device_status())
    elif stderr is not '':
        return stderr
    else:
        return stdout
#--------------------------------

def unbind_pci_device(device):
    """
    unbind the device specified

    :param device: The device id or device_name
    :type device: string
    """

    dpdk_script = rootdir + DPDK_SCRIPT
    cmd = dpdk_script + ' -u ' + ' ' + device
    (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
    if ret != 0:
        raise RuntimeError('{} failed {} {}'.format(
            cmd, stdout, stderr))
    if stdout is '' or "is not currently managed by any driver" in stdout:
        # print stdout
        # if "X710" in stdout:
        #     print "X710"
        #     bind_pci_device("uio_pci_generic", device)
        # else:
        #     print "I211"
        bind_pci_device('igb', device)
        return "{} unbound successfully \n {}".format(device, device_status())
    elif stderr is not '':
        return stderr
    else:
        return stdout
#----------------------------------------------------------
# Client side

app = Flask(__name__)
@app.route("/puzzle/api/v1/vpp_dpdk/bind", methods=['GET','POST'])
def call_bind():
    def index():
        driver = request.args.get("driver")
        device = request.args.get("device")
        if re.search(PCI_DEV_ID_REGEX, device):
            return bind_pci_device(driver, device)
        else:
            return bind_pci_device(driver, device)
    return Response(index(), mimetype='txt/html')

@app.route("/puzzle/api/v1/vpp_dpdk/unbind", methods=['GET','POST'])
def call_unbind():
    def index():
        device = request.args.get("device")
        if re.search(PCI_DEV_ID_REGEX, device):
            return unbind_pci_device(device)
        else:
            return unbind_pci_device(device)
    return Response(index(), mimetype='txt/html')

@app.route("/puzzle/api/v1/vpp_dpdk/status", methods=['GET','POST'])
def call_status():
    def index():
        return device_status()
    return Response(index(), mimetype='txt/json')

@app.route("/puzzle/api/v1/vpp_dpdk/stop", methods=['GET','POST'])
def call_stop():
    def index():
        return vpp_stop()
    return Response(index(), mimetype='txt/json')

@app.route("/puzzle/api/v1/vpp_dpdk/restart", methods=['GET','POST'])
def call_restart():
    def index():
        return vpp_restart()
    return Response(index(), mimetype='txt/json')

if __name__ == "__main__":
    app.run(debug=True)


# If needed device details alone, the below function acn be used

# def get_device_details(device_id):
#     device = {}
#     cmd = "lspci -vmmks {}".format(device_id)
#     (ret, stdout,stderr) = PKGManager.execute_cmd(cmd)
#
#     dev_info = stdout.splitlines()
#
#     # parse lspci details
#     for line in dev_info:
#         if len(line) == 0:
#             continue
#         name, value = line.decode().split("\t", 1)
#         name = name.strip(":")
#         device[name] = value
#
#     # check for a unix interface name and add it
#     device["Interface"] = ""
#     for base, dirs, _ in os.walk("/sys/bus/pci/devices/%s/" % device_id):
#         if "net" in dirs:
#             device["Interface"] = \
#                 ",".join(os.listdir(os.path.join(base, "net")))
#             break
#     return device


# @app.route("/puzzle/api/v1/vpp_dpdk/details", methods=['GET','POST'])
# def call_dev_details():
#     device = request.args.get("device")
#     return jsonify(get_device_details(device))


