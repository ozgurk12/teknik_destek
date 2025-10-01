from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import bcrypt
import jwt
from app.core.config import settings

def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict] = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }

    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)  # 7 days default

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Handle both bcrypt and argon2 hashes
    password_bytes = plain_password.encode('utf-8')

    # Truncate password to 72 bytes for bcrypt compatibility
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Check if it's an argon2 hash (starts with $argon2)
    if hashed_password.startswith('$argon2'):
        # For argon2 hashes, we need to use argon2-cffi
        try:
            from argon2 import PasswordHasher
            ph = PasswordHasher()
            ph.verify(hashed_password, plain_password)
            return True
        except:
            return False
    else:
        # For bcrypt hashes
        try:
            return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
        except:
            return False

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')

    # Truncate password to 72 bytes for bcrypt compatibility
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def decode_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.DecodeError):
        return None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Şifre en az 8 karakter olmalıdır"

    if not any(char.isdigit() for char in password):
        return False, "Şifre en az bir rakam içermelidir"

    if not any(char.isupper() for char in password):
        return False, "Şifre en az bir büyük harf içermelidir"

    if not any(char.islower() for char in password):
        return False, "Şifre en az bir küçük harf içermelidir"

    return True, ""