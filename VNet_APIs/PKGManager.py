#!/usr/bin/env python
"""Library to manage the installations"""

from __future__ import print_function
import logging
import subprocess
from flask import Flask, Response, jsonify, Request
import json


VPP_VERSION = ".stable.1804"

#logging.basicConfig(level=logging.INFO)

def execute_cmd(cmd):
    """Execute the given command on the local node

    :param cmd: Command to run locally.
    :param timeout: Timeout value
    :type cmd: str
    :type timeout: int
    :return return_code, stdout, stderr
    :rtype: tuple(int, str, str)
    """

    app.logger.info(" Local Command: {}".format(cmd))
    out = ''
    err = ''
    prc = subprocess.Popen(cmd, shell=True, bufsize=1,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

    with prc.stdout:
        for line in iter(prc.stdout.readline, b''):
            logging.info("  {}".format(line.strip('\n')))
            out += line

    with prc.stderr:
        for line in iter(prc.stderr.readline, b''):
            logging.warning("  {}".format(line.strip('\n')))
            err += line

    ret = prc.wait()
    return ret, out, err
#---------------------------------------------------------------------------

def _install_vpp_pkg(pkg):
    """
    Install the VPP packages

    :param pkg: The vpp packages
    :type pkg: string
    """

    cmd = 'echo 8888 | sudo -S apt-get -y install {}'.format(pkg)
    (ret, stdout, stderr) = execute_cmd(cmd)
    if ret != 0:
        raise RuntimeError('{} failed {} {}'.format(
            cmd, stdout, stderr))
    return stdout
    app.logger.info('Installed {}'.format(pkg))
#---------------------------------------------------------------------------

def install_vpp(fdio_version=VPP_VERSION, ubuntu_version='xenial'):

    # Modify the source list
    sfile = '/etc/apt/sources.list.d/99fd.io.list'

    # Remove the current source file
    #root_pwd = Request.args.get('root_password')
    cmd = 'echo 8888 | sudo -S rm {}'.format(sfile)
    (ret, stdout, stderr) = execute_cmd(cmd)

    if ret != 0:
        logging.debug('{} failed {}'.format(cmd, stderr))

    reps = 'deb [trusted=yes] https://nexus.fd.io/content/'
    reps += 'repositories/fd.io{}.ubuntu.{}.main/ ./\n'.format(
        fdio_version, ubuntu_version)

    cmd = 'echo "{0}" | sudo tee -a {1}'.format(reps, sfile)
    (ret, stdout, stderr) = execute_cmd(cmd)
    if ret != 0:
        raise RuntimeError('{} failed {}'.format(
            cmd,
            stderr))

    # Install the package
    # 'echo '8888' | sudo -S apt-get update'
    cmd = 'echo 8888 | sudo -S apt-get update'
    (ret, stdout, stderr) = execute_cmd(cmd)
    if ret != 0:
        raise RuntimeError('{} apt-get update failed {}'.format(
            cmd,
            stderr))
#---------------------------------------------------------------------------------

def uninstall_vpp(pkg):
    cmd = 'echo 8888 | sudo -S dpkg --purge {}'.format(pkg)
    (ret, stdout, stderr) = execute_cmd(cmd)
    if ret != 0:
        raise RuntimeError('{} failed {} {}'.format(
            cmd, stdout, stderr))
    logging.info('Uninstalled {}'.format(pkg))
    return stdout
#----------------------------------------------------------------------------------

def check_installation(tool='vpp'):
    (ret, stdout, stderr) = execute_cmd('hash {} 2>/dev/null'.format(tool))
    print (ret)
    if ret == 0:
        app.logger.info('{} is already installed'.format(tool))
        (ret,out,err) = execute_cmd('dpkg-query -l {} | grep {}'
                                .format(tool, tool))
        result_line = out.split(' ')

        kv = {'Status': 'Installed',
              'Name': result_line[2],
              'Version': result_line[14],
              'Architechture': result_line[15],
              'Description': result_line[23] + ' ' + result_line[24] + ' ' + result_line[25]}

        return kv
    else:
        app.logger.info('{} is not installed.'.format(tool))
        kv = {'Status': 'Not Installed',
              'Name': tool}
        return kv

#---------------------------------------------------------------------------------

app = Flask(__name__)

@app.route("/puzzle/api/v1/vpp/install", methods=['GET', 'POST'])
def install():
    install_vpp()
    libraries = ['vpp-lib', 'vpp', 'vpp-plugins', 'vpp-dpdk-dkms',
                 'vpp-dpdk-dev', 'vpp-api-python', 'vpp-api-java',
                 'vpp-api-lua', 'vpp-dev']
    for lib in libraries:
        _install_vpp_pkg(lib)
    return jsonify(check_installation())

@app.route("/puzzle/api/v1/vpp/uninstall", methods=['GET','POST'])
def uninstall():
    uninstall_vpp('vpp-api-python')
    uninstall_vpp('vpp-api-java')
    uninstall_vpp('vpp-api-lua')
    uninstall_vpp('vpp-plugins')
    uninstall_vpp('vpp-dpdk-dev')
    uninstall_vpp('vpp-dpdk-dkms')
    uninstall_vpp('vpp-dev')
    uninstall_vpp('vpp')
    uninstall_vpp('vpp-lib')
    return "vpp is uninstalled"
    # for s,v in zip(check_installation()):
    #     if s[v] == 'Not Installed':


@app.route("/puzzle/api/v1/vpp/check", methods=['GET','POST'])
def check():
    return jsonify(check_installation())

if __name__ == "__main__":
    app.run(debug=True)

