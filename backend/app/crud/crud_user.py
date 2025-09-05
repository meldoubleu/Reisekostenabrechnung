from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserUpdate
from ..core.auth import get_password_hash


async def get(db: AsyncSession, id: int) -> Optional[User]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.controller), selectinload(User.employees))
        .filter(User.id == id)
    )
    return result.scalars().first()


async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.controller), selectinload(User.employees))
        .filter(User.email == email)
    )
    return result.scalars().first()


async def get_multi(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.controller), selectinload(User.employees))
        .order_by(User.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_employees_by_controller(
    db: AsyncSession, controller_id: int, skip: int = 0, limit: int = 100
) -> List[User]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.controller), selectinload(User.employees))
        .filter(User.controller_id == controller_id)
        .filter(User.role == UserRole.employee)
        .order_by(User.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_controllers(db: AsyncSession) -> List[User]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.employees))
        .filter(User.role == UserRole.controller)
        .order_by(User.name)
    )
    return result.scalars().all()


async def create(db: AsyncSession, *, obj_in: UserCreate) -> User:
    # Convert schema to dict and handle password
    obj_data = obj_in.model_dump()
    
    # Handle password hashing
    if obj_data.get('password') and not obj_data.get('password_hash'):
        obj_data['password_hash'] = get_password_hash(obj_data['password'])
    
    # Remove password field since it's not in the User model
    obj_data.pop('password', None)
    
    db_obj = User(**obj_data)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    # Eagerly load the relationships to prevent MissingGreenlet error
    result = await db.execute(
        select(User)
        .options(selectinload(User.controller), selectinload(User.employees))
        .filter(User.id == db_obj.id)
    )
    return result.scalars().first()


async def update(db: AsyncSession, *, db_obj: User, obj_in: UserUpdate) -> User:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def assign_controller(db: AsyncSession, employee_id: int, controller_id: Optional[int]) -> User:
    """Assign a controller to an employee. One employee can only have one controller."""
    result = await db.execute(select(User).filter(User.id == employee_id))
    employee = result.scalars().first()
    if not employee:
        raise ValueError(f"Employee with id {employee_id} not found")
    
    if employee.role != UserRole.employee:
        raise ValueError(f"User {employee_id} is not an employee")
    
    # If assigning to a controller, verify controller exists and is a controller
    if controller_id is not None:
        result = await db.execute(select(User).filter(User.id == controller_id))
        controller = result.scalars().first()
        if not controller:
            raise ValueError(f"Controller with id {controller_id} not found")
        if controller.role != UserRole.controller:
            raise ValueError(f"User {controller_id} is not a controller")
    
    # Update assignment (can be None to unassign)
    employee.controller_id = controller_id
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return employee


async def remove(db: AsyncSession, *, id: int) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == id))
    obj = result.scalars().first()
    if obj:
        await db.delete(obj)
        await db.commit()
    return obj
