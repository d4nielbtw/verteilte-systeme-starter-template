from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError, VerificationError
from .config import settings

# Defaults von argon2-cffi folgen den OWASP-Empfehlungen (Argon2id, t=3, m=64MiB, p=4)
ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hash_str: str) -> bool:
    try:
        ph.verify(hash_str, password)
        return True
    except (VerifyMismatchError, InvalidHashError, VerificationError):
        return False

def needs_rehash(hash_str: str) -> bool:
    # Wenn Argon2-Parameter später erhöht werden, automatisch upgraden
    return ph.check_needs_rehash(hash_str)

def create_access_token(subject: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),                                       # JWT-Standard: sub ist string
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expiry_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])