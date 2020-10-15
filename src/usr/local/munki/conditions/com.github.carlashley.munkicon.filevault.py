#!/usr/local/munki/python
import os
import subprocess
import sys

try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker


class FileVaultConditions(object):
    """FileVault conditions."""
    def __init__(self):
        self.conditions = self._process()

    def _fdesetup(self, verb):
        """Executes the `fdesetup` command and processes output."""
        result = None

        if os.geteuid() == 0:
            _cmd = ['/usr/bin/fdesetup', verb]

            _subprocess = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _result, _error = _subprocess.communicate()

            if _subprocess.returncode == 0 or (verb == 'showdeferralinfo' and _subprocess.returncode == 20):
                if _result:
                    if isinstance(_result, bytes):
                        _result = _result.decode('utf-8').strip()

                    result = _result
        else:
            sys.exit(1)

        return result

    def _get_status(self):
        """FileVault state (on or off) and returns True/False for encryption/decryption processes when
        FileVault has been turned on."""
        result = {'status': '',
                  'encryption_in_progress': False,
                  'decryption_in_progress': False}

        _result = self._fdesetup(verb='status')

        if _result:
            _lines = _result.strip().splitlines()
            for _line in _lines:
                _line = _line.strip()

                if 'FileVault is ' in _line:
                    _fv_state = _line.replace('FileVault is ', '').lower().replace('.', '')
                    # _fv_state = _result.replace('FileVault is ', '').lower().replace('.', '')

                    result['status'] = _fv_state

                result['encryption_status'] = True if 'Encryption in progress: Percent completed = ' in _line else False
                result['decryption_status'] = True if 'Decryption in progress: Percent completed = ' in _line else False

        return result

    def _get_isactive(self):
        """FileVault is on and active. This differs to `status`."""
        result = False

        _result = self._fdesetup(verb='isactive')

        if _result:
            result = True if _result == 'true' else False

        return result

    def _get_users(self):
        """Array of FileVault users."""
        result = None

        _result = self._fdesetup(verb='list')

        if _result:
            # This returns the 'username,GeneratedUID' of each user that is added to FileVault,
            # however the GeneratedUID value cannot be known ahead of time, and will be different,
            # so each 'username,GeneratedUID' is split and only the 'username' value is kept.
            result = {_line.strip().split(',')[0] for _line in _result.splitlines()}

        return result

    def _get_deferralinfo(self):
        """Deferrals are active or none exist."""
        result = None

        _result = self._fdesetup(verb='showdeferralinfo')

        if _result:
            _lines = _result.splitlines()

            for _line in _lines:
                if 'Not found.' in _line:
                    result = 'not_found'
                    break
                elif 'Defer' in _line:
                    result = 'active'
                    break

        return result

    def _get_has_personal_recovery_key(self):
        """Personal recovery key is in use."""
        result = False

        _result = self._fdesetup(verb='haspersonalrecoverykey')

        if _result:
            result = True if _result == 'true' else False

        return result

    def _get_has_institute_recovery_key(self):
        """Institutional recovery key is in use."""
        result = False

        _result = self._fdesetup(verb='hasinstitutionalrecoverykey')

        if _result:
            result = True if _result == 'true' else False

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = {'filevault_active': self._get_isactive(),
                  'filevault_deferral': '',
                  'filevault_institution_key': self._get_has_institute_recovery_key(),
                  'filevault_personal_key': self._get_has_personal_recovery_key(),
                  'filevault_status': '',
                  'filevault_users': list()}

        _fde_deferral = self._get_deferralinfo()
        _fde_status = self._get_status()
        _fde_users = self._get_users()

        if _fde_deferral:
            result['filevault_deferral'] = _fde_deferral

        if _fde_status:
            result['filevault_status'] = _fde_status.get('status', '')
            result['filevault_encryption_in_progress'] = _fde_status.get('encryption_status', False)
            result['filevault_decryption_in_progress'] = _fde_status.get('decryption_status', False)

        if _fde_users:
            result['filevault_users'] = list(_fde_users)

        return result


def main():
    fde = FileVaultConditions()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=fde.conditions)


if __name__ == '__main__':
    main()
