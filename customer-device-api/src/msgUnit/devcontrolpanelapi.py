'''
Created on Aug 28, 2018

@author: Ramesh
'''
#!/usr/bin/python3
import socket
import time, threading
import json
import sys
import os
import logging
import subprocess
import requests
from flask import Flask, request, Response, jsonify
from hwUnit.dev_hwinfo import device
import xml.etree.ElementTree as ET
import urllib.request
class main:
    def __init__(self,app):
        self.project_path = os.path.dirname(os.path.realpath(__file__))
        ### device use
        app.add_url_rule('/puzzle/api/v1/devCPInfo', 'devCPInfo', self.devCPInfo, methods=['GET'])
        app.add_url_rule('/puzzle/api/v1/devPower', 'devPower', self.devPower, methods=['POST'])
        app.add_url_rule('/puzzle/api/v1/fwUpdate', 'fwUpdate', self.fwUpdate, methods=['POST'])
        ### pc use
        app.add_url_rule('/puzzle/api/v1/devNetworkInfo', 'devNetworkInfo', self.devNetworkInfo, methods=['GET'])
        app.add_url_rule('/puzzle/api/v1/devCheck', 'devCheck', self.devCheck, methods=['POST'])

        self.info={}
        self.PASS = 1
        self.FAIL = 2
        a=device()
        self.info["serialno"]=a.getSN()
        self.info["productname"]=a.getProductName()
        self.info["firmwarever"]=self.getFwVersion()
        self.cpu_info()
        #self.callNetworkInfo()

    def getFwVersion(self):
        versionfile= self.project_path + "/updateUse/" + ".utilityversion"
        file = open(versionfile,"r")
        oldVS=file.read()
        file.close()
        return oldVS
    ###### devcontrolpanelapi PART
    def mycmp(self,version1, version2):
        def cmdPre(v):
            myarr=v.split(".")
            myIntArr=[]
            for loop in myarr:
                myIntArr.append(int(loop))
            return myIntArr

        def cmp(a, b):
            cmpResult=(a > b) - (a < b)
            if cmpResult>0:
                # print("update {}".format(cmpResult))
                ret=True
            else:
                ret=False
                # print("laster {}".format(cmpResult))
            return ret
        a=cmdPre(version1.replace("-beta",".1"))
        b=cmdPre(version2.replace("-beta",".1"))
        return cmp(a, b)

    def fwUpdate(self):
        body = request.get_json()
        action=body["action"]
        updateCenterUrl = "http://cloud.ieiworld.com/appcentre/app_utility.xml"
        versionfile= self.project_path + "/updateUse/" + ".utilityversion"
        if action=="check":
            # get new version
            url = updateCenterUrl
            headers = {'Content-Type': "application/json"}
            data = requests.get(url=url, headers=headers)
            # print("data is {}".format(data.text))
            root = ET.fromstring(data.text)

            # print("tree is {}".format(root))
            # print("tree is {}".format(type(root)))
            newVS=None
            puzzleFlag=False
            for child_of_root in root:
                # print("root is tag {}, attrib {}".format(child_of_root.tag,child_of_root.text))
                if "item" in child_of_root.tag:
                    for child_of_child_of_root in child_of_root:
                        # print("child_of_root is tag {}, attrib {}".format(child_of_child_of_root.tag,child_of_child_of_root.text))
                        if "name" in child_of_child_of_root.tag:
                            if "PUZZLE" in child_of_child_of_root.text:
                                puzzleFlag=True
                        if puzzleFlag:
                            if "fwVersion" in child_of_child_of_root.tag:
                                newVS=child_of_child_of_root.text
                                break

                if puzzleFlag:
                    break
            file = open(versionfile,"r")
            oldVS=file.read()
            file.close()
            # print("newVS is {}, oldVS is {}".format(newVS,oldVS))
            if newVS is not None:
                if self.mycmp(newVS,oldVS):
                    msg="{} is laster version, please update".format(newVS)
                    status=0
                else:
                    msg="{} is the laster version, no update availble".format(newVS)
                    status=1
                data={
                    "msg": msg,
                    "status": status
                }
            else:
                msg="fail info from update center"
                data={
                    "msg": msg,
                    "status": 1
                }
        elif action=="update":
           # Do update

           # get new version
           url = updateCenterUrl
           headers = {'Content-Type': "application/json"}
           data = requests.get(url=url, headers=headers)
           # print("data is {}".format(data.text))
           root = ET.fromstring(data.text)

           # print("tree is {}".format(root))
           # print("tree is {}".format(type(root)))
           url=""
           puzzleFlag=False
           locationFlag=False
           location=None
           newVS=None
           platform="x86" # x86 or ARM
           for child_of_root in root:
               # print("root is tag {}, attrib {}".format(child_of_root.tag,child_of_root.text))
               if "item" in child_of_root.tag:
                   for child_of_child_of_root in child_of_root:
                       # print("child_of_root is tag {}, attrib {}".format(child_of_child_of_root.tag,child_of_child_of_root.text))
                       if "name" in child_of_child_of_root.tag:
                           if "PUZZLE" in child_of_child_of_root.text:
                               puzzleFlag=True
                       if puzzleFlag:
                           if "fwVersion" in child_of_child_of_root.tag and newVS is None:
                               newVS=child_of_child_of_root.text
                           if "platform" in child_of_child_of_root.tag:
                                for child_of_child_of_root_of_root in child_of_child_of_root:
                                   if "platformID" in child_of_child_of_root_of_root.tag:
                                       if platform in child_of_child_of_root_of_root.text:
                                           locationFlag=True

                                   if locationFlag:
                                       if "location" in child_of_child_of_root_of_root.tag and location is None:
                                           location=child_of_child_of_root_of_root.text
                                           break

               if puzzleFlag and locationFlag:
                   break

           if newVS is not None and location is not None:
               # print("location {}".format(location))
               # print("newVS {}".format(newVS))
               copyPath = self.project_path + "/updateUse/" + "update.tar.xz"
               urllib.request.urlretrieve(location, copyPath)
               updateflag=True
               status=0

               runPath = self.project_path + "/updateUse/" + "run.sh"
               cmd="sh {}".format(runPath)
               (ret, stdout, stderr) = self.execute_cmd(cmd)
               if len( stderr ) >= 1:
                   print ("Get error:\n" + stderr)
                   updateflag=False
               else:
                   temp=stdout.splitlines()
                   # print("temp {}".format(temp))

               if updateflag:
                   file = open(versionfile,"w")
                   file.write(newVS)
                   file.close()
                   self.info["firmwarever"]=newVS
                   msg="update finish"
               else:
                   msg="update fail"
                   status=1
               data={
                   "msg": msg,
                   "status": status
               }
           else:
               msg="fail info from update center"
               data={
                   "msg": msg,
                   "status": 1
               }
        else:
           msg="fail request"
           data={
               "msg": msg,
               "status": 1
           }

        tmp=jsonify(data)
        return tmp

    def devCPInfo(self):
        self.mem_info()
        return jsonify(self.info)
    '''
    def callNetworkInfo(self):
        print('Timer')
        self.network_info()
        threading.Timer(5, self.callNetworkInfo).start()
    '''
    def devNetworkInfo(self):
        dev=self.network_info()
        ret={
            "network":dev,
            "sn":self.info["serialno"]
        }
        return jsonify(ret)

    def devCheck(self):
        devmsg = "I am Puzzle!"
        num_nics = self.count_nics()
        devinfo = {"sn":str(self.info["serialno"]),"msg":devmsg,"interfaces":int(num_nics),"modelName":self.info["productname"],"firmwarever":self.info["firmwarever"]}
        # rx_ip = request.get_json(silent=True)
        # server_ip = rx_ip['ip']
        # print('Recevied customer server ip is ',server_ip)
        # # Store the customer server ip address
        # self.inputDevAgent(server_ip)
        return jsonify(devinfo)

    def devPower(self):
        rx_power = request.get_json(silent=True)
        pow_resp = "fail"
        if "power" in rx_power:
            pow_state = rx_power['power']
            if pow_state == "reboot" :
                print('Rebooting now ...')
                cmd='sleep 5; shutdown -r now'
                thread = threading.Thread(target=self.execute_cmd, args=(cmd,))
                thread.daemon = True
                thread.start()
                # os.system('sleep 5; shutdown -r now')
                pow_resp = "success"
            elif(pow_state == "off"):
                print('Shutting down ...')
                cmd='sleep 5; shutdown -h now'
                thread = threading.Thread(target=self.execute_cmd, args=(cmd,))
                thread.daemon = True
                thread.start()
                # os.system('sleep 5; shutdown -h now')
                pow_resp = "success"
        pow_result = {"result":pow_resp}
        print('pow_result  {}'.format(pow_result))
        return jsonify(pow_result)

    def updateInfo(self,data):
        self.info.update(data)
    # Function to call device information api
    def devinfoapi(self,data):
        url = 'http://{}:{}/deviceInfo'.format("localhost", 8882)
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data, headers=headers)
        print('Dev Info API Response Code: ', r.status_code)
        retData = {}
        if r.status_code == 200:
            retData["result"] = self.PASS
            retData["data"] = json.loads(r.text)
        else:
            retData["result"] = self.FAIL
        return retData

    # Function to set input to device information api, and to extract the serial number from the JSON response
    def inputDevInfo(self):
        retData = {}
        inputdata = {
            "config": {
                "name": [0]
            },
            "device": {
                "name": [0]
            }
        }
        tmp = json.dumps(inputdata)
        tmpapi = self.devinfoapi(tmp)
        if tmpapi["result"] == self.PASS:
            srv_credentials = {}
            sn = None
            flag = 0
            apidata = tmpapi["data"]
            tmp = apidata["config"]
            for loop in tmp:
                data = loop["data"]
                if loop["name"] == 0:
                    if isinstance(data, dict):
                        flag = flag + 1
                        srv_credentials["host"] = data["ip"]
                        srv_credentials["port"] = data["port"]
            tmp = apidata["device"]
            retData["result"] = self.PASS
            #print("myInput retData {}".format(data))
            retData["sn"] = str(tmp[0]["data"])
        else:
            retData["result"] = self.FAIL
        return retData

    # Function to call device agent api to store the customer server ip
    def devagentapi(self,devagent_input):
        url = 'http://{}:{}/deviceAgent'.format("localhost", 8882)
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, devagent_input, headers=headers)
        print('Dev Agent Response Code: ', r.status_code)
        retData = {}
        if r.status_code == 200:
            retData["result"] = self.PASS
            retData["data"] = json.loads(r.text)
        else:
            retData["result"] = self.FAIL
        return retData

    # Function to set input to device information api, and to extract the serial number from the JSON response
    def inputDevAgent(self,srvip):
        inputdata = {
            "config": [
                {
                    "name": 0,
                    "data": {
                       "ip":srvip,
                       "port":1234
                    }
                }
            ]
        }
        tmp = json.dumps(inputdata)
        tmpapi = self.devagentapi(tmp)
        if tmpapi["result"] == self.PASS:
            print("Stored Server IP Address!")
        return None

    def execute_cmd(self,cmd):
        """Execute the given command on the local node

        :param cmd: Command to run locally.
        :param timeout: Timeout value
        :type cmd: str
        :type timeout: int
        :return return_code, stdout, stderr
        :rtype: tuple(int, str, str)
        """

        out = ''
        err = ''
        prc = subprocess.Popen(cmd, shell=True, bufsize=1,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        with prc.stdout:
            for line in iter(prc.stdout.readline, b''):
                line = line.decode("utf-8")
                logging.info("  {}".format(line.strip('\n')))
                out += line

        with prc.stderr:
            for line in iter(prc.stderr.readline, b''):
                line = line.decode("utf-8")
                logging.warning("  {}".format(line.strip('\n')))
                err += line

        ret = prc.wait()
        return ret, out, err

    def pci_info(self):
        cmd = "echo 8888 | sudo -S lshw -c network -businfo"
        (_, out, err) = self.execute_cmd(cmd)

        interfaces = []
        self.info["network"] = []
        test = out.splitlines()
        desc = []
        for i, line in enumerate(test):
            if len(line) == 0:
                continue
            if line.startswith(" "):
                desc.append(line.split('network', 1)[1].lstrip())
                temp = line.split()
                interfaces.append(temp[temp.index('network')-1])

        for i, intf in enumerate(interfaces):
            device = {}
            # Extract device description
            device["description"] = desc[i]

            # Extract driver of each pci
            cmd = 'ls /sys/bus/pci/devices/{}/driver/module/drivers'. \
                format(id)
            (ret, stdout, stderr) = self.execute_cmd(cmd)
            if ret == 0:
                device['driver'] = stdout.split(':')[1].rstrip('\n')

            # Extract interface name
            device['interface'] = intf

            # Extract MAC address
            cmd = "ifconfig {} | grep -Po '\HWaddr \K.*'".format(intf)
            (ret, stdout, stderr) = self.execute_cmd(cmd)
            if ret != 0:
                raise RuntimeError('{} failed {} {}'.
                                       format(cmd, stderr, stdout))
            device['macaddr'] = stdout.rstrip('\n').split()[0]

            # Extract the IP address of the active NIC
            device['ip'] = " "
            cmd = "ip addr show {} | grep -Po 'inet \K[\d.]+'".format(intf)
            (ret, stdout, stderr) = self.execute_cmd(cmd)
            if len(stdout) > 0:
                device['ip'] = str(stdout.rstrip('\n'))

            # Extract the state of each NIC
            device['status'] = " "
            cmd = "ip addr show {} | grep -Po 'state \K[\w.]+'".format(intf)
            (ret, stdout, stderr) = self.execute_cmd(cmd)
            if len(stdout) > 0:
                device['status'] = str(stdout.rstrip('\n'))

            self.info["network"].append(device)

        return self.info

    def network_info(self):
        devices = []
        # Find the NIC name and type
        cmd = "ls -l /sys/class/net/"
        (_,out,err) = self.execute_cmd(cmd)
        temp = out.splitlines()
        for i, line in enumerate(temp):
            device = {}
            temp1 = []
            flagCheck="/net" in line
            if (len(line) > 0) & flagCheck:
                print('Resp ',line)
                temp1 = line.split('/virtual/net/',1)
                if len(temp1) > 1:
                    device["interface"] = temp1[1]
                    device["type"] = "Virtual"
                else:
                    device["interface"] = line.split('/net/',1)[1]
                    device["type"] = "Physical"
                devices.append(device)
        for i, device in enumerate(devices):
            device["description"] = "Ethernet Interface"
            # Extract the IP address of the active NIC
            device['ip'] = " "
            cmd = "ip addr show {} | grep -Po 'inet \K[\d.]+'".format(device["interface"])
            (ret, stdout, stderr) = self.execute_cmd(cmd)
            if ret == 0:
                device['ip'] = str(stdout.rstrip('\n'))

            # Extract the state of each NIC
            cmd = "ip addr show {} | grep -Po 'state \K[\w.]+'".format(device["interface"])
            (ret, stdout, stderr) = self.execute_cmd(cmd)
            if ret == 0:
                device['status'] = str(stdout.rstrip('\n'))

            # Extract MAC address
            cmd = "ifconfig {} | grep -Po '\HWaddr \K.*'".format(device["interface"])
            (ret, stdout, stderr) = self.execute_cmd(cmd)
            if ret != 0:
                device['macaddr'] = "unknown"
            else:
                device['macaddr'] = stdout.rstrip('\n').split()[0]

        # self.info["network"] = devices
        return devices


    def cpu_info(self):
        cmd = "lscpu | grep '"'Architecture:'"'| awk '{print $2}'"
        self.info["cpu"] = ""
        (_, out, err) = self.execute_cmd(cmd)
        arch = out.splitlines()[0].lstrip()
        #model = out.splitlines()[0].split(":",1)[1].lstrip()
        cmd = "lscpu | grep '"'CPU(s):'"'| awk '{print $2}'"
        (_, out, err) = self.execute_cmd(cmd)
        processors = out.splitlines()[0].lstrip()
        cpuinfo = arch + " CPU(s): " + processors
        self.info["cpu"] = cpuinfo
        return self.info

    def count_nics(self):
        cmd = "lscpu | grep '"'Architecture:'"'| awk '{print $2}'"
        (_, out, err) = self.execute_cmd(cmd)
        arch = out.splitlines()[0].lstrip()
        if arch == "x86_64":
            cmd = "lspci | egrep -i --color 'network|ethernet' | wc -l"
            (_, out, err) = self.execute_cmd(cmd)
        else:
            cmd = "sudo -S lshw -c network -businfo | grep Eth | wc -l"
            (_, out, err) = self.execute_cmd(cmd)
        nics = out.splitlines()[0]
        return nics

    def mem_info(self):
        cmd = "grep '"'Mem'"' /proc/meminfo"
        (_, out, err) = self.execute_cmd(cmd)
        self.info["memory"] = ""
        meminfo = []
        for line in out.splitlines():
            temp = line.split(":", 1)[1].lstrip().split(' ')[0]
            temp = str(format(float(temp)/(1024*1024),
                                                 '.2f')) + " GB"
            meminfo.append(temp)
        self.info["memory"] = meminfo[0] + " ({} free)".format(meminfo[1])
        return self.info
