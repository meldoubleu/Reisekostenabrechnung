from pydantic import BaseModel, Field, model_validator
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
    # Optional employee_id for new relationship-based travel creation
    employee_id: Optional[int] = None
    
    @model_validator(mode='after')
    def validate_date_range(self):
        """Validate that end_at is after start_at."""
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValueError("End date must be after start date")
        return self


class TravelUpdate(TravelBase):
    employee_id: Optional[int] = None


class TravelStatusUpdate(BaseModel):
    status: TravelStatus


class Travel(TravelBase):
    id: int
    employee_id: Optional[int] = None
    receipts: List[Receipt] = Field(default_factory=list)

    class Config:
        from_attributes = True
