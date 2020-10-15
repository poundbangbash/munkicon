#!/usr/local/munki/python
import os

try:
    from munkicon import plist
    from munkicon import worker
except ImportError:
    from .munkicon import plist
    from .munkicon import worker


class SystemExtensionPolicyConditions(object):
    """Whitelisted System Extension's as applied by MDM or set by user."""
    def __init__(self):

        self.conditions = self._process()

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = {'sys_ext_teams': set(),
                  'sys_ext_bundles': set(),
                  'sys_ext_team_bundle': set()}

        _db_file = '/Library/SystemExtensions/db.plist'

        if os.path.exists(_db_file):
            _exts = plist.readPlist(path=_db_file)['extensions']

            if _exts:
                for _e in _exts:
                    _bundle_id = _e.get('identifier', None)
                    _team_id = _e.get('teamID', None)
                    _state = _e.get('state', None)

                    if _state == 'activated_enabled':
                        if _bundle_id:
                            result['sys_ext_bundles'].add(_bundle_id)

                        if _team_id:
                            result['sys_ext_teams'].add(_team_id)

                        if _bundle_id and _team_id:
                            result['sys_ext_team_bundle'].add('{},{}'.format(_team_id, _bundle_id))

                result['sys_ext_teams'] = list(result['sys_ext_teams'])
                result['sys_ext_bundles'] = list(result['sys_ext_bundles'])
                result['sys_ext_team_bundle'] = list(result['sys_ext_team_bundle'])

        return result


def main():
    s_ext = SystemExtensionPolicyConditions()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=s_ext.conditions)


if __name__ == '__main__':
    main()
