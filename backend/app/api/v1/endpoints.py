from fastapi import APIRouter, HTTPException, Body, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
from pathlib import Path

from ...crud import crud_travel, crud_user
from ...schemas.travel import Travel, TravelCreate, TravelUpdate, TravelStatusUpdate
from ...models.travel import Receipt
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
    employee_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    """Get all travel reports, optionally filtered by employee name or ID."""
    if employee_id:
        return await crud_travel.get_multi_by_employee_id(
            db, employee_id=employee_id, skip=skip, limit=limit
        )
    elif employee_name:
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
    
    # Create the receipt record in the database
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Save the file
    file_path = upload_dir / f"receipt_{travel_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create receipt record
    receipt = Receipt(
        travel_id=travel_id,
        file_path=str(file_path),
        amount=None,  # Could be extracted via OCR later
        currency="EUR",
        merchant=None
    )
    
    db.add(receipt)
    await db.commit()
    await db.refresh(receipt)
    
    return receipt


@router.get("/employee/{employee_id}/travels", response_model=List[Travel])
async def get_travels_by_employee_id(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: int,
    skip: int = 0,
    limit: int = 100,
):
    """Get all travels for a specific employee by ID."""
    return await crud_travel.get_multi_by_employee_id(
        db, employee_id=employee_id, skip=skip, limit=limit
    )


@router.get("/controller/{controller_id}/travels", response_model=List[Travel])
async def get_travels_for_controller(
    *,
    db: AsyncSession = Depends(get_db),
    controller_id: int,
    skip: int = 0,
    limit: int = 100,
):
    """Get all travels from employees assigned to a specific controller."""
    return await crud_travel.get_travels_for_controller(
        db, controller_id=controller_id, skip=skip, limit=limit
    )


@router.put("/{travel_id}/approve", response_model=Travel)
async def approve_travel(
    *,
    db: AsyncSession = Depends(get_db),
    travel_id: int,
):
    """Approve a travel report (controller action)."""
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    
    travel.status = "approved"
    db.add(travel)
    await db.commit()
    await db.refresh(travel)
    return travel


@router.put("/{travel_id}/reject", response_model=Travel)
async def reject_travel(
    *,
    db: AsyncSession = Depends(get_db),
    travel_id: int,
):
    """Reject a travel report (controller action)."""
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    
    travel.status = "rejected"
    db.add(travel)
    await db.commit()
    await db.refresh(travel)
    return travel


@router.post("/{travel_id}/submit", response_model=Travel)
async def submit_travel(
    *,
    db: AsyncSession = Depends(get_db),
    travel_id: int,
):
    """Submit a travel report for approval."""
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    
    travel.status = "submitted"
    db.add(travel)
    await db.commit()
    await db.refresh(travel)
    return travel


@router.get("/{travel_id}/export")
async def export_travel_pdf(
    *,
    db: AsyncSession = Depends(get_db),
    travel_id: int,
):
    """Export a travel report as PDF."""
    from fastapi.responses import Response
    
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    
    # Create a simple PDF content (in real implementation, you'd use a proper PDF library)
    pdf_content = f"""
    Travel Report PDF Export
    ID: {travel.id}
    Employee: {travel.employee_name}
    Destination: {travel.destination_city}, {travel.destination_country}
    Purpose: {travel.purpose}
    Status: {travel.status}
    """.encode('utf-8')
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=travel_{travel_id}.pdf"}
    )
