import os
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt

# Concept for Interview: Password Hashing vs Encryption
# Hashing is a one-way function (cannot be decrypted). We use bcrypt which includes a salt.
# A salt protects against rainbow table attacks by adding random data to the password before hashing.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generates a bcrypt hash for the password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Concept for Interview: JWT (JSON Web Token)
    JWT is a stateless authentication mechanism. The server doesn't store the session.
    Instead, it cryptographically signs the token.
    Structure: Header (algorithm) . Payload (data/claims) . Signature
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Add 'sub' (subject, typically user ID) and 'exp' (expiration) claims
    to_encode.update({"exp": expire})
    
    # Sign the token using HMAC SHA-256 (HS256)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
