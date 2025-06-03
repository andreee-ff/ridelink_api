from passlib.context import CryptContext

# Define a password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash a password (used during registration)
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Verify a password (used during login)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
