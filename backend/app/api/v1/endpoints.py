from fastapi import APIRouter, HTTPException, Body, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
from pathlib import Path
from datetime import datetime

from ...crud import crud_travel, crud_user
from ...schemas.travel import Travel, TravelCreate, TravelUpdate, TravelStatusUpdate, ReceiptUpdate, Receipt as ReceiptSchema
from ...models.travel import Receipt
from ...models.user import UserRole, User as UserModel
from ..deps import get_db, get_current_user
from ...services.receipt_parsing import receipt_parser


router = APIRouter()


@router.post("/", response_model=Travel, status_code=200)
async def create_travel(
    *,
    db: AsyncSession = Depends(get_db),
    travel_in: TravelCreate,
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new travel expense report."""
    # Employees can only create their own travel reports
    if current_user.role == UserRole.employee:
        travel_in.employee_id = current_user.id
    
    return await crud_travel.create(db=db, obj_in=travel_in)


@router.get("/", response_model=List[Travel])
async def get_all_travels(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    employee_name: Optional[str] = None,
    employee_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    """Get travel reports based on user role."""
    # Employees can only see their own travels
    if current_user.role == UserRole.employee:
        return await crud_travel.get_multi_by_employee_id(
            db, employee_id=current_user.id, skip=skip, limit=limit
        )
    
    # Controllers can only see travels of their assigned employees
    elif current_user.role == UserRole.controller:
        # Get employees assigned to this controller
        controller_employees = await crud_user.get_employees_by_controller(
            db, controller_id=current_user.id, skip=0, limit=1000
        )
        
        if not controller_employees:
            return []
        
        # Get travels for all these employees
        employee_ids = [emp.id for emp in controller_employees]
        travels = []
        for emp_id in employee_ids:
            emp_travels = await crud_travel.get_multi_by_employee_id(
                db, employee_id=emp_id, skip=skip, limit=limit
            )
            travels.extend(emp_travels)
        return travels
    
    # Admins can see all travels
    elif current_user.role == UserRole.admin:
        if employee_id:
            return await crud_travel.get_multi_by_employee_id(
                db, employee_id=employee_id, skip=skip, limit=limit
            )
        elif employee_name:
            return await crud_travel.get_multi_by_employee(
                db, employee_name=employee_name, skip=skip, limit=limit
            )
        return await crud_travel.get_multi(db, skip=skip, limit=limit)
    
    else:
        raise HTTPException(status_code=403, detail="Access denied")


@router.get("/my", response_model=List[Travel])
async def get_my_travels(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """Get current user's travel reports."""
    if current_user.role == UserRole.employee:
        travels = await crud_travel.get_multi_by_employee_id(
            db, employee_id=current_user.id, skip=skip, limit=limit
        )
        # Filter by status if provided
        if status:
            travels = [travel for travel in travels if travel.status == status]
        return travels
    else:
        raise HTTPException(status_code=403, detail="Access denied")


@router.get("/export")
async def export_travel_data(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Export travel data as CSV."""
    if current_user.role == UserRole.employee:
        travels = await crud_travel.get_multi_by_employee_id(
            db, employee_id=current_user.id
        )
        if not travels:
            raise HTTPException(status_code=404, detail="No travel data found")
        
        # Create CSV content
        csv_content = "id,purpose,destination_city,destination_country,start_at,end_at,status\n"
        for travel in travels:
            csv_content += f"{travel.id},{travel.purpose},{travel.destination_city},{travel.destination_country},{travel.start_at},{travel.end_at},{travel.status}\n"
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=travels.csv"}
        )
    else:
        raise HTTPException(status_code=403, detail="Access denied")


@router.get("/assigned", response_model=List[Travel])
async def get_assigned_travels(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """Get travels from employees assigned to current controller."""
    if current_user.role == UserRole.controller:
        return await crud_travel.get_travels_for_controller(
            db, controller_id=current_user.id, skip=skip, limit=limit
        )
    else:
        raise HTTPException(status_code=403, detail="Controller access required")


@router.get("/{travel_id}", response_model=Travel)
async def get_travel_by_id(
    *,
    db: AsyncSession = Depends(get_db),
    travel_id: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Get a single travel report by its ID."""
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    
    # Check access permissions
    if current_user.role == UserRole.employee:
        if travel.employee_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == UserRole.controller:
        # Check if the travel belongs to one of the controller's employees
        controller_employees = await crud_user.get_employees_by_controller(
            db, controller_id=current_user.id, skip=0, limit=1000
        )
        employee_ids = [emp.id for emp in controller_employees]
        if travel.employee_id not in employee_ids:
            raise HTTPException(status_code=403, detail="Access denied")
    # Admins can access any travel
    
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
    current_user: UserModel = Depends(get_current_user)
):
    """Upload a receipt for a specific travel report and parse it automatically."""
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    
    # Check if user can access this travel
    if not await _user_can_access_travel(db, current_user, travel):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check file type
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and image files are allowed.")
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Save the file temporarily for parsing
    file_path = upload_dir / f"receipt_{travel_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Parse the receipt using the parsing service
    try:
        parsed_data = await receipt_parser.parse_receipt_file(str(file_path), file.content_type)
        parsing_status = "success" if parsed_data.parsing_confidence > 50 else "low_confidence"
    except Exception as e:
        parsed_data = None
        parsing_status = "failed"
    
    # Create receipt record with parsed data
    receipt_kwargs = {
        "travel_id": travel_id,
        "file_path": str(file_path),
        "original_filename": file.filename,
        "file_size": len(content),
        "mime_type": file.content_type,
        "currency": "EUR",
        "parsing_status": parsing_status,
        "parsed_at": datetime.utcnow() if parsed_data else None,
        "created_at": datetime.utcnow()
    }
    
    # Add parsed data if available
    if parsed_data:
        receipt_kwargs.update({
            "amount": parsed_data.amount,
            "vat": parsed_data.vat,
            "vat_rate": parsed_data.vat_rate,
            "merchant": parsed_data.merchant,
            "category": parsed_data.category,
            "date": parsed_data.date,
            "invoice_number": parsed_data.invoice_number,
            "payment_method": parsed_data.payment_method,
            "merchant_address": parsed_data.merchant_address,
            "merchant_tax_id": parsed_data.merchant_tax_id,
            "parsing_confidence": parsed_data.parsing_confidence,
            "ocr_text": parsed_data.ocr_text
        })
    
    receipt = Receipt(**receipt_kwargs)
    
    db.add(receipt)
    await db.commit()
    await db.refresh(receipt)
    
    # Optionally delete the file after parsing (based on your preference)
    # For now, keep it for debugging/verification
    
    return receipt


@router.put("/receipts/{receipt_id}", response_model=ReceiptSchema)
async def update_receipt(
    *,
    db: AsyncSession = Depends(get_db),
    receipt_id: int,
    receipt_in: ReceiptUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """Update receipt details like amount, merchant, category, and description."""
    # Get the receipt
    receipt = await db.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Get the associated travel to check permissions
    travel = await crud_travel.get(db, id=receipt.travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Associated travel not found")
    
    # Check if user can access this travel/receipt
    if not await _user_can_access_travel(db, current_user, travel):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update receipt fields if provided
    update_data = receipt_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(receipt, field, value)
    
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


@router.post("/submit", response_model=Travel, status_code=201)
async def submit_travel(
    *,
    db: AsyncSession = Depends(get_db),
    travel_in: TravelCreate,
    current_user: UserModel = Depends(get_current_user)
):
    """Submit a new travel expense report."""
    # Employees can only create their own travel reports
    if current_user.role == UserRole.employee:
        travel_in.employee_id = current_user.id
    
    travel = await crud_travel.create(db=db, obj_in=travel_in)
    # Automatically submit the travel
    travel.status = "submitted"
    await db.commit()
    # Refresh and load relationships
    await db.refresh(travel)
    travel = await crud_travel.get(db, id=travel.id)  # This loads relationships
    return travel


@router.get("/{travel_id}/export")
async def export_travel_pdf(
    *,
    db: AsyncSession = Depends(get_db),
    travel_id: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Export a travel report as PDF."""
    from fastapi.responses import Response
    
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    
    # Check access permissions
    if not await _user_can_access_travel(db, current_user, travel):
        raise HTTPException(status_code=403, detail="Access denied")
    
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


@router.get("/{travel_id}/receipts")
async def get_travel_receipts(
    *,
    db: AsyncSession = Depends(get_db),
    travel_id: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Get receipts for a specific travel report."""
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    
    # Check if user can access this travel
    if (current_user.role == UserRole.employee and travel.employee_id != current_user.id) or \
       (current_user.role == UserRole.controller and not await _user_can_access_travel(db, current_user, travel)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return travel.receipts


@router.post("/{travel_id}/submit", response_model=Travel)
async def submit_existing_travel(
    *,
    db: AsyncSession = Depends(get_db),
    travel_id: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Submit an existing travel for approval."""
    travel = await crud_travel.get(db, id=travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    
    # Check access permissions  
    if current_user.role == UserRole.employee:
        if travel.employee_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Update status to submitted
    travel.status = "submitted"
    await db.commit()
    await db.refresh(travel)
    return travel


async def _user_can_access_travel(db: AsyncSession, user: UserModel, travel) -> bool:
    """Check if a user can access a specific travel."""
    if user.role == UserRole.admin:
        return True
    elif user.role == UserRole.employee:
        return travel.employee_id == user.id
    elif user.role == UserRole.controller:
        # Check if the travel belongs to an employee assigned to this controller
        if travel.employee_id:
            employee = await crud_user.get(db, id=travel.employee_id)
            return employee and employee.controller_id == user.id
    return False
