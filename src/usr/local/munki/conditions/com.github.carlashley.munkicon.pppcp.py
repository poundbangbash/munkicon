#!/usr/local/munki/python
import os

try:
    from munkicon import plist
    from munkicon import worker
except ImportError:
    from .munkicon import plist
    from .munkicon import worker


class PPPCPConditions(object):
    """Generates a simple array of PPPCP payloads deployed via MDM."""
    def __init__(self):
        self.conditions = self._process()

    def _get_mdm_pppcp_overrides(self):
        """Returns PPPCP identifiers from MDM overrides."""
        result = set()

        _mdmoverrides = '/Library/Application Support/com.apple.TCC/MDMOverrides.plist'

        if os.path.exists(_mdmoverrides):
            _overrides = plist.readPlist(path=_mdmoverrides)

            if _overrides:
                for _override, _payloads in _overrides.items():
                    for _payload, _values in _payloads.items():
                        _identifier = _values.get('Identifier', None)

                        result.add(_identifier)

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result['pppcp_payloads'] = list(self._get_mdm_pppcp_overrides())

        return result


def main():
    pppcp = PPPCPConditions()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=pppcp.conditions)


if __name__ == '__main__':
    main()
