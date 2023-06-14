#!/prj/qct/coredev/hexagon/sitelinks/arch/bin/pkw_python3.6.0
"""
utility functions
"""
import argparse
import logging
import os
import subprocess
import time


def run_cmd(cmd, fail_on_error=1):
    """
    wrapper to execute a shell command, and return stdout+stderr(if any) and fail on error
    """
    logging.debug(cmd)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout_bytes, stderr_bytes) = proc.communicate()
    stdout = stdout_bytes.decode("utf-8")
    stderr = stderr_bytes.decode("utf-8")
    rcode = proc.returncode
    cwd = os.getcwd()
    if rcode and fail_on_error:
        msg = "FAIL: " + cmd + "\n rc=" + str(rcode) + "\n cwd=" + cwd + "\n ret=" + stdout + "\n" + stderr
        print(msg)
        raise RuntimeError(msg)
    else:
        logging.debug("\n rc=" + str(rcode) + "\n cwd=" + cwd + "\n ret=" + stdout)
    return rcode, stdout.rstrip() + stderr.rstrip()
