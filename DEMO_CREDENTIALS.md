# TravelExpense Demo User Credentials

## 🔑 Admin Users
| Email | Password | Name | Department |
|-------|----------|------|------------|
| `admin@demo.com` | `admin123` | System Administrator | IT |

**Admin Access:**
- Full system administration
- Create/manage all users
- Access all data and reports
- System configuration

---

## 👔 Controller Users
| Email | Password | Name | Department | Assigned Employees |
|-------|----------|------|------------|-------------------|
| `controller1@demo.com` | `controller123` | Anna Controlling | Finance | Max Mustermann, Malte, test employee |
| `controller2@demo.com` | `controller123` | Thomas Controller | Management | Lisa Müller, Michael Weber |

**Controller Access:**
- Manage assigned employees
- Approve/reject travel expenses
- View employee expense reports
- Limited administrative functions

**Note:** The controller dashboard shows real employee data fetched from the database based on controller-employee assignments.

---

## 👨‍💼 Employee Users
| Email | Password | Name | Department | Cost Center |
|-------|----------|------|------------|-------------|
| `max.mustermann@demo.com` | `employee123` | Max Mustermann | Sales | SALES-001 |
| `sarah.schmidt@demo.com` | `employee123` | Sarah Schmidt | Marketing | MKT-002 |
| `michael.weber@demo.com` | `employee123` | Michael Weber | Development | DEV-003 |
| `lisa.mueller@demo.com` | `employee123` | Lisa Müller | HR | HR-004 |
| `malte@demo.com` | `employee123` | Malte | Software | Jesus123 |
| `integration.test@demo.com` | `employee123` | Integration Test Employee | Testing | TEST-001 |
| `test.employee@demo.com` | `employee123` | Test Employee | Testing | TEST-001 |
| `newuser@test.com` | `employee123` | New User | General | N/A |
| `test123@test.com` | `employee123` | test employee | test | test |

**Employee Access:**
- Submit travel expense requests
- Upload receipts and documents
- View personal expense history
- Edit draft expenses

---

## 🚀 Quick Access (Recommended Demo Accounts)

### For Testing Admin Features:
```
Email: admin@demo.com
Password: admin123
```

### For Testing Controller Features:
```
Email: controller1@demo.com
Password: controller123
```

### For Testing Employee Features:
```
Email: max.mustermann@demo.com
Password: employee123
```

---

## 🌐 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Main Landing** | http://localhost:8000/ | Entry point with login |
| **Admin Dashboard** | http://localhost:8000/admin.html | Admin interface |
| **User Dashboard** | http://localhost:8000/dashboard | Controller/Employee interface |
| **Test Login** | http://localhost:8000/test-login.html | Debug login page |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |

---

## 📝 Password Pattern

All passwords follow a consistent pattern:
- **Admin**: `admin123`
- **Controllers**: `controller123`
- **Employees**: `employee123`

---

## ✅ Database Confirmation

- **Single Database**: All users stored in `app.db` SQLite database
- **Unified Authentication**: All roles use the same authentication system
- **Data Consistency**: All user data accessible across the system
- **Account Creation**: Admin-created accounts immediately accessible

---

## 🔧 System Management

### Start System (Recommended - Fast):
```bash
./run_local.sh
```

### Start Options:
```bash
./run_local.sh start --quick     # Fast startup with minimal tests (default)
./run_local.sh start --no-tests  # Fastest startup, skip all tests
./run_local.sh start --full      # Complete startup with all 188 tests
```

### Test Credentials:
```bash
./run_tests.sh            # Run all tests manually
./run_local.sh test        # Full test suite via run_local.sh
```

### Check Status:
```bash
./status.sh
```

---

*Last Updated: September 5, 2025*
*Total Users: 13 (1 Admin, 3 Controllers, 9 Employees)*
