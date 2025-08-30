from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class Receipt(BaseModel):
    """Model for a single receipt."""
    filename: str
    amount: float
    category: str
    date: date

class Travel(BaseModel):
    """Model for a travel expense report."""
    id: Optional[int] = None
    employee_name: str = Field(..., example="Max Mustermann")
    cost_center: Optional[str] = Field(None, example="SALES-001")
    purpose: str = Field(..., example="Kundenbesuch bei ACME Corp")
    destination_city: str = Field(..., example="Berlin")
    destination_country: str = Field(..., example="Deutschland")
    start_at: date
    end_at: date
    transport_details: Optional[str] = Field(None, example="Flug LH202, Mietwagen")
    accommodation_details: Optional[str] = Field(None, example="Hotel InterContinental")
    notes: Optional[str] = None
    receipts: List[Receipt] = []
    total_expenses: Optional[float] = 0.0
    status: str = "draft"
