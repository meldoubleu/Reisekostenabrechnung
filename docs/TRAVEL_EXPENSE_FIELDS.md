# Travel Expense Database Fields - Comprehensive Overview

## 📋 **CURRENT TRAVEL EXPENSE FIELDS (Implemented)**

Based on the existing database models and frontend form, here are the fields employees can fill out for travel expenses:

### **✈️ TRAVELS Table - Main Travel Request**

| Field | Type | Required | Purpose | Frontend Field |
|-------|------|----------|---------|----------------|
| **id** | INTEGER | ✅ | Unique identifier | Auto-generated |
| **employee_name** | VARCHAR(255) | ✅ | Employee name (legacy) | Auto-filled |
| **employee_id** | INTEGER | ❌ | User relationship | Auto-filled |
| **start_at** | DATETIME | ✅ | Travel start date/time | `trip-start` |
| **end_at** | DATETIME | ✅ | Travel end date/time | `trip-end` |
| **destination_city** | VARCHAR(255) | ✅ | Travel destination | `trip-destination` |
| **destination_country** | VARCHAR(255) | ✅ | Country of travel | `trip-destination` |
| **purpose** | TEXT | ✅ | Business purpose | `trip-purpose` |
| **cost_center** | VARCHAR(100) | ❌ | Budget allocation | Auto-filled |
| **status** | ENUM | ✅ | Approval workflow | Auto-managed |

**Status Workflow:**
```
draft → submitted → approved/rejected
```

**Purpose Options:**
- `business` - Geschäftlich
- `training` - Training  
- `conference` - Konferenz
- `customer` - Kundenbesuch

### **🧾 RECEIPTS Table - Individual Expenses**

| Field | Type | Required | Purpose | Frontend Handling |
|-------|------|----------|---------|-------------------|
| **id** | INTEGER | ✅ | Unique identifier | Auto-generated |
| **travel_id** | INTEGER | ✅ | Links to travel | Auto-assigned |
| **file_path** | VARCHAR(500) | ✅ | Receipt file location | File upload |
| **amount** | NUMERIC(12,2) | ❌ | Expense amount | `trip-costs` (estimated) |
| **currency** | VARCHAR(10) | ❌ | Currency code | `trip-currency` |
| **date** | DATETIME | ❌ | Expense date | Date picker |
| **vat** | NUMERIC(12,2) | ❌ | VAT amount | OCR extraction |
| **merchant** | VARCHAR(255) | ❌ | Vendor/merchant | OCR extraction |
| **category** | ENUM | ❌ | Expense type | Dropdown |
| **notes** | TEXT | ❌ | Additional details | Text area |

**Expense Categories:**
- `lodging` - Accommodation
- `transport` - Transportation  
- `meals` - Meals & dining
- `entertainment` - Business entertainment
- `other` - Other expenses

**Currency Options:**
- `EUR` - Euro
- `USD` - US Dollar
- `GBP` - British Pound

---

## 🔍 **MISSING/ADDITIONAL FIELDS (Recommended)**

For a complete travel expense system, consider adding these fields:

### **Enhanced Travel Fields**

| Field | Type | Purpose | Business Value |
|-------|------|---------|----------------|
| **advance_payment** | NUMERIC(12,2) | Company advance given | Financial tracking |
| **total_estimated_cost** | NUMERIC(12,2) | Budget estimation | Budget planning |
| **actual_total_cost** | NUMERIC(12,2) | Final expense total | Cost analysis |
| **accommodation_details** | TEXT | Hotel/lodging info | Audit trail |
| **transport_mode** | ENUM | Car/plane/train/etc | Policy compliance |
| **business_contacts** | TEXT | People met | Business justification |
| **approval_notes** | TEXT | Controller comments | Review documentation |
| **approved_by** | INTEGER | Controller ID | Audit trail |
| **approved_at** | DATETIME | Approval timestamp | Process tracking |
| **rejected_reason** | TEXT | Rejection explanation | Process improvement |

### **Enhanced Receipt Fields**

| Field | Type | Purpose | Business Value |
|-------|------|---------|----------------|
| **receipt_number** | VARCHAR(100) | Invoice/receipt number | Audit compliance |
| **tax_rate** | NUMERIC(5,2) | VAT percentage | Tax reporting |
| **reimbursable** | BOOLEAN | Company vs personal | Policy enforcement |
| **policy_compliant** | BOOLEAN | Meets company policy | Automatic validation |
| **exchange_rate** | NUMERIC(10,4) | Currency conversion | Multi-currency support |
| **payment_method** | ENUM | Cash/card/bank transfer | Expense tracking |

### **User Preference Fields**

| Field | Type | Purpose | Business Value |
|-------|------|---------|----------------|
| **preferred_currency** | VARCHAR(10) | Default currency | User experience |
| **default_cost_center** | VARCHAR(100) | Auto-fill budget | Efficiency |
| **expense_policy_version** | VARCHAR(20) | Policy compliance | Audit tracking |

---

## 📊 **CURRENT FRONTEND FORM MAPPING**

### **Travel Form Fields (frontend/travel-form.html)**

```html
<!-- Basic Travel Information -->
<select name="trip-purpose">          → travels.purpose
<input name="trip-destination">       → travels.destination_city + destination_country  
<input type="date" name="trip-start"> → travels.start_at
<input type="date" name="trip-end">   → travels.end_at
<input name="trip-costs">             → estimated total (not stored directly)
<select name="trip-currency">         → receipts.currency (default)

<!-- Receipt Upload -->
<input type="file" name="receipt-files[]"> → receipts.file_path
```

### **Data Flow:**
1. **Employee** fills out travel form
2. **System** creates `travels` record with status='draft'
3. **Employee** uploads receipts → creates `receipts` records
4. **Employee** submits → status='submitted'
5. **Controller** reviews → status='approved/rejected'

---

## 🔧 **RECOMMENDED ENHANCEMENTS**

### **1. Add Missing Core Fields**
```sql
ALTER TABLE travels ADD COLUMN advance_payment NUMERIC(12,2);
ALTER TABLE travels ADD COLUMN total_estimated_cost NUMERIC(12,2); 
ALTER TABLE travels ADD COLUMN actual_total_cost NUMERIC(12,2);
ALTER TABLE travels ADD COLUMN approved_by INTEGER REFERENCES users(id);
ALTER TABLE travels ADD COLUMN approved_at DATETIME;
```

### **2. Enhance Receipt Tracking**
```sql
ALTER TABLE receipts ADD COLUMN receipt_number VARCHAR(100);
ALTER TABLE receipts ADD COLUMN tax_rate NUMERIC(5,2);
ALTER TABLE receipts ADD COLUMN reimbursable BOOLEAN DEFAULT TRUE;
ALTER TABLE receipts ADD COLUMN payment_method VARCHAR(20);
```

### **3. Add Travel Categories**
```sql
CREATE TYPE transport_mode AS ENUM ('car', 'plane', 'train', 'bus', 'other');
ALTER TABLE travels ADD COLUMN transport_mode transport_mode;
```

---

## 🎯 **BUSINESS REQUIREMENTS COVERAGE**

| Requirement | Current Status | Implementation |
|-------------|----------------|----------------|
| **Basic travel request** | ✅ Complete | travels table + form |
| **Receipt upload** | ✅ Complete | receipts table + file upload |
| **Approval workflow** | ✅ Complete | status enum + controller review |
| **Multi-currency support** | ✅ Partial | currency field exists |
| **Expense categorization** | ✅ Complete | category enum |
| **Budget tracking** | ⚠️ Partial | cost_center exists |
| **Advance payments** | ❌ Missing | Needs enhancement |
| **Policy compliance** | ❌ Missing | Needs enhancement |
| **Audit trail** | ⚠️ Partial | Basic tracking exists |

---

## 📋 **SUMMARY**

The current travel expense system has **solid core functionality** with these key fields:

### **✅ Well Implemented:**
- Basic travel request (dates, destination, purpose)
- Receipt file upload and storage
- Approval workflow (draft → submitted → approved/rejected)
- Expense categorization (lodging, transport, meals, etc.)
- Multi-currency support
- User-travel-receipt relationships

### **⚠️ Areas for Enhancement:**
- Financial tracking (advance payments, totals)
- Enhanced audit trail (approval timestamps, notes)
- Policy compliance validation
- Advanced receipt metadata (tax rates, payment methods)
- Reporting and analytics fields

The current implementation provides a **functional MVP** for travel expense management that covers the essential employee workflow of creating travel requests, uploading receipts, and obtaining approvals.
