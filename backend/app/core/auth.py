from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

# For demo purposes, using a simple secret. In production, use environment variables
SECRET_KEY = "demo-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate_demo_user(email: str, password: str) -> Optional[dict]:
    """Demo authentication function."""
    # For demo purposes, we accept any password for specific demo accounts
    demo_users = {
        'admin@demo.com': {'role': 'admin', 'id': 1, 'name': 'Admin User'},
        'controller@demo.com': {'role': 'controller', 'id': 2, 'name': 'Controller User'},
        'employee@demo.com': {'role': 'employee', 'id': 3, 'name': 'Employee User'},
    }
    
    if email in demo_users and password:  # Any non-empty password works for demo
        return demo_users[email]
    
    # For other emails, determine role based on email pattern
    if email and password:
        if 'admin' in email.lower():
            return {'role': 'admin', 'id': 999, 'name': email.split('@')[0]}
        elif 'controller' in email.lower():
            return {'role': 'controller', 'id': 998, 'name': email.split('@')[0]}
        else:
            return {'role': 'employee', 'id': 997, 'name': email.split('@')[0]}
    
    return None
