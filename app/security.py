"""
Centralized password verification.

The expected password hash is read from the environment variable
``JARVIS_PASSWORD_HASH``.  Generate a hash for a new password with::

    python -c "from app.security import hash_password; \
        print(hash_password('my-secret'))"

If the variable is **not** set, the application refuses to start and
shows an error dialog explaining how to configure it.
"""

import hashlib
import hmac
import os

# Fixed salt so that the same password always produces the same hash.
# This is acceptable because the hash is compared locally, not stored
# in a multi-user database.
_SALT = b"jarvis-finance-salt"


def hash_password(password: str) -> str:
    """Return a hex-encoded SHA-256 HMAC of *password*."""
    return hmac.new(
        _SALT, password.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def verify_password(password: str) -> bool:
    """Check *password* against ``JARVIS_PASSWORD_HASH``.

    Returns ``False`` when the env-var is missing **or** the hash does
    not match.
    """
    expected = os.environ.get("JARVIS_PASSWORD_HASH", "")
    if not expected:
        return False
    return hmac.compare_digest(hash_password(password), expected)


def is_password_configured() -> bool:
    """Return True when JARVIS_PASSWORD_HASH is set."""
    return bool(os.environ.get("JARVIS_PASSWORD_HASH", ""))
