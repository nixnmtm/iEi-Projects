import PKGManager
from flask import Flask, jsonify
import os
#import collections

app = Flask(__name__)

info = {}

def pci_info():
    cmd = "echo 8888 | sudo -S lshw -c network -businfo | grep pci"
    (_, out, err) = PKGManager.execute_cmd(cmd)

    ids = []
    info["pciinfo"] = {}
    test = out.splitlines()
    desc = []
    for i, line in enumerate(test):
        if len(line) == 0:
            continue
        if line.startswith("pci"):
            ids.append(line.split()[0].split("@", 1)[1])
            desc.append(line.split("network", 1)[1].lstrip())

    for i, id in enumerate(ids):

        device = {}
        # Extract device description
        device["description"] = desc[i]

        # Extract driver of each pci
        cmd = 'ls /sys/bus/pci/devices/{}/driver/module/drivers'. \
            format(id)
        (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
        if ret == 0:
            device['driver'] = stdout.split(':')[1].rstrip('\n')

        # Extract interface name
        interfaces = []
        device['interface'] = []
        cmd = 'ls /sys/bus/pci/devices/{}/net'.format(id)
        (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
        if ret == 0:
            interfaces = stdout.rstrip('\n').split()
            device['interface'] = interfaces[0]

        # Extract MAC address
        # l2_addrs = []
        for intf in interfaces:
            cmd = 'cat /sys/bus/pci/devices/{}/net/{}/address'.format(
                id, intf)
            (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
            if ret != 0:
                raise RuntimeError('{} failed {} {}'.
                                   format(cmd, stderr, stdout))

            # l2_addrs.append(stdout.rstrip('\n'))

        device['macaddr'] = stdout.rstrip('\n')
        info["pciinfo"][id] = device

    return info

def cpu_info():
    cmd = "echo 8888 | sudo -S lscpu"
    info["cpuinfo"] = {}
    (_, out, err) = PKGManager.execute_cmd(cmd)
    for line in out.splitlines():
        details = [
                    "Architecture",
                    "Model Name",
                    "CPU(s)",
                    "Thread(s) per core",
                    "Core(s) per socket"
                   ]
        for detail in details:
            k = line.split(":", 1)[0]
            v = line.split(":", 1)[1]
            if k == detail:
                k = k.lower()
                k = k.replace(" ", "")
                if "(s)" in k:
                    k = k.split("(s)")[0] + k.split("(s)")[1]
                info['cpuinfo'][k] = v.lstrip()
    return info
def mem_info():
    cmd = "cat /proc/meminfo"
    (_, out, err) = PKGManager.execute_cmd(cmd)
    info["meminfo"] = {}
    for line in out.splitlines():
        details = [
            "MemTotal",
            "MemFree",
            "MemAvailable",
        ]
        for detail in details:
            k = line.split(":", 1)[0]
            v = line.split(":", 1)[1]
            if k == detail:
                k = k.lower()
                k = k.replace(" ", "")
                info['meminfo'][k] = str(format(float(v.lstrip().split(' ')[0])/(1024*1024),
                                             '.2f')) + " GB"
    return info
def allinfo():
    cpu_info()
    pci_info()
    mem_info()
    #_allinfo = collections.OrderedDict(sorted(info['Mem_Info'].items()))
    #return _allinfo
    return info

@app.route("/puzzle/api/v1/hwinfo", methods=['GET','POST'])
def call_info():
    return jsonify(allinfo())

if __name__ == "__main__":
    app.run(debug=True)
