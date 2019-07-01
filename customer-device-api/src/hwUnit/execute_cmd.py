import logging
import subprocess

log = logging.getLogger(__name__)

def execute_cmd(cmd):
    out = ''
    err = ''
    prc = subprocess.Popen(cmd, shell=True, bufsize=1,
		               stdin=subprocess.PIPE,
		               stdout=subprocess.PIPE,
		               stderr=subprocess.PIPE)
    with prc.stdout:
        for line in iter(prc.stdout.readline, b''):
            #logging.info("  {}".format(line.strip('\n')))
            out += line.decode("utf-8","ignore")
            
    with prc.stderr:
        for line in iter(prc.stderr.readline, b''):
            #logging.warning("  {}".format(line.strip('\n')))
            err += line.decode("utf-8","ignore")
        ret = prc.wait()
        return ret, out, err