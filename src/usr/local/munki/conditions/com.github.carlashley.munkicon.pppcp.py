#!/usr/local/munki/python
import os

try:
    from munkicon import plist
    from munkicon import worker
except ImportError:
    from .munkicon import plist
    from .munkicon import worker

# Keys: 'pppcp_payloads'


class PPPCPConditions(object):
    """Generates a simple array of PPPCP payloads deployed via MDM."""
    def __init__(self):
        self.conditions = self._process()

    def _pppcp_overrides(self):
        """Returns PPPCP identifiers from MDM overrides."""
        result = {'pppcp_payloads': list()}

        _mdmoverrides = '/Library/Application Support/com.apple.TCC/MDMOverrides.plist'
        _result = set()

        if os.path.exists(_mdmoverrides):
            _overrides = plist.readPlist(path=_mdmoverrides)

            if _overrides:
                for _override, _payloads in _overrides.items():
                    for _payload, _values in _payloads.items():
                        _identifier = _values.get('Identifier', None)

                        _result.add(_identifier)

        result['pppcp_payloads'] = list(_result)

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._pppcp_overrides())

        return result


def main():
    pppcp = PPPCPConditions()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=pppcp.conditions)


if __name__ == '__main__':
    main()
