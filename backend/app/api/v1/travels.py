from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.app.db.session import SessionLocal
from backend.app.models.travel import Travel, Receipt, TravelStatus
from backend.app.schemas.travel import Travel as TravelSchema, Receipt as ReceiptSchema
from backend.app.services.ocr import extract_text_from_file, simple_parse
from backend.app.core.config import settings
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

router = APIRouter()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.post("/", response_model=TravelSchema)
async def create_travel(
    employee_name: str = Form(...),
    start_at: datetime = Form(...),
    end_at: datetime = Form(...),
    destination_city: str = Form(...),
    destination_country: str = Form(...),
    purpose: str = Form(...),
    cost_center: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    travel = Travel(
        employee_name=employee_name,
        start_at=start_at,
        end_at=end_at,
        destination_city=destination_city,
        destination_country=destination_country,
        purpose=purpose,
        cost_center=cost_center,
        status=TravelStatus.draft,
    )
    db.add(travel)
    await db.commit()
    await db.refresh(travel)
    
    # Load the receipts relationship to avoid serialization issues
    result = await db.execute(
        select(Travel).options(selectinload(Travel.receipts)).where(Travel.id == travel.id)
    )
    travel_with_receipts = result.scalar_one()
    return travel_with_receipts


@router.get("/", response_model=List[TravelSchema])
async def list_travels(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Travel).options(selectinload(Travel.receipts)).order_by(Travel.id.desc())
    )
    return result.scalars().all()


@router.post("/{travel_id}/receipts", response_model=ReceiptSchema)
async def upload_receipt(
    travel_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # ensure travel exists
    travel = await db.get(Travel, travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")

    # store file
    upload_dir = settings.upload_dir / f"travel_{travel_id}"
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / file.filename
    with dest.open("wb") as f:
        f.write(await file.read())

    # OCR
    text = extract_text_from_file(str(dest))
    parsed = simple_parse(text)

    receipt = Receipt(
        travel_id=travel_id,
        file_path=str(dest),
        amount=parsed.get("amount"),
        currency=parsed.get("currency"),
        date=parsed.get("date"),
        merchant=parsed.get("merchant"),
    )
    db.add(receipt)
    await db.commit()
    await db.refresh(receipt)
    return receipt


@router.post("/{travel_id}/submit", response_model=TravelSchema)
async def submit_travel(travel_id: int, db: AsyncSession = Depends(get_db)):
    travel = await db.get(Travel, travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    travel.status = TravelStatus.submitted
    await db.commit()
    await db.refresh(travel)
    
    # Load the receipts relationship to avoid serialization issues
    result = await db.execute(
        select(Travel).options(selectinload(Travel.receipts)).where(Travel.id == travel_id)
    )
    travel_with_receipts = result.scalar_one()
    return travel_with_receipts


@router.get("/{travel_id}/export", response_class=FileResponse)
async def export_pdf(travel_id: int, db: AsyncSession = Depends(get_db)):
    travel = await db.get(Travel, travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")

    # fetch receipts
    result = await db.execute(select(Receipt).where(Receipt.travel_id == travel_id))
    receipts = result.scalars().all()

    export_dir = settings.upload_dir / f"travel_{travel_id}"
    export_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = export_dir / "export.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4

    # Cover page
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30*mm, height - 30*mm, "Reisekostenabrechnung")
    c.setFont("Helvetica", 11)
    y = height - 45*mm
    lines = [
        f"Mitarbeiter: {travel.employee_name}",
        f"Zeitraum: {travel.start_at} - {travel.end_at}",
        f"Ziel: {travel.destination_city}, {travel.destination_country}",
        f"Zweck: {travel.purpose}",
        f"Kostenstelle: {travel.cost_center or '-'}",
        f"Status: {travel.status.value}",
    ]
    for line in lines:
        c.drawString(30*mm, y, line)
        y -= 7*mm
    c.showPage()

    # Summary per category (simple)
    totals = {}
    for r in receipts:
        cat = (r.category.value if r.category else "unassigned")
        totals[cat] = totals.get(cat, 0) + float(r.amount or 0)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(30*mm, height - 30*mm, "Zusammenfassung")
    c.setFont("Helvetica", 11)
    y = height - 45*mm
    for cat, total in totals.items():
        c.drawString(30*mm, y, f"{cat}: {total:.2f}")
        y -= 7*mm
    c.showPage()

    # Details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30*mm, height - 30*mm, "Details")
    c.setFont("Helvetica", 10)
    y = height - 40*mm
    for r in receipts:
        lines = [
            f"Betrag: {r.amount or '-'} {r.currency or ''}",
            f"Datum: {r.date or '-'}",
            f"Händler: {r.merchant or '-'}",
            f"Kategorie: {r.category.value if r.category else '-'}",
            f"Datei: {Path(r.file_path).name}",
        ]
        for line in lines:
            c.drawString(20*mm, y, line)
            y -= 6*mm
        y -= 4*mm
        if y < 30*mm:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 30*mm

    c.save()
    return FileResponse(str(pdf_path), filename=f"travel_{travel_id}.pdf")
