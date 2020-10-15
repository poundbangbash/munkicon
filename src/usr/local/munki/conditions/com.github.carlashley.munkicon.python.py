#!/usr/local/munki/python
import os
import subprocess

try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker


class PythonConditions(object):
    """Generates information about python versions."""
    def __init__(self):
        self.conditions = self._process()

    def _get_python_path(self, python):
        """Gets the real path (following symlinks) of Python several paths."""
        result = ''

        if os.path.exists(python):
            result = os.path.realpath(python)

        return result

    def _get_python_ver(self, python):
        """Gets the version of several Python paths (if they exist)."""
        result = ''

        if os.path.exists(python):
            _path = os.path.realpath(python)

            _cmd = [_path, '--version']

            _subprocess = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _result, _error = _subprocess.communicate()

            if _subprocess.returncode == 0:
                if _result:
                    if isinstance(_result, bytes):
                        _result = _result.decode('utf-8').strip()

                    result = _result.replace('Python ', '')
                elif _error:
                    if isinstance(_error, bytes):
                        _error = _error.decode('utf-8').strip()

                    if 'Python ' in _error:
                        result = _error.replace('Python ', '')

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        _mac = '/usr/bin/python'
        _munki = '/usr/local/munki/munki-python'
        _official3 = '/usr/local/bin/python3'

        _mac_os_python_path = self._get_python_path(python=_mac)
        _munki_python_path = self._get_python_path(python=_munki)
        _official_python3_path = self._get_python_path(python=_official3)

        _mac_os_python_ver = self._get_python_ver(python=_mac)
        _munki_python_ver = self._get_python_ver(python=_munki)
        _official_python3_ver = self._get_python_ver(python=_official3)

        result['mac_os_python_path'] = _mac_os_python_path
        result['munki_python_path'] = _munki_python_path
        result['official_python3_path'] = _official_python3_path

        result['mac_os_python_ver'] = _mac_os_python_ver
        result['munki_python_ver'] = _munki_python_ver
        result['official_python3_ver'] = _official_python3_ver

        return result


def main():
    py = PythonConditions()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=py.conditions)


if __name__ == '__main__':
    main()
