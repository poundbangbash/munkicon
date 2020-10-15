#!/usr/local/munki/python
import subprocess
import sys

try:
    from munkicon import plist
    from munkicon import worker
except ImportError:
    from .munkicon import plist
    from .munkicon import worker


class UserAccounts(object):
    def __init__(self):
        self.conditions = self._process()

    def _user_list(self):
        """Generate a list of users that exist on the system"""
        result = None

        _cmd = ['/usr/bin/dscl', '.', '-list', '/Users']

        _subprocess = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _result, _error = _subprocess.communicate()

        if _subprocess.returncode == 0:
            if _result:
                result = {x.decode('utf-8').strip() for x in _result.splitlines()}
        else:
            sys.exit(1)

        return result

    def _get_users(self):
        """Reads all users info."""
        result = set()
        _users = self._user_list()

        _ignored_users = ['nobody', 'daemon']

        if _users:
            for _user in _users:
                _result = None
                _home_dir = None

                _cmd = ['/usr/bin/dscl', '-plist', '.', '-read', '/Users/{}'.format(_user), 'NFSHomeDirectory']

                _subprocess = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _result, _error = _subprocess.communicate()

                if _subprocess.returncode == 0:
                    if _result:
                        _home_dir = plist.readPlistFromString(_result)['dsAttrTypeStandard:NFSHomeDirectory']

                        if _home_dir:
                            try:
                                _result = '{},{}'.format(_user, _home_dir[0].strip())
                            except IndexError:
                                _result = '{},{}'.format(_user, _home_dir.strip())
                else:
                    sys.exit(1)

                if _result and not _result.startswith('_') and _user not in _ignored_users:
                    result.add(_result)

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = {'user_home_path': set()}

        result['user_home_path'] = list(self._get_users())

        return result


def main():
    users = UserAccounts()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=users.conditions)


if __name__ == '__main__':
    main()
