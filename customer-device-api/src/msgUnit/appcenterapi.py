import subprocess
import os
import more_itertools as mit
from flask import Flask, request, Response, jsonify
import json, logging, socket
import platform

class manageApps(object):

    """
    **** Manage Installation of apps ****

    :param host: host address
    :type host: str
    :param port: port number
    :type port: int

     # Flask input
    :param {"app_name": "<App name to install>"}
    :type :json

    """

    def __init__(self, app):

        self.app = app
        self.app.add_url_rule('/appcentre/install', 'install', self.install, methods=['POST'])
        self.app.add_url_rule('/appcentre/uninstall', 'uninstall', self.uninstall, methods=['POST'])
        self.app.add_url_rule('/appcentre/apps_status', 'apps_status', self.apps_status, methods=['GET'])
        self.app.add_url_rule('/appcentre/app_limit', 'app_limit', self.app_limit, methods=['POST'])

        # Check installed apps book is present already
        filename = "app_install_status_book.txt"
        self.project_path = os.path.dirname(os.path.realpath(__file__))
        print(self.project_path)
        book_path = self.project_path + "/" + filename

        print("Book Path:\n{}".format(book_path))
        if os.path.exists(book_path):
            with open(filename) as json_file:
                self.app_details = json.load(json_file)
        else:
            self.app_details = dict()
            self.app_details["apps"] = []
            if self.platform() == "intel":
                self.all_apps = ["OVS", "qemu_kvm", "VPP"] #[ "docker", "kubernetes"]
            if self.platform() == "arm":
                self.all_apps = ["OVS", "qemu_kvm"] #["docker", "kubernetes"]
            # try:
            for app in self.all_apps:
                initial_book = dict()
                initial_book["app_name"] = app
                initial_book["app_url"] = "{}{}".format("/puzzle/api/images/",app)                
                if self.get_version(app) == 0:
                    initial_book["status"] = "Not Installed"
                if self.get_version(app) != 0 and self.get_version(app) != 2:
                    if app == "kubernetes":
                        device_ip = self.get_own_ip()
                        url = "http://{}:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/".format(
                            device_ip)
                        initial_book["url"] = url
                    initial_book["status"] = "Installed"
                    initial_book["version"] = self.get_version(app)
                self.app_details["apps"].append(initial_book)
            # except Exception as e:
            #     pass
        print("App_Book_Status:\n{}".format(self.app_details))

    def get_own_ip(self):
        """
        Get the own IP, even without internet connection.
        """
        return ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [
            [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
             [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])

    def internet_on(self, host="8.8.8.8", port=53, timeout=3):

        """
           Host: 8.8.8.8 (google-public-dns-a.google.com)
           OpenPort: 53/tcp
           Service: domain (DNS/TCP)
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception as ex:
            print(ex)
            return False

    def execute_cmd(self, cmd):
        """Execute the given command on the local node

        :param cmd: Command to run locally.
        :type cmd: str
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
                logging.error("  {}".format(line.strip('\n')))
                err += line

        ret = prc.wait()
        return ret, out, err

    def platform(self):
        pf = platform.machine()
        if pf == "x86_64":
            return "intel"
        elif pf == "aarch64":
            return "arm"

    def get_version(self, app_name):
        if app_name == "OVS":
            try:
                get_version_cmd = "sudo ovs-vsctl --version"
                (_, ver, _) = self.execute_cmd(get_version_cmd)
                app_version = ver.split(" ")[3].split("\n")[0]
                return app_version
            except Exception as e:
                return 0  # not installed
        if app_name == "VPP":
            try:
                get_version_cmd = "sudo vppctl sh version | awk  '{print $2}'"
                (_, ver, _) = self.execute_cmd(get_version_cmd)
                if ver:
                    app_version = ver.strip()
                    return app_version
                else:
                    return 0
            except Exception as e:
                return 0  # not installed

        if app_name == "docker":
            try:
                get_version_cmd = "sudo docker version --format '{{.Server.Version}}'"
                (_, ver, _) = self.execute_cmd(get_version_cmd)
                if ver:
                    app_version = ver.strip()
                    return app_version
                else:
                    return 0
            except Exception as e:
                return 0  # not installed
        if app_name == "kubernetes":
            try:
                get_version_cmd = "kubectl version -o=json"
                (_, ver, _) = self.execute_cmd(get_version_cmd)
                ver = json.loads(ver)
                app_version = ver["clientVersion"]["gitVersion"]
                return app_version
            except Exception as e:
                return 0  # not installed
        if app_name == "qemu_kvm":
            try:
                if self.platform() == "intel":
                    get_version_cmd = "qemu-system-x86_64 --version"
                if self.platform() == "arm":
                    get_version_cmd = "qemu-system-aarch64 --version"
                (_, ver, _) = self.execute_cmd(get_version_cmd)
                if ver:
                    app_version = ver.split("\n")[0].split("(")[0].split(" ")[-1]
                    return app_version
                else:
                    return 0
            except Exception as e:
                return 0  # not installed
        if app_name not in self.all_apps:
            print(self.all_apps)
            return 2 # unknown app_name


    def inst_core(self, script_path, app_name):
        print("Installing:", app_name)
        return_inst = dict()
        if self.internet_on():
            if app_name == "kubernetes":
                device_ip = self.get_own_ip()
                print(device_ip)
                (ret, out, err) = self.execute_cmd("sudo bash {} {} 10.0.0.0 {}".format(script_path, self.project_path, device_ip))
                url = "http://{}:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/".format(
                    device_ip)
                index = list(mit.locate(self.app_details["apps"], pred=lambda d: d["app_name"] == app_name))
                self.app_details["apps"][index[0]]["url"] = url
                return_inst["url"] = url
            else:
                (ret, out, err) = self.execute_cmd("sudo bash {}".format(script_path))
            if ret == 0:
                index = list(mit.locate(self.app_details["apps"], pred=lambda d: d["app_name"] == app_name))
                self.app_details["apps"][index[0]]["app_name"] = app_name
                self.app_details["apps"][index[0]]["status"] = "Installed"
                self.app_details["apps"][index[0]]["version"] = self.get_version(app_name)

                # write the updated apps book
                with open('app_install_status_book.txt', 'w') as outfile:
                    json.dump(self.app_details, outfile)
                return_inst["status"] = 1
                return_inst["msg"] = "{} is successfully installed".format(app_name)
                print(jsonify(return_inst))
                return jsonify(return_inst)
            else:
                return_inst["status"] = 0
                return_inst["msg"] = err
                return jsonify(return_inst)
        else:
            return_inst["status"] = 0
            return_inst["msg"] = "Internet Connection Unavailable"
            return jsonify(return_inst)

    def install(self):
        message = request.get_json()
        app_name = message["app_name"]
        return_inst = dict()
        if self.platform() == "intel":
            script_name = app_name + "_install.sh"
        elif self.platform() == "arm":
            script_name = app_name + "_install_arm.sh"
        else:
            return jsonify({"msg": "Unknown Platform"})
        script_path = self.project_path + "/scripts/" +  script_name.lower()
        if os.path.exists(script_path):
            try:
                index = list(mit.locate(self.app_details["apps"], pred=lambda d: d["app_name"] == app_name))
                if self.get_version(app_name) == 2:
                    print(self.get_version(app_name))
                    logging.warning("Unknown app: {}".format(app_name))
                    return "Unknown app: {}".format(app_name)
                elif self.get_version(app_name) != 0 and self.get_version(app_name) != 2:
                    logging.info("{} is already installed.".format(app_name))
                    return_inst["status"] = 1
                    return_inst["msg"] = "{} is already installed.".format(app_name)
                    self.app_details["apps"][index[0]]["app_name"] = app_name
                    self.app_details["apps"][index[0]]["status"] = "Installed"
                    self.app_details["apps"][index[0]]["version"] = self.get_version(app_name)
                    return jsonify(return_inst)
                else:
                    if app_name == "kubernetes":
                        (_, check, _) = self.execute_cmd("systemctl is-active docker")
                        if check.strip() == "active":
                            pass
                        elif check.strip() == "inactive":
                            print("Prerequisite: Docker is installing")
                            docker_path = self.project_path + "/scripts/" + "docker_install.sh"
                            self.inst_core(docker_path, "docker")
                            print("Installed Docker")
                    return self.inst_core(script_path, app_name)
            except Exception as e:
                logging.error("Error in installation", str(e))
                return_inst["status"] = 0
                return_inst["msg"] = "{}: {}".format(type(e).__name__, str(e))
                return jsonify(return_inst)
        else:
            return_inst["status"] = 0
            return_inst["msg"] = "Script file not available"
            return jsonify(return_inst)

    def uninst_core(self, script_path, app_name):
        print("Uninstalling :", app_name)
        return_uninst = dict()
        if app_name == "kubernetes":
            device_ip = self.get_own_ip()
            (ret, out, err) = self.execute_cmd("sudo bash {} {}".format(script_path, device_ip))
            index = list(mit.locate(self.app_details["apps"], pred=lambda d: d["app_name"] == app_name))
            if self.app_details["apps"][index[0]].get("url") is not None:
                del self.app_details["apps"][index[0]]["url"]
                print("url is removed from book")
        else:
            (ret, out, err) = self.execute_cmd("sudo bash {}".format(script_path))

        if ret == 0:
            index = list(mit.locate(self.app_details["apps"], pred=lambda d: d["app_name"] == app_name))
            # update the book
            self.app_details["apps"][index[0]]["status"] = "Not Installed"
            logging.info("{} is successfully uninstalled".format(app_name))
            # write the updated apps book
            with open('app_install_status_book.txt', 'w') as outfile:
                json.dump(self.app_details, outfile)
            return_uninst["status"] = 1
            return_uninst["msg"] = "{} is successfully uninstalled".format(app_name)
            return jsonify(return_uninst)
        else:
            return_uninst["status"] = 0
            return_uninst["msg"] = err
            return jsonify(return_uninst)

    def uninstall(self):

        """ Uninstall given app and update in book"""

        # get app_name
        message = request.get_json()
        app_name = message["app_name"]

        # Extract platform and define path
        if self.platform() == "intel":
            script_name = app_name + "_uninstall.sh"
        elif self.platform() == "arm":
            script_name = app_name + "_uninstall_arm.sh"
        else:
            return jsonify({"msg": "Unknown Platform"})
        script_path = self.project_path + "/scripts/" + script_name.lower()
        return_uninst = dict()
        if os.path.exists(script_path):
            try:
                if self.get_version(app_name) == 2:
                    print(self.get_version(app_name))
                    logging.warning("Unknown app: {}".format(app_name))
                    return "Unknown app: {}".format(app_name)
                elif self.get_version(app_name) == 0:
                    return_uninst["status"] = 1
                    return_uninst["msg"] = "{} module not found. Cannot uninstall".format(app_name)
                    return jsonify(return_uninst)
                else:
                    if app_name == "docker":
                        self.uninst_core(script_path, app_name)
                        if self.get_version("kubernetes") != 0 and self.get_version("kubernetes") != 2:
                            print("Uninstalling Kubernetes as it is inoperative after Docker uninstalled")
                            kube_path = self.project_path + "/scripts/" + "kubernetes_uninstall.sh"
                            self.uninst_core(kube_path, "kubernetes")
                    return self.uninst_core(script_path, app_name)
            except Exception as e:
                return_uninst["status"] = 0
                return_uninst["msg"] = "{}: {}".format(type(e).__name__, str(e))
                return jsonify(return_uninst)
        else:
            return_uninst["status"] = 0
            return_uninst["msg"] = "Script file not available"
            return jsonify(return_uninst)

    def apps_status(self):
        """List the installed apps"""
        return jsonify(self.app_details)

    def app_limit(self):
        """Check whether app has dependency during installation and uninstallation"""
        message = request.get_json()
        app_name = message["app_name"]
        action = message["action"]
        resp = dict()
        if action == "install":
            if app_name == "kubernetes":
                (_, check, _) = self.execute_cmd("systemctl is-active docker")
                if check.strip() == "active":
                    resp["app_name"] = app_name
                    resp["dependency"] = False
                    resp["msg"] = ""
                else:
                    resp["app_name"] = app_name
                    resp["dependency"] = True
                    resp["msg"] = "Kubernetes is dependent on Docker. Do you wish to proceed installing docker?"
            else:
                resp["app_name"] = app_name
                resp["dependency"] = False
                resp["msg"] = ""
        if action == "uninstall":
            if app_name == "docker":
                resp["app_name"] = app_name
                if self.get_version("kubernetes") != 0 and self.get_version("kubernetes") != 2:
                    resp["dependency"] = True
                    resp["msg"] = "Uninstalling docker makes Kubernetes inoperative. Do you wish to proceed?"
                else:
                    resp["dependency"] = False
                    resp["msg"] = ""
            else:
                resp["app_name"] = app_name
                resp["dependency"] = False
                resp["msg"] = ""
        return jsonify(resp)
