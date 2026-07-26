from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"])


def hash_password(plain: str) -> str:
    return context.hash(plain.encode())


def verify_password(plain: str, hash: bytes) -> bool:
    return context.verify(plain, hash)
