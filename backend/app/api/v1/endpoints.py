from fastapi import APIRouter, HTTPException, Body, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...crud import crud_travel
from ...schemas.travel import Travel, TravelCreate, TravelUpdate, TravelStatusUpdate
from ..deps import get_db


router = APIRouter()


@router.post("/", response_model=Travel, status_code=200)
async def create_travel(
    *,
    db: AsyncSession = Depends(get_db),
    travel_in: TravelCreate
):
    """Create a new travel expense report."""
    return await crud_travel.create(db=db, obj_in=travel_in)


@router.get("/", response_model=List[Travel])
async def get_all_travels(
    db: AsyncSession = Depends(get_db),
    employee_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """Get all travel reports, optionally filtered by employee name."""
    if employee_name:
        return await crud_travel.get_multi_by_employee(
            db, employee_name=employee_name, skip=skip, limit=limit
        )
    return await crud_travel.get_multi(db, skip=skip, limit=limit)


@router.get("/{travel_id}", response_model=Travel)
async def get_travel_by_id(
    *,
    db: AsyncSession = Depends(get_db),
    travel_id: int,
):
    """Get a single travel report by its ID."""
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    return travel


@router.put("/{travel_id}", response_model=Travel)
async def update_travel(
    *,
    db: AsyncSession = Depends(get_db),
    travel_id: int,
    travel_in: TravelStatusUpdate,
):
    """Update a travel report status."""
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    
    # Update just the status
    travel.status = travel_in.status
    db.add(travel)
    await db.commit()
    await db.refresh(travel)
    return travel


@router.post("/{travel_id}/receipts", status_code=201)
async def upload_receipt(
    *,
    db: AsyncSession = Depends(get_db),
    travel_id: int,
    file: UploadFile = File(...),
):
    """Upload a receipt for a specific travel report."""
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    # Here you would handle the file upload, e.g., save it and create a receipt record
    return {"filename": file.filename, "travel_id": travel_id}
