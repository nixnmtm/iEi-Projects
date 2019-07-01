import socket
from multiprocessing.pool import ThreadPool
import timeit
import logging
from flask import Flask, jsonify, request
import json
import requests
import time
import uuid

class MustangTools(object):
    def __init__(self, app, local=False):
        self.app = app
        self.app.add_url_rule('/mustangTools/discover', 'discover', self.discover, methods=['GET', 'POST'])
        self.app.add_url_rule('/mustangTools/mustangBurn', 'mustangBurn', self.mustangBurn, methods=['POST'])
        self.app.add_url_rule('/mustangTools/mustangTest', 'mustangTest', self.mustangTest, methods=['GET'])
        self.app.add_url_rule('/mustangTools/mustangDigits', 'mustangDigits', self.mustangDigits, methods=['GET'])

        self.ip_addr = dict()
        self.ip_addr["ip"] = []
        if local:
            self.hostip = "10.10.70.150"
        else:
            self.hostip = self.get_own_ip()

    def get_own_ip(self):
        """
        Get the own IP, even without internet connection.
        """
        return ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [
            [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
             [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])

    def get_allIP(self, subnet):
        """
        Populate ips in a range
        """
        result = []
        for i in range(1, 256):
            ip = subnet + '.' + str(i)
            result.append(ip)
        return result

    def check_connection(self, address, timeout=0.2, port=8882):
        """
        1. Check for accessible ips in the port.
        2. Call devAPI API to fetch serial number if puzzle device.
        3. Send ip and serial number to Server API

        :param address: str
        :param timeout: int (Optional)
        """
        # Create a TCP socket
        s = socket.socket()
        s.settimeout(timeout)
        try:
            s.connect((address, port))
            if not address == self.get_own_ip():
                logging.info("Connection ON --> {}:{}".format(address, port))
                # Device API POST IP & GET serial numb
                devsend = dict()
                devsend["ip"] = address
                headers = {'Content-Type': "application/json"}
                devapiurl = "http://{}:8882/deviceAck".format(address)
                r1 = requests.get(url=devapiurl, headers=headers, data=json.dumps(devsend))
                resp = r1.json()
                if resp["msg"] == "Mustang-V100":
                    self.ip_addr["ip"].append(address)
            else:
                pass
        except socket.error as e:
            #logging.warning("Not Reachable {}:{}".format(address, port))
            pass

    def generatorSN(self, string_length=7, prefix="MX"):
        """Returns a random string of length string_length."""
        random = str(uuid.uuid4())  # Convert UUID format to a Python string.
        random = random.upper()  # Make all characters uppercase.
        random = random.replace("-", "")  # Remove the UUID '-'.
        randSN = prefix + random[0:string_length]
        return randSN  # Return the random string.

    def get_burnstatus(self, devid):
        querystring = {"serialNo": devid}
        headers = {'Content-Type': "application/json"}
        url = "http://" + self.hostip + ":3000/puzzle/api/v1/deviceStatus/getBurningStatus"
        r = requests.get(url=url, headers=headers, params=querystring)
        resp = r.json()
        return resp["info"]["burnInStatus"]

    def get_teststatus(self, devid):
        querystring = {"serialNo": devid}
        headers = {'Content-Type': "application/json"}
        url = "http://" + self.hostip + ":3000/puzzle/api/v1/deviceStatus/getTestStatus"
        r = requests.get(url=url, headers=headers, params=querystring)
        resp = r.json()
        return resp["info"]["testStatus"]

    def notify(self, data):
        try:
            headers = {'Content-Type': "application/json"}
            notifyurl = "http://" + self.hostip + ":3000/puzzle/api/v1/notifications/mxdevicescan"
            r = requests.post(notifyurl, headers=headers, data=json.dumps(data))
            logging.info("Notification status {}".format(r.status_code))
        except Exception as e:
            logging.error("Notification API,{} {}".format(type(e).__name__, str(e)))

    def checkNsetSN(self, devSN, cardSNs, dev_details, address):
        headers = {'Content-Type': "application/json"}
        setsn_url = "http://" + self.hostip + ":3000/puzzle/api/v1/common/setsysserialno"
        try:
            if not devSN:
                cardSNs = dev_details["info"]["snArray"]
                devSN = self.generatorSN()
                setquery = {"ip": address, "serialNo": devSN}
            else:
                setquery = {"ip": address, "serialNo": devSN}
            setSN = requests.post(url=setsn_url, headers=headers, data=json.dumps(setquery))
            logging.info("Setting SN for {}: status code {}".format(address, setSN.status_code))
            time.sleep(1)
        except Exception as ex:
            logging.error("Setting Serial Number API,{} {}".format(type(ex).__name__, str(ex)))
        resp_need = {"ip": address, "sn": devSN, "snArray": cardSNs}
        return resp_need

    def scanmustang(self, address, mode=None):
        headers = {'Content-Type': "application/json"}
        checksn_url = "http://" + self.hostip + ":3000/puzzle/api/v1/common/checksysserialno"
        checkquery = {"ip": address}
        checkSN = requests.post(url=checksn_url, headers=headers, data=json.dumps(checkquery))
        dev_details = checkSN.json()
        cardSNs = dev_details["info"]["snArray"]
        devSN = dev_details["info"]["sn"]
        digits = dev_details['info']['digitsArr']
        if mode == "burn":
            print("BurnIn Stage")
            if not any(self.get_burnstatus(card) == True for card in cardSNs if card):  # if burnIn Status is false, then proceed
                resp = self.checkNsetSN(devSN, cardSNs, dev_details, address)
                self.notify(resp)
                return resp
            else:
                logging.info("Atleast 1 MX card of {} is now in BurnIn stage. Skipping".format(devSN))
                return None
        if mode == "test":
            print("TEST Stage")
            if not any(self.get_teststatus(card) == True for card in cardSNs if card): # if all test status is false, then proceed
                return self.checkNsetSN(devSN, cardSNs, dev_details, address)
            else:
                logging.info("Atleast 1 MX card of {} is now in Test stage. Skipping".format(devSN))
                return None
        if mode is None:
            ret = dict()
            ret["ip"] = address
            ret["digits"] = digits
            return ret


#######################################################################################################################
    ''' Below are APIs '''

    def discover(self):
        "extract subnet from given ip"
        if request.method == "POST":
            if "serverIP" in request.json:
                server_ip = request.json["serverIP"]
                if not server_ip:
                    logging.warning("No IP given, using local subnet")
                    server_ip = self.get_own_ip()
            else:
                logging.warning("No IP given, using local subnet")
                server_ip = self.get_own_ip()
        elif request.method == 'GET':
            server_ip = self.get_own_ip()
        else:
            logging.error("Unknown Method API Call")
        logging.info("Server ip: {}".format(server_ip))
        subnet = ".".join(server_ip.split(".")[0:-1])
        start_time = timeit.default_timer()
        p = ThreadPool(200)
        try:
            result = p.map_async(self.check_connection, self.get_allIP(subnet))
            result.wait(timeout=2)
            p.terminate()
        except:
            pass
        elapsed = timeit.default_timer() - start_time
        logging.info("Time elapsed: {} secs".format(round(elapsed, 2)))
        ip_list = self.ip_addr["ip"] # store list in another variable
        self.ip_addr["ip"] = []   # Clear the list for next call
        # if len(ip_list) > 1:
        #     logging.warning(" More than one IP address received")
        return jsonify({"ip": ip_list})

    def mustangBurn(self):
        try:
            accumulate_data = list()
            headers = {'Content-Type': "application/json"}
            scannedIps = requests.get("http://" + self.hostip + ":3332/mustangTools/discover", headers=headers)
            print(scannedIps.json())
            for adr in scannedIps.json()["ip"]:
                accumulate_data.append(self.scanmustang(adr, mode="burn"))
            accumulate_data = [x for x in accumulate_data if x is not None]
            if accumulate_data:  # if accumulate_data is not empty, proceed
                sn_array = [d['sn'] for d in accumulate_data if 'sn' in d]
                cardarray = [d['snArray'] for d in accumulate_data
                             if 'snArray' in d if d["snArray"]]  # only if snArray has values
                resp = {"snArray": sn_array, "infoSN": cardarray[0][0]}
                print("mustangBurn response:", resp)
                return jsonify(resp)
            else:
                logging.warning("No data accumulated from scanmustang. Hint: May be all in burnIn stage")
                return jsonify({"snArray": "", "infoSN": ""})
        except Exception as e:
            logging.error("mustangBurn: {} {}".format(type(e).__name__, str(e)))
            return jsonify({"snArray": "", "infoSN": ""})

    def mustangTest(self):
        try:
            accumulate_data = list()
            headers = {'Content-Type': "application/json"}
            scannedIps = requests.get("http://" + self.hostip + ":3332/mustangTools/discover", headers=headers)
            print(scannedIps.json())
            for adr in scannedIps.json()["ip"]:
                accumulate_data.append(self.scanmustang(adr, mode="test"))
            accumulate_data = [x for x in accumulate_data if x is not None]
            if accumulate_data:  # if accumulate_data is not empty, proceed
                print("mustangTest response:", accumulate_data)
                resp = {"info": accumulate_data}
                return jsonify(resp)
            else:
                logging.warning("No data accumulated from scanmustang. Hint: May be all in Test stage")
                return jsonify({"info": "No data accumulated from scanmustang. Hint: May be all in Test stage"})
        except Exception as e:
            logging.error("mustangTest: {} {}".format(type(e).__name__, str(e)))
            return jsonify({"info": "mustangTest: {} {}".format(type(e).__name__, str(e))})

    def mustangDigits(self):
        try:
            accumulate_data = list()
            headers = {'Content-Type': "application/json"}
            scannedIps = requests.get("http://" + self.hostip + ":3332/mustangTools/discover", headers=headers)
            print(scannedIps.json())
            for adr in scannedIps.json()["ip"]:
                accumulate_data.append(self.scanmustang(adr))
            return jsonify({"info": accumulate_data})
        except Exception as e:
            return jsonify({"info": "mustangDigits: {} {}".format(type(e).__name__, str(e))})

if __name__ == '__main__':
    app = Flask(__name__)
    MustangTools(app)  # if running other than server and need to call APIs in '10.10.70.150' add local=true argument
    logging.basicConfig(level=logging.INFO)
    app.run('0.0.0.0', port=3332)