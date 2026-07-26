from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

password_hash = PasswordHash((BcryptHasher(),))


def hash_password(plain: str) -> str:
    return password_hash.hash(plain)


def verify_password(plain: str, hash: str) -> bool:
    return password_hash.verify(plain, hash)
