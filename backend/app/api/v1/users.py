from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...crud import crud_user
from ...schemas.user import User, UserCreate, UserUpdate, UserWithRelations
from ..deps import get_db, get_current_admin_user, get_current_controller_user
from ...models.user import User as UserModel

router = APIRouter()


@router.post("/", response_model=User, status_code=201)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Create a new user. Admin only."""
    # Check if user with this email already exists
    existing_user = await crud_user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    return await crud_user.create(db=db, obj_in=user_in)


@router.get("/", response_model=List[UserWithRelations])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100,
):
    """Get all users with their relationships."""
    return await crud_user.get_multi(db, skip=skip, limit=limit)


@router.get("/controllers", response_model=List[UserWithRelations])
async def get_controllers(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get all controllers with their assigned employees. Admin only."""
    return await crud_user.get_controllers(db)


@router.get("/my-team", response_model=List[User])
async def get_my_team(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_controller_user),
    skip: int = 0,
    limit: int = 100,
):
    """Get all employees assigned to the current controller."""
    return await crud_user.get_employees_by_controller(
        db, controller_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/{user_id}", response_model=UserWithRelations)
async def get_user_by_id(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get a user by ID with their relationships. Admin only."""
    user = await crud_user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/email/{email}", response_model=UserWithRelations)
async def get_user_by_email(
    *,
    db: AsyncSession = Depends(get_db),
    email: str,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get a user by email with their relationships. Admin only."""
    user = await crud_user.get_by_email(db=db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Update a user. Admin only."""
    user = await crud_user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return await crud_user.update(db=db, db_obj=user, obj_in=user_in)


@router.put("/{employee_id}/assign-controller/{controller_id}", response_model=User)
async def assign_controller_to_employee(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: int,
    controller_id: int,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Assign a controller to an employee. Admin only."""
    try:
        return await crud_user.assign_controller(db=db, employee_id=employee_id, controller_id=controller_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/controller/{controller_id}/employees", response_model=List[User])
async def get_employees_by_controller(
    *,
    db: AsyncSession = Depends(get_db),
    controller_id: int,
    current_user: UserModel = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100,
):
    """Get all employees assigned to a specific controller. Admin only."""
    return await crud_user.get_employees_by_controller(
        db, controller_id=controller_id, skip=skip, limit=limit
    )


@router.delete("/{user_id}", response_model=User)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Delete a user. Admin only."""
    user = await crud_user.remove(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
