import random
import string
import subprocess
import itertools
import types
import prettytable
import re


def getstatusoutput(cmd):
    """
    Return (status, output) of executing cmd in a shell.
    This new implementation should work on all platforms.
    """
    pipe = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = str.join("", pipe.stdout.readlines())
    sts = pipe.wait()
    if sts is None:
        sts = 0
    return sts, output
