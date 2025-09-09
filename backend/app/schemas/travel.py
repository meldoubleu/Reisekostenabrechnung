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
    # Core parsed fields
    amount: Optional[float] = None
    currency: Optional[str] = "EUR"
    date: Optional[datetime] = None
    vat: Optional[float] = None
    vat_rate: Optional[float] = None
    merchant: Optional[str] = None
    category: Optional[ExpenseCategory] = None
    
    # Additional parsed fields
    invoice_number: Optional[str] = None
    payment_method: Optional[str] = None
    merchant_address: Optional[str] = None
    merchant_tax_id: Optional[str] = None
    
    # User fields
    notes: Optional[str] = None
    verified: Optional[bool] = False


class ReceiptCreate(ReceiptBase):
    """Schema for creating new receipts (mainly for manual entry)."""
    pass


class ReceiptUpdate(ReceiptBase):
    """Schema for updating receipt categorization and details."""
    pass


class ReceiptParsed(BaseModel):
    """Schema for parsed receipt data from OCR/AI processing."""
    # Core parsed fields (required from parsing)
    amount: Optional[float] = None
    currency: str = "EUR"
    date: Optional[datetime] = None
    vat: Optional[float] = None
    vat_rate: Optional[float] = None
    merchant: Optional[str] = None
    category: Optional[ExpenseCategory] = None
    
    # Additional parsed fields
    invoice_number: Optional[str] = None
    payment_method: Optional[str] = None
    merchant_address: Optional[str] = None
    merchant_tax_id: Optional[str] = None
    
    # Parsing metadata
    parsing_confidence: Optional[float] = None
    ocr_text: Optional[str] = None


class Receipt(ReceiptBase):
    id: int
    travel_id: int
    
    # File metadata (optional after parsing)
    file_path: Optional[str] = None
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    
    # Parsing metadata
    parsing_status: Optional[str] = None
    parsing_confidence: Optional[float] = None
    parsed_at: Optional[datetime] = None
    ocr_text: Optional[str] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TravelBase(BaseModel):
    employee_name: str = Field(...)
    # Legacy fields (for backward compatibility)
    start_at: datetime
    end_at: datetime
    
    # Enhanced travel timeline fields
    departure_location: Optional[str] = None
    departure_timestamp: Optional[datetime] = None
    arrival_at_destination_timestamp: Optional[datetime] = None
    departure_from_destination_timestamp: Optional[datetime] = None
    arrival_home_timestamp: Optional[datetime] = None
    
    destination_city: str
    destination_country: str
    purpose: str
    total_expenses: Optional[float] = 0.0
    cost_center: Optional[str] = None
    status: TravelStatus = TravelStatus.draft


class TravelCreate(TravelBase):
    # Optional employee_id for new relationship-based travel creation
    employee_id: Optional[int] = None
    
    @model_validator(mode='after')
    def validate_travel_timeline(self):
        """Validate travel timeline logic."""
        # Legacy validation: end_at must be after start_at
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValueError("End date must be after start date")
        
        # Enhanced timeline validation
        timestamps = []
        if self.departure_timestamp:
            timestamps.append(('departure', self.departure_timestamp))
        if self.arrival_at_destination_timestamp:
            timestamps.append(('arrival_at_destination', self.arrival_at_destination_timestamp))
        if self.departure_from_destination_timestamp:
            timestamps.append(('departure_from_destination', self.departure_from_destination_timestamp))
        if self.arrival_home_timestamp:
            timestamps.append(('arrival_home', self.arrival_home_timestamp))
        
        # Sort by timestamp to validate chronological order
        timestamps.sort(key=lambda x: x[1])
        
        # Validate logical sequence
        if len(timestamps) >= 2:
            for i in range(len(timestamps) - 1):
                if timestamps[i][1] >= timestamps[i + 1][1]:
                    raise ValueError(f"Travel timeline error: {timestamps[i][0]} must be before {timestamps[i + 1][0]}")
        
        # Validate that arrival at destination comes before departure from destination
        if (self.arrival_at_destination_timestamp and self.departure_from_destination_timestamp and 
            self.arrival_at_destination_timestamp >= self.departure_from_destination_timestamp):
            raise ValueError("Arrival at destination must be before departure from destination")
        
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
