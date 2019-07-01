from flask import  request, jsonify
from datetime import datetime
import threading
import subprocess

import copy
import pytz
from config.normal import resultDefine
resultDef=resultDefine()

class main:
    def __init__(self,app):
        app.add_url_rule('/gettimezone', 'gettimezone', self.gettimezone, methods=['GET'])
        app.add_url_rule('/gettime', 'gettime', self.gettime, methods=['GET'])
        app.add_url_rule('/settime', 'settime', self.settime, methods=['POST'])

        self.currentTime=datetime.now()
        self.timezoneall=pytz.common_timezones
        self.timer=None
        self.timeupdateflag=True
        self.timeupdate()


    def timeupdate(self):
        self.currentTime=datetime.now()
        if self.timeupdateflag:
            self.timer=threading.Timer(1.0, self.timeupdate)
            self.timer.start()
        # print("self.currentTime {}".format(self.currentTime))

    def gettimezone(self):
        res = {};
        result=resultDef.PASS
        cmd = "cat /etc/timezone"
        (ret, out, err) = self.execute_cmd(cmd)
        if ret < 0:
            result=resultDef.FAIL
            msg="TimeZone error: {}".format(err)
        else:
            res["current"] = out; #'Asia/Taipei';

        # print("res {}".format(res))
        res["result"] = result;#1:PASS, 2:FAIL
        res["data"] = self.timezoneall
        return jsonify(res)

    def settime(self):
        res = {};
        body = request.get_json();
        result=resultDef.PASS
        msg=""

        cmd = "sudo timedatectl set-ntp 0" #sudo timedatectl set-local-rtc 1
        (ret, out, err) = self.execute_cmd(cmd)
        if ret < 0:
            result=resultDef.FAIL
            msg="TimeZone error: {}".format(err)
        else:
            self.timeupdateflag=False
            if self.timer is not None:
                self.timer.cancel()
            if "timezone" in body:
                timezone = body["timezone"];
                timecheck=None
                cmd = "cat /etc/timezone"
                (ret, out, err) = self.execute_cmd(cmd)
                if ret >= 0:
                    if out in self.timezoneall:
                        timecheck = out; #'Asia/Taipei';

                if timecheck is None:
                    cmd = "sudo timedatectl set-timezone {}".format(timezone)
                    print("time cmd {}".format(cmd))
                    (ret, out, err) = self.execute_cmd(cmd)
                    if ret < 0:
                        result=resultDef.FAIL
                        msg="TimeZone error: {}".format(err)
                else:
                    print("time timecheck is same , {}".format(timecheck))

            if "time" in body:
                mTime = body["time"].replace("/","-");
                cmd = "sudo timedatectl set-time '{}'".format(mTime) #"2016/11/11 10:21:32"
                # print("time cmd {}".format(cmd))
                (ret, out, err) = self.execute_cmd(cmd)
                if ret < 0:
                    result=resultDef.FAIL
                    if len(msg) > 0:
                        msg+=", Time error: {}".format(err)
                    else:
                        msg="Time error: {}".format(err)
                else:
                    # print("datetime out {}".format(out))
                    # print("datetime {}".format(datetime.now()))
                    self.currentTime=datetime.now()

            cmd = "sleep 3; sudo systemctl restart collectd.service " #sudo timedatectl set-local-rtc 1
            self.execute_cmd(cmd)

            self.timeupdateflag=True
            self.timeupdate()

        if len(msg) == 0:
            msg= "Update successfully"

        res["result"] = result
        res["msg"] = msg
        return jsonify(res)

    def gettime(self):
        ret={"time":self.currentTime}
        return jsonify(ret)

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
                # logging.info("  {}".format(line.strip('\n')))
                out += line

        with prc.stderr:
            for line in iter(prc.stderr.readline, b''):
                line = line.decode("utf-8")
                # logging.error("  {}".format(line.strip('\n')))
                err += line

        ret = prc.wait()
        return ret, out, err
