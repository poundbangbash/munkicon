#!/usr/local/munki/python
import os

try:
    from munkicon import plist
    from munkicon import worker
except ImportError:
    from .munkicon import plist
    from .munkicon import worker

# Keys: 'sys_ext_bundles'
#       'sys_ext_teams'
#       'sys_ext_team_bundle'


class SystemExtensionPolicyConditions(object):
    """Whitelisted System Extension's as applied by MDM or set by user."""
    def __init__(self):

        self.conditions = self._process()

    def _sys_exts(self):
        """System Extensions."""
        result = {'sys_ext_teams': list(),
                  'sys_ext_bundles': list(),
                  'sys_ext_team_bundle': list()}

        _db_file = '/Library/SystemExtensions/db.plist'
        _sys_ext_teams = set()
        _sys_ext_bundles = set()
        _sys_ext_team_bundle = set()

        if os.path.exists(_db_file):
            # Note, System Ext profiles do not have a payload key of allowed
            # Bundle ID's per https://developer.apple.com/documentation/devicemanagement/systemextensions
            _ext_policies = plist.readPlist(path=_db_file)['extensionPolicies']

            # This appears to be where manually approved items exist.
            _exts = plist.readPlist(path=_db_file)['extensions']

            # Policies managed by profiles
            for _policy in _ext_policies:
                _allowed_team_ids = _policy.get('allowedTeamIDs', None)
                _allowed_team_bundles = _policy.get('allowedExtensions', None)

                if _allowed_team_ids:
                    for _id in _allowed_team_ids:
                        _sys_ext_teams.add(_id)

                if _allowed_team_bundles:
                    for _k, _v in _allowed_team_bundles.items():
                        for _bundle in _v:
                            _team_bundle_str = '{},{}'.format(_k, _bundle)

                            _sys_ext_team_bundle.add(_team_bundle_str)

            # Policies managed by user
            if _exts:
                for _e in _exts:
                    _bundle_id = _e.get('identifier', None)
                    _team_id = _e.get('teamID', None)
                    _state = _e.get('state', None)

                    if _state == 'activated_enabled':
                        if _team_id:
                            _sys_ext_teams.add(_team_id)

                        if _bundle_id:
                            _sys_ext_bundles.add(_bundle_id)

                        if _bundle_id and _team_id:
                            _team_bundle_str = '{},{}'.format(_team_id, _bundle_id)
                            _sys_ext_team_bundle.add(_team_bundle_str)

        result['sys_ext_teams'] = list(_sys_ext_teams)
        result['sys_ext_bundles'] = list(_sys_ext_bundles)
        result['sys_ext_team_bundle'] = list(_sys_ext_team_bundle)

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._sys_exts())

        return result


def main():
    s_ext = SystemExtensionPolicyConditions()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=s_ext.conditions)


if __name__ == '__main__':
    main()
