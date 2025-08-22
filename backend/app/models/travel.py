from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Numeric, Text
from ..db.session import Base
import enum
from datetime import datetime


class TravelStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class Travel(Base):
    __tablename__ = "travels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_name: Mapped[str] = mapped_column(String(255))
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    destination_city: Mapped[str] = mapped_column(String(255))
    destination_country: Mapped[str] = mapped_column(String(255))
    purpose: Mapped[str] = mapped_column(Text)
    cost_center: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[TravelStatus] = mapped_column(Enum(TravelStatus), default=TravelStatus.draft)

    receipts: Mapped[list["Receipt"]] = relationship("Receipt", back_populates="travel", cascade="all, delete-orphan")


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
    file_path: Mapped[str] = mapped_column(String(500))
    amount: Mapped[float | None] = mapped_column(Numeric(12,2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    vat: Mapped[float | None] = mapped_column(Numeric(12,2), nullable=True)
    merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[ExpenseCategory | None] = mapped_column(Enum(ExpenseCategory), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    travel: Mapped[Travel] = relationship("Travel", back_populates="receipts")
