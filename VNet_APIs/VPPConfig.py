import re
import PKGManager
import NICbind
from flask import Flask, jsonify, request, Response
from vpplib import AutoConfig, VppHugePageUtil

rootdir = "/usr/local/"
vpp_yaml = "/vpp/vpp-config/configs/auto-config.yaml"
MAX_PERCENT_FOR_HUGE_PAGES = 70
MIN_TOTAL_HUGE_PAGEs = 1024

VPP_REAL_HUGE_PAGE_FILE = '/etc/sysctl.d/80-vpp.conf'
VPP_HUGEPAGE_CONFIG = """
vm.nr_hugepages={nr_hugepages}
vm.max_map_count={max_map_count}
vm.hugetlb_shm_group=0
kernel.shmmax={shmmax}
"""


app = Flask(__name__)

hp = {}


def get_actual_hugepages():

    """
    Get the current huge page configuration

    :returns the hugepage total, hugepage free, hugepage size,
    total memory, and total memory free
    :rtype: tuple
    """

    # Get the memory information using /proc/meminfo
    cmd = 'sudo cat /proc/meminfo'
    (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
    if ret != 0:
        raise RuntimeError(
            '{} failed on node {} {}'.format(
                cmd, stdout, stderr))

    total = re.findall(r'HugePages_Total:\s+\w+', stdout)
    free = re.findall(r'HugePages_Free:\s+\w+', stdout)
    size = re.findall(r'Hugepagesize:\s+\w+\s+\w+', stdout)
    memtotal = re.findall(r'MemTotal:\s+\w+\s+\w+', stdout)
    memfree = re.findall(r'MemFree:\s+\w+\s+\w+', stdout)

    hp["HugePages Total"] = total[0].split(':')[1].lstrip()
    hp["HugePages Free"] = free[0].split(':')[1].lstrip()
    hp["Hugepagesize"] = size[0].split(':')[1].lstrip()
    hp["MemTotal"] = memtotal[0].split(':')[1].lstrip()
    hp["MemFree"] = memfree[0].split(':')[1].lstrip()

    return hp

def huge_range():
    actual = get_actual_hugepages()

    memfree = actual["MemFree"].split(" ", 1)[0]
    hugefree = actual["HugePages Free"].split(" ", 1)[0]
    hugesize = actual["Hugepagesize"].split(" ", 1)[0]
    maxpages = (int(memfree) * MAX_PERCENT_FOR_HUGE_PAGES / 100) / int(hugesize)
    return (
        "There are currently {} {}kb huge pages free. \n \
        As the huge pages should not be more than 70% of the total free memory \n \
        choose between {} {}, the default is {}").format(
        hugefree,
        hugesize,
        MIN_TOTAL_HUGE_PAGEs,
        maxpages,
        MIN_TOTAL_HUGE_PAGEs
    )

def modify_hugepages(inp):

    """Need to check hugepages limits and shared memmory limits to modify dynamically"""
    """Look modify hugepages in AutoConfig"""
    actual = get_actual_hugepages()
    memfree = actual["MemFree"].split(" ", 1)[0]
    hugesize = actual["Hugepagesize"].split(" ", 1)[0]
    maxpages = (int(memfree) * MAX_PERCENT_FOR_HUGE_PAGES / 100) / int(hugesize)
    if MIN_TOTAL_HUGE_PAGEs <= inp <= maxpages:
        pass
    else:
        RuntimeError("PLease input Hugepages between {} and {}".format(
            MIN_TOTAL_HUGE_PAGEs, maxpages))

    hp["HugePages Total"] = str(inp)
    hp["max_map_count"] = int(hp["HugePages Total"]) * 2 + 1024
    hp["shmmax"] = int(hp["HugePages Total"]) * 2 * 1024 * 1024

    return hp

def apply_hugepages(inp):
    hpgs = modify_hugepages(inp)

    vpp_hugepage_config = VPP_HUGEPAGE_CONFIG.format(
        nr_hugepages = hpgs["HugePages Total"],
        max_map_count = hpgs['max_map_count'],
        shmmax = hpgs['shmmax'])

    if VPP_REAL_HUGE_PAGE_FILE:
        cmd = 'cp {} {}.default'.format(
            VPP_REAL_HUGE_PAGE_FILE, VPP_REAL_HUGE_PAGE_FILE)
        (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
        if ret != 0:
            raise RuntimeError('{} failed {} {}'.
                               format(cmd, stdout, stderr))

    filename = VPP_REAL_HUGE_PAGE_FILE
    cmd = 'echo "{0}" | sudo tee {1}'.\
        format(vpp_hugepage_config, filename)
    (ret, stdout, stderr) = PKGManager.execute_cmd(cmd)
    print (stdout)
    if ret != 0:
        raise RuntimeError('{} failed on node {} {}'.
                            format(cmd, stdout, stderr))
    return hp

@app.route("/puzzle/api/v1/vpp_dpdk/apply_hugepages", methods=['GET','POST'])
def call_info():
    def index():
        input = request.args.get("hugepages")
        return jsonify(apply_hugepages(input))
    return index()

@app.route("/puzzle/api/v1/vpp_dpdk/get_hugepages", methods=['GET','POST'])
def call_gethugpages():
    return jsonify(get_actual_hugepages())

if __name__ == "__main__":
    app.run(debug=True)


