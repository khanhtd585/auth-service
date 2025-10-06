# src/utils/hash_utils.py
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError
from typing import Optional
import hmac
import hashlib

# Configure Argon2 parameters as needed (adjust by your hardware)
ph = PasswordHasher(
    time_cost=3,
    memory_cost=64 * 1024,  # 64 MiB
    parallelism=2,
    hash_len=32,
    type=Type.ID
)

def _apply_pepper(password: str, pepper: Optional[str]) -> str:
    if not pepper:
        return password
    # Use HMAC-SHA256 to incorporate pepper (pepper is secret)
    return hmac.new(pepper.encode(), password.encode(), hashlib.sha256).hexdigest()

def hash_password(password: str, pepper: Optional[str] = None) -> str:
    pw = _apply_pepper(password, pepper)
    return ph.hash(pw)  # returns encoded string with params & salt

def verify_password(password: str, hash_str: str, pepper: Optional[str] = None) -> bool:
    pw = _apply_pepper(password, pepper)
    try:
        return ph.verify(hash_str, pw)
    except VerifyMismatchError:
        return False