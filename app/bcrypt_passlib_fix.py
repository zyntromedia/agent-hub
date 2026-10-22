"""
bcrypt_passlib_fix.py — compatibility shim for passlib 1.7.4 + bcrypt >= 4.1.0

PROBLEM
-------
passlib 1.7.4's bcrypt handler does, at import/init time:
    import bcrypt
    bcrypt.__about__.__version__          # <-- removed in bcrypt 4.1.0
Raises: AttributeError: module 'bcrypt' has no attribute '__about__'
on the FIRST password hash/verify (login / signup / token refresh).

FIX (quick — unblocks the bcrypt==4.3.0 bump)
---------------------------------------------
Paste these 4 lines at the TOP of the module that first imports passlib
(usually app/core/security.py or app/main.py), BEFORE any
`from passlib.context import CryptContext` line:

    import bcrypt
    from types import SimpleNamespace
    if not hasattr(bcrypt, "__about__"):
        bcrypt.__about__ = SimpleNamespace(__version__=getattr(bcrypt, "__version__", "4.0.0"))

That's it. passlib will then read the fake __about__ and work normally.

VERIFY
------
Add this test — it will fail on the unpatched branch and pass after:

    def test_password_hash_roundtrip():
        from app.core.security import get_password_hash, verify_password
        h = get_password_hash("s3cret!")
        assert verify_password("s3cret!", h) is True
        assert verify_password("wrong", h) is False

BETTER LONG-TERM (recommended)
------------------------------
passlib is unmaintained (last release 2020). Drop it and call bcrypt directly
(~10 lines, zero shims). Replace your security.py helpers with:

    import bcrypt

    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except ValueError:
            return False   # malformed hash

Then remove `passlib[bcrypt]` from requirements.txt entirely — you only need
`bcrypt==4.3.0`. This also avoids the next passlib/bcrypt breakage.

NOTES
-----
- The patch is idempotent and safe on bcrypt < 4.1 (hasattr check skips it).
- If you build on Alpine/musllinux: ensure pip >= 23 so bcrypt 4.3 wheels are
  picked up; otherwise the build falls back to compiling Rust (slow / fails).
- rounds=12 is a good 2024 default; passlib defaulted to 12 as well, so existing
  hashes stay verifiable (bcrypt stores the cost in the hash itself).
"""

# ---------------------------------------------------------------------------
# Self-contained patch (copy this block into your app startup)
# ---------------------------------------------------------------------------
import bcrypt  # noqa: E402
from types import SimpleNamespace  # noqa: E402

if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = SimpleNamespace(
        __version__=getattr(bcrypt, "__version__", "4.0.0")
    )

# Now safe to import passlib:
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
