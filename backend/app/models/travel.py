from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Numeric, Text, Boolean, Float
from ..db.session import Base
import enum
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class TravelStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class Travel(Base):
    __tablename__ = "travels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Keep employee_name for backward compatibility, but add user_id for proper relationship
    employee_name: Mapped[str] = mapped_column(String(255))
    employee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    
    # Legacy fields (for backward compatibility)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Enhanced travel timeline fields
    departure_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Starting location (e.g., "Munich, Germany")
    departure_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # When leaving home/office
    arrival_at_destination_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # When arriving at destination
    departure_from_destination_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # When leaving destination
    arrival_home_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # When returning home/office
    
    destination_city: Mapped[str] = mapped_column(String(255))
    destination_country: Mapped[str] = mapped_column(String(255))
    purpose: Mapped[str] = mapped_column(Text)
    total_expenses: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)  # Total travel expenses
    cost_center: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[TravelStatus] = mapped_column(Enum(TravelStatus), default=TravelStatus.draft)

    # Relationships
    employee: Mapped[Optional["User"]] = relationship("User", back_populates="travels")
    receipts: Mapped[List["Receipt"]] = relationship("Receipt", back_populates="travel", cascade="all, delete-orphan")


class ExpenseCategory(str, enum.Enum):
    lodging = "lodging"
    transport = "transport"
    meals = "meals"
    entertainment = "entertainment"
    other = "other"


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    travel_id: Mapped[int] = mapped_column(ForeignKey("travels.id"), index=True)
    
    # File handling - will be optional/temporary for parsing
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Parsed receipt data (core fields)
    amount: Mapped[Optional[float]] = mapped_column(Numeric(12,2), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default="EUR")
    date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    vat: Mapped[Optional[float]] = mapped_column(Numeric(12,2), nullable=True)
    vat_rate: Mapped[Optional[float]] = mapped_column(Numeric(5,2), nullable=True)  # VAT percentage (19%, 7%, etc.)
    merchant: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[Optional[ExpenseCategory]] = mapped_column(Enum(ExpenseCategory), nullable=True)
    
    # Additional parsed fields
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # cash, card, bank_transfer
    merchant_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    merchant_tax_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Parsing metadata
    parsing_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # pending, success, failed, manual
    parsing_confidence: Mapped[Optional[float]] = mapped_column(Numeric(5,2), nullable=True)  # 0-100%
    parsed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Raw OCR output for debugging
    
    # User fields
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)  # User confirmed parsed data is correct
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    travel: Mapped["Travel"] = relationship("Travel", back_populates="receipts")
