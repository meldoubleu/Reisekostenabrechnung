# TravelExpense Database Entity Relationship Model (ERM)

## 📊 **DATABASE OVERVIEW**

The TravelExpense SaaS application uses a **relational database** with **3 main entities** and **hierarchical relationships** for role-based access control.

---

## 🗂️ **ENTITY RELATIONSHIP DIAGRAM**

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAVELEXPENSE DATABASE ERM                   │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │                         USERS                               │
    │─────────────────────────────────────────────────────────────│
    │ PK  id: INTEGER                                             │
    │ UK  email: VARCHAR(255)                                     │
    │     name: VARCHAR(255)                                      │
    │     role: ENUM(employee, controller, admin)                 │
    │     company: VARCHAR(255)                                   │
    │     department: VARCHAR(100) [NULL]                         │
    │     cost_center: VARCHAR(100) [NULL]                        │
    │     is_active: BOOLEAN (DEFAULT: TRUE)                      │
    │     password_hash: VARCHAR(255) [NULL]                      │
    │ FK  controller_id: INTEGER [NULL] → users.id                │
    └─────────────────────────────────────────────────────────────┘
              │                                    ↑
              │                                    │
              │ 1:N (employees)                    │ N:1 (controller)
              │                                    │
              ↓                                    │
    ┌─────────────────────────────────────────────────────────────┐
    │                       TRAVELS                               │
    │─────────────────────────────────────────────────────────────│
    │ PK  id: INTEGER                                             │
    │     employee_name: VARCHAR(255) [LEGACY]                    │
    │ FK  employee_id: INTEGER [NULL] → users.id                  │
    │     start_at: DATETIME                                      │
    │     end_at: DATETIME                                        │
    │     destination_city: VARCHAR(255)                          │
    │     destination_country: VARCHAR(255)                       │
    │     purpose: TEXT                                           │
    │     cost_center: VARCHAR(100) [NULL]                        │
    │     status: ENUM(draft, submitted, approved, rejected)      │
    └─────────────────────────────────────────────────────────────┘
              │
              │ 1:N (receipts)
              │
              ↓
    ┌─────────────────────────────────────────────────────────────┐
    │                       RECEIPTS                              │
    │─────────────────────────────────────────────────────────────│
    │ PK  id: INTEGER                                             │
    │ FK  travel_id: INTEGER → travels.id                         │
    │     file_path: VARCHAR(500)                                 │
    │     amount: NUMERIC(12,2) [NULL]                            │
    │     currency: VARCHAR(10) [NULL]                            │
    │     date: DATETIME [NULL]                                   │
    │     vat: NUMERIC(12,2) [NULL]                               │
    │     merchant: VARCHAR(255) [NULL]                           │
    │     category: ENUM(lodging,transport,meals,entertainment,other) [NULL] │
    │     notes: TEXT [NULL]                                      │
    └─────────────────────────────────────────────────────────────┘
```

---

## 🔗 **RELATIONSHIPS**

### **1. Users ↔ Users (Self-Referencing)**
- **Type:** One-to-Many (1:N)
- **Description:** Controllers manage multiple employees
- **Implementation:** `controller_id` foreign key in users table
- **Constraint:** `FOREIGN KEY(controller_id) REFERENCES users(id)`

```sql
Controller (User with role='controller')
    ├── Employee 1 (controller_id = controller.id)
    ├── Employee 2 (controller_id = controller.id)
    └── Employee N (controller_id = controller.id)
```

### **2. Users ↔ Travels**
- **Type:** One-to-Many (1:N)
- **Description:** Each user (employee) can have multiple travel requests
- **Implementation:** `employee_id` foreign key in travels table
- **Note:** `employee_name` is kept for backward compatibility

```sql
User (Employee)
    ├── Travel 1 (employee_id = user.id)
    ├── Travel 2 (employee_id = user.id)
    └── Travel N (employee_id = user.id)
```

### **3. Travels ↔ Receipts**
- **Type:** One-to-Many (1:N)
- **Description:** Each travel can have multiple expense receipts
- **Implementation:** `travel_id` foreign key in receipts table
- **Constraint:** `FOREIGN KEY(travel_id) REFERENCES travels(id)`
- **Cascade:** DELETE CASCADE (receipts deleted when travel is deleted)

```sql
Travel
    ├── Receipt 1 (travel_id = travel.id)
    ├── Receipt 2 (travel_id = travel.id)
    └── Receipt N (travel_id = travel.id)
```

---

## 📋 **ENTITY DETAILS**

### **🧑‍💼 USERS Entity**

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEXED | User login credential |
| `name` | VARCHAR(255) | NOT NULL | User display name |
| `role` | ENUM | NOT NULL | Access control (employee/controller/admin) |
| `company` | VARCHAR(255) | NOT NULL | Company affiliation |
| `department` | VARCHAR(100) | NULLABLE | Department assignment |
| `cost_center` | VARCHAR(100) | NULLABLE | Budget allocation |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account status |
| `password_hash` | VARCHAR(255) | NULLABLE | Encrypted password |
| `controller_id` | INTEGER | FK, NULLABLE | Reports-to relationship |

**Role Hierarchy:**
- **Admin:** Full system access, manage all users and data
- **Controller:** Manage assigned employees, approve travel requests  
- **Employee:** Submit travel requests, view own data

### **✈️ TRAVELS Entity**

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique travel identifier |
| `employee_name` | VARCHAR(255) | NOT NULL | Legacy employee name |
| `employee_id` | INTEGER | FK, NULLABLE | User relationship |
| `start_at` | DATETIME | NOT NULL | Travel start date/time |
| `end_at` | DATETIME | NOT NULL | Travel end date/time |
| `destination_city` | VARCHAR(255) | NOT NULL | Travel destination |
| `destination_country` | VARCHAR(255) | NOT NULL | Travel country |
| `purpose` | TEXT | NOT NULL | Business purpose |
| `cost_center` | VARCHAR(100) | NULLABLE | Budget allocation |
| `status` | ENUM | NOT NULL, DEFAULT 'draft' | Approval workflow |

**Status Workflow:**
```
draft → submitted → approved/rejected
```

### **🧾 RECEIPTS Entity**

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique receipt identifier |
| `travel_id` | INTEGER | FK, NOT NULL, INDEXED | Travel association |
| `file_path` | VARCHAR(500) | NOT NULL | Receipt file location |
| `amount` | NUMERIC(12,2) | NULLABLE | Expense amount |
| `currency` | VARCHAR(10) | NULLABLE | Currency code |
| `date` | DATETIME | NULLABLE | Expense date |
| `vat` | NUMERIC(12,2) | NULLABLE | VAT amount |
| `merchant` | VARCHAR(255) | NULLABLE | Vendor name |
| `category` | ENUM | NULLABLE | Expense classification |
| `notes` | TEXT | NULLABLE | Additional details |

---

## 🔍 **DATABASE INDEXES**

```sql
-- Primary Keys (automatic indexes)
users.id, travels.id, receipts.id

-- Unique Constraints
users.email (UNIQUE)

-- Foreign Key Indexes  
travels.employee_id
receipts.travel_id

-- Additional Indexes
users.id, travels.id (explicit indexes)
```

---

## 🔐 **DATA RELATIONSHIPS & BUSINESS LOGIC**

### **Hierarchical User Management**
```
Admin
├── Controller 1
│   ├── Employee A (controller_id = 1)
│   ├── Employee B (controller_id = 1)
│   └── Employee C (controller_id = 1)
├── Controller 2  
│   ├── Employee D (controller_id = 2)
│   └── Employee E (controller_id = 2)
└── Unassigned Employees (controller_id = NULL)
```

### **Travel Request Flow**
```
Employee → Travel (draft) → Receipt uploads → Submit → Controller Review → Approve/Reject
```

### **Data Access Patterns**
- **Admin:** Access ALL users, travels, receipts
- **Controller:** Access assigned employees + their travels/receipts  
- **Employee:** Access only own travels/receipts

---

## 📊 **SAMPLE DATA STRUCTURE**

```sql
-- Users Table
users: [
  {id: 1, email: "controller1@demo.com", role: "controller", controller_id: NULL},
  {id: 3, email: "max.mustermann@demo.com", role: "employee", controller_id: 1},
  {id: 7, email: "admin@demo.com", role: "admin", controller_id: NULL}
]

-- Travels Table  
travels: [
  {id: 1, employee_id: 3, employee_name: "Max Mustermann", status: "submitted"},
  {id: 2, employee_id: 3, employee_name: "Max Mustermann", status: "draft"}
]

-- Receipts Table
receipts: [
  {id: 1, travel_id: 1, amount: 45.50, category: "meals", file_path: "/uploads/receipt1.pdf"},
  {id: 2, travel_id: 1, amount: 120.00, category: "lodging", file_path: "/uploads/receipt2.pdf"}
]
```

---

## 🏗️ **DESIGN PATTERNS**

1. **Self-Referencing Hierarchy:** Users table with controller_id foreign key
2. **Enum Constraints:** Role-based access and status workflows
3. **Soft References:** Legacy employee_name + new employee_id for migration
4. **Cascade Deletion:** Receipts deleted when travel is removed
5. **Optional Relationships:** Nullable foreign keys for flexibility

This ERM supports the TravelExpense SaaS application's role-based access control, travel expense management, and receipt tracking requirements.
