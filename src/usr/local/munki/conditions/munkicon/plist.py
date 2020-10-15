"""Wrappers for plistlib"""
import os
import plistlib

from sys import version_info

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
            result = plistlib.readPlist(path)

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
