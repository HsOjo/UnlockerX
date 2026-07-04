from __future__ import annotations

import getpass

from app.platform import proc


def verify_password(password: str) -> bool:
    """Validate the current user's login password locally via directory services.

    Called once per user-entered attempt (never in a loop), so it will not trip
    the account lockout that repeated wrong entries at the lock screen would.
    """
    stat, _, _ = proc.run(['/usr/bin/dscl', '.', '-authonly', getpass.getuser(), password])
    return stat == 0
