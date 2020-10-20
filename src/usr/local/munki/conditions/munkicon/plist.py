"""Wrappers for plistlib"""
import os
import plistlib
import shutil
import subprocess

from sys import version_info
from xml.parsers.expat import ExpatError

# plistlib.readPlist() and plistlib.writePlist() deprecated in Python 3.4+
DEPRECATED = (version_info.major == 3 and version_info.minor > 4)


def readPlist(path):
    """Read a property list."""
    result = dict()

    if os.path.exists(path):
        # plistlib.readPlist() deprecated in Python 3.4+
        if DEPRECATED:
            with open(path, 'rb') as _f:
                result = plistlib.load(_f)
        else:
            try:
                result = plistlib.readPlist(path)
            except ExpatError:
                _tmp_path = '/tmp/{}'.format(os.path.basename(path))
                shutil.copy(path, _tmp_path)
                _cmd = ['/usr/bin/plutil', '-convert', 'xml1', _tmp_path]

                _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _r, _e = _p.communicate()

                if _p.returncode == 0:
                    result = plistlib.readPlist(_tmp_path)
                    os.remove(_tmp_path)

    return result


def readPlistFromString(obj):
    """Read a property list."""
    result = dict()

    if DEPRECATED:
        result = plistlib.loads(obj)
    else:
        result = plistlib.readPlistFromString(obj)

    return result


def writePlist(path, data):
    """Write a property list to file."""
    if DEPRECATED:
        with open(path, 'wb') as _f:
            plistlib.dump(data, _f)
    else:
        plistlib.writePlist(data, path)
