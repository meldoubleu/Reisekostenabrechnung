# TravelExpense System - Receipt Parsing Enhancement

## 🚀 **NEW: Automatic Receipt Parsing Implementation**

The system has been enhanced to automatically parse receipt images/PDFs into structured data instead of just storing raw files.

### ✅ **Database Schema Updates**

#### Enhanced Receipt Model
```python
class Receipt(Base):
    # File handling - optional/temporary for parsing
    file_path: Optional[str]          # Temporary file storage
    original_filename: Optional[str]   # Original upload filename
    file_size: Optional[int]          # File size in bytes
    mime_type: Optional[str]          # MIME type (image/jpeg, application/pdf)
    
    # Parsed receipt data (core fields)
    amount: Optional[float]           # Total amount
    currency: Optional[str]           # Currency (default: EUR)
    date: Optional[datetime]          # Receipt date
    vat: Optional[float]              # VAT amount
    vat_rate: Optional[float]         # VAT percentage (19%, 7%, etc.)
    merchant: Optional[str]           # Merchant/vendor name
    category: Optional[ExpenseCategory] # Auto-categorized expense type
    
    # Additional parsed fields
    invoice_number: Optional[str]     # Invoice/receipt number
    payment_method: Optional[str]     # cash, card, bank_transfer
    merchant_address: Optional[str]   # Merchant address
    merchant_tax_id: Optional[str]    # Tax ID/VAT number
    
    # Parsing metadata
    parsing_status: str               # pending, success, failed, manual
    parsing_confidence: float         # 0-100% confidence score
    parsed_at: Optional[datetime]     # When parsing was completed
    ocr_text: Optional[str]           # Raw OCR output for debugging
    
    # User verification
    verified: bool                    # User confirmed data is correct
    notes: Optional[str]              # User notes
    created_at: datetime              # Creation timestamp
    updated_at: Optional[datetime]    # Last update timestamp
```

### ✅ **Receipt Parsing Service**

#### Automatic Data Extraction
- **OCR Text Extraction**: From images (PNG, JPG) and PDFs
- **Field Parsing**: Regex-based extraction of structured data
- **Auto-Categorization**: Intelligent categorization based on merchant/content
- **Confidence Scoring**: Quality assessment of parsed data

#### Supported Fields
| Field | Description | Example |
|-------|-------------|---------|
| `amount` | Total amount | 87.50 |
| `vat` | VAT amount | 14.01 |
| `vat_rate` | VAT percentage | 19.0 |
| `merchant` | Vendor name | "Hotel Berlin" |
| `date` | Receipt date | "2024-01-15" |
| `invoice_number` | Receipt/invoice number | "2024-001234" |
| `payment_method` | Payment type | "ec_karte" |
| `category` | Auto-categorized type | "lodging" |

#### Auto-Categorization Rules
- **Lodging**: hotel, hostel, pension, übernachtung, zimmer
- **Transport**: bahn, flug, airline, taxi, uber, bus, ticket
- **Meals**: restaurant, café, bar, pizza, burger, bistro
- **Entertainment**: kino, theater, museum, event, konzert
- **Other**: Default fallback category

### ✅ **Enhanced API Workflow**

#### Receipt Upload & Parsing
```http
POST /api/v1/travels/{travel_id}/receipts
Content-Type: multipart/form-data

# Automatically:
# 1. Saves file temporarily
# 2. Extracts text via OCR
# 3. Parses structured data
# 4. Auto-categorizes expense
# 5. Calculates confidence score
# 6. Stores parsed data in database
# 7. (Optionally) Removes original file
```

#### Response Format
```json
{
  "id": 1,
  "travel_id": 29,
  "amount": 87.50,
  "currency": "EUR",
  "vat": 14.01,
  "vat_rate": 19.0,
  "merchant": "Hotel Berlin",
  "category": "lodging",
  "date": "2024-01-15T00:00:00",
  "invoice_number": "2024-001234",
  "payment_method": "ec_karte",
  "parsing_status": "success",
  "parsing_confidence": 95.5,
  "verified": false,
  "created_at": "2024-01-15T14:30:00"
}
```

### ✅ **Updated Schemas**

#### New Schema Types
- `ReceiptParsed`: For parsed data from OCR/AI
- `ReceiptCreate`: For manual receipt entry
- `ReceiptUpdate`: For editing parsed/manual data

#### Enhanced Receipt Schema
- Added all parsing-related fields
- File metadata fields
- Parsing status and confidence
- User verification flags

### ✅ **Parsing Algorithm**

#### Text Extraction Patterns
```python
# Amount extraction
amount_pattern = r'(?:gesamt|total|summe)[:\s]*([0-9,]+[.,][0-9]{2})'

# VAT extraction  
vat_pattern = r'mwst[.\s]*([0-9]+)%[:\s]*([0-9,]+[.,][0-9]{2})'

# Date extraction
date_pattern = r'datum[:\s]*([0-9]{1,2}[./][0-9]{1,2}[./][0-9]{2,4})'

# Invoice number
invoice_pattern = r'(?:rechnung|invoice|nr)[.\s#]*([a-z0-9-]+)'
```

#### Confidence Calculation
- Base confidence: 30% for any parsed data
- Amount found: +25%
- Merchant found: +20%  
- Date found: +15%
- VAT found: +10%
- Text quality indicators: +5%

### ✅ **File Management Strategy**

#### Options for File Storage
1. **Parse & Delete**: Extract data, remove original file (recommended)
2. **Parse & Archive**: Extract data, move file to archive storage
3. **Parse & Keep**: Extract data, keep file for verification

#### Current Implementation
- Files temporarily stored in `uploads/` directory
- OCR processing extracts structured data
- Original files kept for debugging/verification
- Future: Configurable file retention policy

### ✅ **Testing**

#### Parsing Service Tests
- Text extraction accuracy
- Auto-categorization logic
- Confidence calculation
- Error handling for poor OCR quality

#### Integration Tests
- Upload → Parse → Store workflow
- Multiple file format support
- Error scenarios and fallbacks

### 🔮 **Future Enhancements**

#### Advanced OCR Integration
- Cloud OCR services (Google Vision, AWS Textract)
- Tesseract OCR integration
- Multi-language support

#### AI-Powered Parsing
- Machine learning for better field extraction
- Context-aware categorization
- Merchant recognition database

#### Real-time Processing
- Background job processing for large files
- Webhook notifications for parsing completion
- Bulk processing capabilities

---

**Status**: ✅ Database schema updated, parsing service implemented, API enhanced
**Next**: Integration testing with real receipt images, OCR service integration
