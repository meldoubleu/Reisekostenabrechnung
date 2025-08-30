from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import enum


class TravelStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class ExpenseCategory(str, enum.Enum):
    lodging = "lodging"
    transport = "transport"
    meals = "meals"
    entertainment = "entertainment"
    other = "other"


class ReceiptBase(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    date: Optional[datetime] = None
    vat: Optional[float] = None
    merchant: Optional[str] = None
    category: Optional[ExpenseCategory] = None
    notes: Optional[str] = None


class ReceiptCreate(ReceiptBase):
    pass


class Receipt(ReceiptBase):
    id: int
    travel_id: int
    file_path: str

    class Config:
        from_attributes = True


class TravelBase(BaseModel):
    employee_name: str = Field(...)
    start_at: datetime
    end_at: datetime
    destination_city: str
    destination_country: str
    purpose: str
    cost_center: Optional[str] = None
    status: TravelStatus = TravelStatus.draft


class TravelCreate(TravelBase):
    pass


class TravelUpdate(TravelBase):
    pass


class TravelStatusUpdate(BaseModel):
    status: TravelStatus


class Travel(TravelBase):
    id: int
    receipts: List[Receipt] = Field(default_factory=list)

    class Config:
        from_attributes = True
