# Testing Guide

## Overview
The TravelExpense system has a comprehensive test suite to verify all functionality works correctly.

## Test Structure

```
tests/
├── integration/
│   ├── system_test.py           # Basic system health checks
│   └── full_integration_test.py # Complete integration testing
└── [other test files...]        # Unit tests
```

## Running Tests

### Quick Test
```bash
./run_tests.sh
```

### Individual Tests
```bash
# System health check
python3 tests/integration/system_test.py

# Full integration test
python3 tests/integration/full_integration_test.py
```

## What the Tests Verify

### System Test (`system_test.py`)
- ✅ Database connectivity and user data
- ✅ Backend API responsiveness
- ✅ Authentication for all user roles
- ✅ Admin dashboard functionality

### Integration Test (`full_integration_test.py`)
- ✅ Database consistency across all roles
- ✅ User authentication for admin, controller, employee
- ✅ Employee creation flow (admin creates → employee can login)
- ✅ Admin dashboard access and data retrieval

## Key Confirmations

The integration tests specifically verify:

1. **Single Database**: All roles (admin, controller, employee) use the same `app.db` SQLite database
2. **Account Creation**: When admin creates an employee, that employee account is immediately accessible with the provided credentials
3. **Role-based Access**: Each role can authenticate and access appropriate endpoints
4. **Data Consistency**: All user data is properly stored and retrievable

## Prerequisites

Before running tests:
1. Backend must be running (`./run_local.sh start`)
2. Database must be initialized with demo data
3. Admin user must exist with credentials `admin@demo.com` / `admin123`

## Expected Output

Successful test run should show:
```
✅ All integration tests passed!
✅ CONFIRMED: All roles use the same database
✅ CONFIRMED: Admin-created employees can login with credentials
✅ CONFIRMED: Authentication works for all user roles
```
