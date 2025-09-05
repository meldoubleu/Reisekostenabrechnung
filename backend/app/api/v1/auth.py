from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import timedelta

from ...core.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password, get_password_hash
from ..deps import get_db, get_current_user
from ...models.user import User as UserModel, UserRole
from ...crud import crud_user
from ...schemas.user import UserCreate

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str
    company: str = "Demo GmbH"
    department: str = "General"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    company: str
    department: str


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token."""
    
    # Get user from database
    user = await crud_user.get_by_email(db, email=login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not user.password_hash or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "company": user.company or "Demo Company",
            "department": user.department or "Demo Department"
        }
    }


@router.post("/register", response_model=TokenResponse)
async def register(register_data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user and return JWT token."""
    
    # Check if user already exists
    existing_user = await crud_user.get_by_email(db, email=register_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    try:
        user_role = UserRole(register_data.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be one of: admin, controller, employee"
        )
    
    # Hash password
    hashed_password = get_password_hash(register_data.password)
    
    # Create user
    user_data = UserCreate(
        email=register_data.email,
        name=register_data.name,
        role=register_data.role,
        company=register_data.company,
        department=register_data.department,
        password_hash=hashed_password,
        is_active=True
    )
    
    user = await crud_user.create(db, obj_in=user_data)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "company": user.company or "Demo Company",
            "department": user.department or "Demo Department"
        }
    }


@router.get("/me")
async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        "company": current_user.company or "Demo Company",
        "department": current_user.department or "Demo Department"
    }
