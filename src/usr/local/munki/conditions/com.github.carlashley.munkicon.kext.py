#!/usr/local/munki/python
import os
import sqlite3
import sys

try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker


class SQLite():
    """Simple class for connecting/disconnecting to SQLite databases."""
    connection = ''
    c = ''

    def connect(self, db):
        """Connect."""
        try:
            self.connection.execute("")
        except Exception:
            try:
                self.connection = sqlite3.connect(db)
                self.c = self.connection.cursor()
            except Exception:
                sys.exit(1)

    def disconnect(self, db):
        """Disconnect."""
        try:
            self.connection.execute("")
            try:
                self.connection.close()
                try:
                    self.connection.execute("")
                except Exception:
                    sys.exit(1)
            except Exception:
                sys.exit(1)
        except Exception:
            pass

    def query(self, query_string, fetch=False):
        """Query."""
        try:
            self.c.execute(query_string)
            if not fetch:
                self.c.execute(query_string)
            else:
                self.c.execute(query_string)
                return self.c.fetchall()
        except Exception:
            raise


class KextPolicyConditions(object):
    """Whitelisted KEXT's as applied by MDM or set by user."""
    def __init__(self):
        self._kextpolicy = '/var/db/SystemPolicyConfiguration/KextPolicy'

        self.conditions = self._process()

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = {'kext_teams': set(),
                  'kext_bundles': set(),
                  'kext_team_bundle': set()}

        if os.path.exists(self._kextpolicy) and os.geteuid() == 0:  # Must be root to read this file
            _sqldb = SQLite()

            _sqldb.connect(self._kextpolicy)
            _mdm_query = _sqldb.query('SELECT team_id, bundle_id, allowed FROM kext_policy_mdm', fetch=True)
            _user_query = _sqldb.query('SELECT team_id, bundle_id, allowed FROM kext_policy', fetch=True)

            if _mdm_query:
                for _team_id, _bundle_id, allowed in _mdm_query:
                    if allowed == 1:
                        if _team_id:
                            result['kext_teams'].add(_team_id)

                        if _bundle_id:
                            result['kext_bundles'].add(_bundle_id)

                        if _team_id and _bundle_id:
                            result['kext_team_bundle'].add('{},{}'.format(_team_id, _bundle_id))

            if _user_query:
                for _team_id, _bundle_id, allowed in _user_query:
                    if allowed == 1:
                        if _team_id:
                            result['kext_teams'].add(_team_id)

                        if _bundle_id:
                            result['kext_bundles'].add(_bundle_id)

                        if _team_id and _bundle_id:
                            result['kext_team_bundle'].add('{},{}'.format(_team_id, _bundle_id))

        result['kext_teams'] = list(result['kext_teams'])
        result['kext_bundles'] = list(result['kext_bundles'])
        result['kext_team_bundle'] = list(result['kext_team_bundle'])

        return result


def main():
    kext = KextPolicyConditions()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=kext.conditions)


if __name__ == '__main__':
    main()
