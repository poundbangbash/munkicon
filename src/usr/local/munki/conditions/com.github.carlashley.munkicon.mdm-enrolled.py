#!/usr/local/munki/munki-python

import subprocess
import sys


try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker


class MDMEnrolledConditions(object):
    def __init__(self):
        self.conditions = self._process()

    def _get_enrollment_state(self):
        """Check the enrollment state of the device."""
        result = dict()

        _cmd = ['/usr/bin/profiles', 'status', '-type', 'enrollment']

        _subprocess = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _result, _error = _subprocess.communicate()

        if _subprocess.returncode == 0:
            if _result:
                _result = _result.decode('utf-8').strip().splitlines()

                for _item in _result:
                    _key = _item.lower().split(': ')[0].replace(' ', '_')
                    _value = _item.lower().split(': ')[1].replace(' ', '_').replace('(', '').replace(')', '')

                    result[_key] = _value
                return result
        else:
            sys.exit(1)

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = {'enrolled_via_dep': '',
                  'mdm_enrollment': ''}

        _result = self._get_enrollment_state()

        if _result:
            result['enrolled_via_dep'] = _result.get('enrolled_via_dep', '')
            result['mdm_enrollment'] = _result.get('mdm_enrollment', '')

        return result


def main():
    mdm = MDMEnrolledConditions()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=mdm.conditions)


if __name__ == '__main__':
    main()
