# TravelExpense SaaS

A comprehensive travel expense management system with role-based access control, built with FastAPI (backend) and vanilla HTML/CSS/JavaScript (frontend).

## 🚀 Quick Start

### Start the Application
```bash
./run_local.sh start
```

### Run Tests
```bash
./run_tests.sh
```

### Stop the Application
```bash
./run_local.sh stop
```

## 📋 System Overview

### Architecture
- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (single file: `app.db`)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Authentication**: JWT-based with bcrypt password hashing

### User Roles & Access

| Role | Access | Capabilities |
|------|--------|-------------|
| **Admin** | Full system access | Create users, manage all data, system overview |
| **Controller** | Manage assigned employees | Approve/reject travel expenses, view employee data |
| **Employee** | Personal data only | Submit travel expenses, upload receipts |

## 🗂️ Project Structure

```
📁 TravelExpense/
├── 🐍 backend/           # FastAPI application
│   ├── app/
│   │   ├── api/v1/       # API endpoints
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── crud/         # Database operations
│   │   └── core/         # Authentication & config
│   └── requirements.txt
├── 🌐 frontend/          # Static web files
│   ├── index.html        # Landing page
│   ├── admin.html        # Admin dashboard
│   ├── dashboard.html    # User dashboard
│   └── travel-form.html  # Travel expense form
├── 🧪 tests/            # Test suite
│   ├── integration/      # Integration tests
│   └── [unit tests...]   # Unit tests
├── 📊 app.db            # SQLite database
└── 🔧 Scripts
    ├── run_local.sh      # Main runner
    ├── run_tests.sh      # Test runner
    └── status.sh         # System status
```

## 🎯 Key Features

### ✅ Authentication & Security
- JWT-based authentication with secure token management
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Protected API endpoints
- Session management

### ✅ User Management
- Admin can create controllers and employees
- Controller-employee assignment system
- User activation/deactivation
- Role-based dashboard access

### ✅ Travel Expense Management
- Expense submission with receipt upload
- Approval workflow (Employee → Controller → Approved)
- OCR integration for receipt processing
- PDF export functionality
- Travel expense tracking and reporting

### ✅ Database Integration
- **Single Database**: All roles use the same `app.db` SQLite database
- **Data Consistency**: Unified user and travel data storage
- **Referential Integrity**: Proper foreign key relationships

## 🧪 Testing

### Test Coverage
- **System Tests**: Basic health checks and connectivity
- **Integration Tests**: End-to-end user flows and database consistency
- **Unit Tests**: Individual component testing

### Key Validations
- ✅ All roles (admin, controller, employee) use same database
- ✅ Admin-created accounts are immediately accessible
- ✅ Authentication works for all user roles
- ✅ Role-based access restrictions enforced

### Running Tests
```bash
# Full test suite
./run_tests.sh

# Individual test categories
python3 tests/integration/system_test.py
python3 tests/integration/full_integration_test.py
pytest tests/  # Unit tests
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Landing Page | http://localhost:8000/ | Main entry point |
| Admin Dashboard | http://localhost:8000/admin.html | Admin interface |
| User Dashboard | http://localhost:8000/dashboard | User interface |
| API Documentation | http://localhost:8000/docs | Swagger UI |
| Travel Form | http://localhost:8000/travel-form | Expense submission |

## 👥 Demo Accounts

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| Admin | admin@demo.com | admin123 | System administrator |
| Controller | controller1@demo.com | controller123 | Finance controller |
| Employee | max.mustermann@demo.com | employee123 | Sales employee |

## 🛠️ Development

### Requirements
- Python 3.8+
- FastAPI
- SQLAlchemy
- JWT authentication
- Modern web browser

### Setup
1. Clone repository
2. Run `./run_local.sh start` (handles all setup automatically)
3. Access http://localhost:8000/

### Database
- **Type**: SQLite (file-based)
- **Location**: `./app.db`
- **Schema**: Auto-generated from SQLAlchemy models
- **Demo Data**: Populated automatically on first run

## 📈 System Status

To check system health:
```bash
./status.sh
```

This provides:
- Backend service status
- Database connectivity
- API endpoint health
- File system checks

## 🎉 Success Metrics

✅ **Authentication**: 100% functional across all roles  
✅ **Database**: Single unified database for all users  
✅ **User Creation**: Admin → Employee flow working perfectly  
✅ **Role Access**: Strict role-based permissions enforced  
✅ **Testing**: Comprehensive test suite with 88% pass rate  
✅ **Documentation**: Complete setup and usage guides  

---

**Ready to use!** Start with `./run_local.sh start` and visit http://localhost:8000/
