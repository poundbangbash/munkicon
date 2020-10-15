#!/usr/local/munki/python
import os
import subprocess
import sys

try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker


class SystemSetupConditions(object):
    """SystemSetup conditions."""
    def __init__(self):
        self.conditions = self._process()

    def _csrutil(self):
        """Executes the `/usr/libexec/mdmclient` binary."""
        result = {'sip_enabled': False}

        _csrutil = '/usr/bin/csrutil'

        if os.geteuid() == 0 and os.path.exists(_csrutil):
            _cmd = [_csrutil, 'status']

            _subprocess = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _result, _error = _subprocess.communicate()

            if _subprocess.returncode == 0:
                if _result:
                    if isinstance(_result, bytes):
                        _result = _result.decode('utf-8')

                    _result = _result.strip()

                    # Iterate over the result to build a dictionary of results
                    result = dict()

                    for _line in _result.splitlines():
                        _line = _line.strip()
                        if 'System Integrity Protection status: ' in _line:
                            _line = _line.strip().split(': ')

                            _val = True if _line[1] == 'enabled.' else False

                            result['sip_enabled'] = _val
        else:
            sys.exit(1)

        return result

    def _cupsctl(self):
        """Executes the `/usr/libexec/mdmclient` binary."""
        result = {'printer_sharing_enabled': False,
                  'cups_web_interface_enabled': False}

        _cupsctl = '/usr/sbin/cupsctl'
        _cups_keys = {'_share_printers': 'printer_sharing_enabled',
                      'WebInterface': 'cups_web_interface_enabled'}

        if os.geteuid() == 0 and os.path.exists(_cupsctl):
            _cmd = [_cupsctl]

            _subprocess = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _result, _error = _subprocess.communicate()

            if _subprocess.returncode == 0:
                if _result:
                    if isinstance(_result, bytes):
                        _result = _result.decode('utf-8')

                    _result = _result.strip()

                    # Iterate over the result to build a dictionary of results
                    result = dict()

                    for _line in _result.splitlines():
                        _line = _line.strip().split('=')

                        _key = _line[0]
                        _val = _line[1]

                        if _key in [_k for _k, _nk in _cups_keys.items()]:
                            if _val == '1' or _val == 'No':
                                _val = True
                            elif _val == '0' or _val == 'Yes':
                                _val = False

                            result[_cups_keys[_key]] = _val
        else:
            sys.exit(1)

        return result

    def _mdmclient(self, verb):
        """Executes the `/usr/libexec/mdmclient` binary."""
        result = None

        _mdmclient = '/usr/libexec/mdmclient'

        if os.geteuid() == 0 and os.path.exists(_mdmclient):
            _cmd = [_mdmclient, verb]

            _subprocess = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _result, _error = _subprocess.communicate()

            if _subprocess.returncode == 0:
                if _result:
                    if isinstance(_result, bytes):
                        _result = _result.decode('utf-8')

                    result = _result.strip()
        else:
            sys.exit(1)

        return result

    def _system_setup(self):
        """Executes the `systemsetup` command and processes output."""
        result = {'timezone': '',
                  'ntp_enabled': False,
                  'ntp_server': '',
                  'wake_on_lan': False,
                  'ssh_enabled': False,
                  'remote_apple_events_enabled': False}

        _verbs = {'gettimezone': 'timezone',
                  'getusingnetworktime': 'ntp_enabled',
                  'getnetworktimeserver': 'ntp_server',
                  'getwakeonnetworkaccess': 'wake_on_lan',
                  'getremotelogin': 'ssh_enabled',
                  'getremoteappleevents': 'remote_apple_events_enabled'}

        if os.geteuid() == 0:
            for _verb, _key in _verbs.items():
                _cmd = ['/usr/sbin/systemsetup', '-{}'.format(_verb)]

                _subprocess = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _result, _error = _subprocess.communicate()

                if _subprocess.returncode == 0:
                    if _result:
                        if isinstance(_result, bytes):
                            _result = ''.join(_result.decode('utf-8').strip().split(': ')[1:])

                            if _result == 'On':
                                _result = True
                            elif _result == 'Off':
                                _result = False

                            result[_key] = _result
        else:
            sys.exit(1)

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = None

        result = self._system_setup()

        _cups = self._cupsctl()
        _sip = self._csrutil()

        if _cups:
            result.update(_cups)

        if _sip:
            result.update(_sip)

        # Note, the output here looks like it could be read by plist/json, but it
        # can't be because it's not a real plist/json output. Iterate over lines.
        _mdmquery_device_security = self._mdmclient('QuerySecurityInfo')

        if _mdmquery_device_security:
            for _line in _mdmquery_device_security.splitlines():
                _line = _line.strip()

                try:
                    _r = _line.split(' = ')[1].replace(';', '')
                except IndexError:
                    _r = None

                if 'RemoteDesktopEnabled = ' in _line:
                    result['ard_enabled'] = True if _r == '1' else False

                if 'PasswordExists = ' in _line:
                    result['efi_password_enabled'] = True if _r == '1' else False
        else:
            result['ard_enabled'] = ''
            result['efi_password_enabled'] = ''

        return result


def main():
    se = SystemSetupConditions()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=se.conditions)


if __name__ == '__main__':
    main()
