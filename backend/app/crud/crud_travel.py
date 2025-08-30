from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from ..models.travel import Travel
from ..models.user import User
from ..schemas.travel import TravelCreate, TravelUpdate


async def get(db: AsyncSession, id: int) -> Optional[Travel]:
    result = await db.execute(
        select(Travel)
        .options(selectinload(Travel.receipts), selectinload(Travel.employee))
        .filter(Travel.id == id)
    )
    return result.scalars().first()


async def get_multi(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Travel]:
    result = await db.execute(
        select(Travel)
        .options(selectinload(Travel.receipts), selectinload(Travel.employee))
        .order_by(Travel.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_multi_by_employee(
    db: AsyncSession, employee_name: str, skip: int = 0, limit: int = 100
) -> List[Travel]:
    result = await db.execute(
        select(Travel)
        .options(selectinload(Travel.receipts), selectinload(Travel.employee))
        .filter(Travel.employee_name == employee_name)
        .order_by(Travel.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_multi_by_employee_id(
    db: AsyncSession, employee_id: int, skip: int = 0, limit: int = 100
) -> List[Travel]:
    """Get travels by employee ID (new method for proper relationship)."""
    result = await db.execute(
        select(Travel)
        .options(selectinload(Travel.receipts))
        .filter(Travel.employee_id == employee_id)
        .order_by(Travel.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_travels_for_controller(
    db: AsyncSession, controller_id: int, skip: int = 0, limit: int = 100
) -> List[Travel]:
    """Get all travels from employees assigned to a specific controller."""
    result = await db.execute(
        select(Travel)
        .options(selectinload(Travel.receipts), selectinload(Travel.employee))
        .join(User, Travel.employee_id == User.id)
        .filter(User.controller_id == controller_id)
        .order_by(Travel.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create(db: AsyncSession, *, obj_in: TravelCreate) -> Travel:
    db_obj = Travel(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    # Eagerly load the receipts and employee relationship to prevent MissingGreenlet error
    result = await db.execute(
        select(Travel)
        .options(selectinload(Travel.receipts), selectinload(Travel.employee))
        .filter(Travel.id == db_obj.id)
    )
    return result.scalars().first()


async def update(db: AsyncSession, *, db_obj: Travel, obj_in: TravelUpdate) -> Travel:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def remove(db: AsyncSession, *, id: int) -> Optional[Travel]:
    result = await db.execute(select(Travel).filter(Travel.id == id))
    obj = result.scalars().first()
    if obj:
        await db.delete(obj)
        await db.commit()
    return obj
