from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import SessionLocal
from ..core.auth import verify_token
from ..crud import crud_user
from ..models.user import User as UserModel, UserRole

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import SessionLocal
from ..core.auth import verify_token
from ..core.logging import logger
from ..crud import crud_user
from ..models.user import User as UserModel, UserRole

security = HTTPBearer()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with SessionLocal() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    """Get the current authenticated user."""
    try:
        token = credentials.credentials
        logger.debug(f"Verifying token for authentication")
        payload = verify_token(token)
        
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token verification failed: no user ID in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id_int = int(user_id)
        logger.debug(f"Token verified for user ID: {user_id_int}")
        
        # For demo users, create a mock user object
        # Updated to match actual database users
        if user_id_int in [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 997, 998, 999]:
            role_map = {
                1: UserRole.admin,       # admin@demo.com (FIXED: was controller)
                2: UserRole.controller,  # controller1@demo.com  
                3: UserRole.employee,    # max.mustermann@demo.com
                5: UserRole.employee,    # michael.weber@demo.com
                6: UserRole.employee,    # lisa.mueller@demo.com
                7: UserRole.controller,  # controller2@demo.com
                8: UserRole.controller,  # test@test.com
                9: UserRole.employee,    # test123@test.com
                11: UserRole.employee,   # malte@demo.com
                12: UserRole.employee,   # test.employee@demo.com
                13: UserRole.employee,   # integration.test@demo.com
                997: UserRole.employee,
                998: UserRole.controller,
                999: UserRole.admin
            }
            mock_user = UserModel()
            mock_user.id = user_id_int
            mock_user.email = payload.get("email", "demo@example.com")
            mock_user.name = payload.get("name", "Demo User")
            mock_user.role = role_map.get(user_id_int, UserRole.employee)
            mock_user.company = "Demo Company"
            mock_user.department = "Demo Department"
            logger.debug(f"Created mock user for ID {user_id_int} with role {mock_user.role}")
            return mock_user
        
        # For real users, fetch from database
        user = await crud_user.get(db, id=user_id_int)
        if user is None:
            logger.warning(f"User not found in database: {user_id_int}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.debug(f"Found user in database: {user.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during user authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """Get the current user and verify they are an admin."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_controller_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """Get the current user and verify they are a controller."""
    if current_user.role != UserRole.controller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Controller access required"
        )
    return current_user


async def get_current_employee_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """Get the current user and verify they are an employee."""
    if current_user.role != UserRole.employee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required"
        )
    return current_user
