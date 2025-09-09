# Restructured Test Suite Documentation

## 📁 New Test Organization

The test suite has been completely restructured to provide comprehensive coverage organized by roles and API endpoints.

### Directory Structure
```
tests/
├── conftest.py                    # Shared test configuration and fixtures
├── pytest_config.py              # Test configuration
├── role_based/                   # Role-based comprehensive tests
│   ├── test_employee_complete.py # Complete employee role test suite
│   ├── test_controller_complete.py # Complete controller role test suite
│   └── test_admin_complete.py    # Complete admin role test suite
├── api_coverage/                 # API endpoint coverage tests
│   └── test_all_endpoints.py     # Tests for all API endpoints
├── unit/                         # Unit tests (isolated components)
├── integration/                  # Integration tests (component interactions)
├── legacy/                       # Previous test files (preserved)
└── test_data/                   # Test data and fixtures
```

## 🎯 Test Categories

### Role-Based Tests
- **Employee Tests** (`test_employee_complete.py`)
  - Authentication (login, get user info)
  - Travel management (create, update, submit travels)
  - Receipt management (upload receipts)
  - Access restrictions (cannot access admin/controller endpoints)
  - Complete workflow testing

- **Controller Tests** (`test_controller_complete.py`) 
  - Authentication and user info
  - Team management (view assigned employees)
  - Travel approval/rejection workflows
  - Employee travel oversight
  - Access restrictions (cannot access admin-only endpoints)
  - Complete workflow testing

- **Admin Tests** (`test_admin_complete.py`)
  - Full system dashboard access
  - User management (create, update, delete users)
  - Controller and employee creation
  - Assignment management (assign employees to controllers)
  - System-wide travel access
  - Complete administrative workflow testing

### API Endpoint Coverage Tests
- **Authentication Endpoints** (`TestAuthEndpoints`)
  - POST `/api/v1/auth/login`
  - POST `/api/v1/auth/register`
  - GET `/api/v1/auth/me`

- **Travel Endpoints** (`TestTravelEndpoints`)
  - POST `/api/v1/travels/` (create travel)
  - GET `/api/v1/travels/` (list travels)
  - GET `/api/v1/travels/my` (employee's travels)
  - GET `/api/v1/travels/assigned` (controller's assigned travels)
  - GET `/api/v1/travels/{id}` (get specific travel)
  - PUT `/api/v1/travels/{id}` (update travel)
  - POST `/api/v1/travels/{id}/receipts` (upload receipts)
  - POST `/api/v1/travels/{id}/submit` (submit for approval)
  - PUT `/api/v1/travels/{id}/approve` (approve travel)
  - PUT `/api/v1/travels/{id}/reject` (reject travel)
  - GET `/api/v1/travels/{id}/export` (export travel data)
  - GET `/api/v1/travels/{id}/receipts` (get receipts)
  - GET `/api/v1/travels/employee/{id}/travels` (employee travels)
  - GET `/api/v1/travels/controller/{id}/travels` (controller travels)

- **User Management Endpoints** (`TestUserEndpoints`)
  - POST `/api/v1/users/` (create user)
  - GET `/api/v1/users/` (list users)
  - GET `/api/v1/users/controllers` (list controllers)
  - GET `/api/v1/users/my-team` (controller's team)
  - GET `/api/v1/users/{id}` (get user by ID)
  - GET `/api/v1/users/email/{email}` (get user by email)
  - PUT `/api/v1/users/{id}` (update user)
  - PUT `/api/v1/users/{employee_id}/assign-controller/{controller_id}` (assign)
  - GET `/api/v1/users/controller/{id}/employees` (controller's employees)
  - DELETE `/api/v1/users/{id}` (delete user)

- **Admin Endpoints** (`TestAdminEndpoints`)
  - GET `/api/v1/admin/dashboard` (admin dashboard)
  - POST `/api/v1/admin/controllers` (create controller)
  - POST `/api/v1/admin/employees` (create employee)
  - PUT `/api/v1/admin/assign-employee/{employee_id}/to-controller/{controller_id}`
  - PUT `/api/v1/admin/unassign-employee/{employee_id}`
  - DELETE `/api/v1/admin/users/{id}` (delete user)
  - GET `/api/v1/admin/controller-assignments` (view assignments)
  - GET `/api/v1/admin/travels` (all travels)

- **Page Endpoints** (`TestPageEndpoints`)
  - GET `/api/v1/` (landing page)
  - GET `/api/v1/landingpage`
  - GET `/api/v1/dashboard`
  - GET `/api/v1/travel-form`
  - GET `/api/v1/ui`
  - GET `/api/v1/debug`
  - GET `/api/v1/admin`

## 🚀 Enhanced Test Runner

Use the new test runner script for targeted testing:

```bash
# Run all role-based tests
./scripts/run_tests_restructured.sh

# Run specific role tests
./scripts/run_tests_restructured.sh --role-employee
./scripts/run_tests_restructured.sh --role-controller  
./scripts/run_tests_restructured.sh --role-admin

# Run specific API tests
./scripts/run_tests_restructured.sh --api-auth
./scripts/run_tests_restructured.sh --api-travel
./scripts/run_tests_restructured.sh --api-user
./scripts/run_tests_restructured.sh --api-admin

# Run by test type
./scripts/run_tests_restructured.sh --unit
./scripts/run_tests_restructured.sh --integration
./scripts/run_tests_restructured.sh --e2e

# Generate coverage reports
./scripts/run_tests_restructured.sh --coverage
./scripts/run_tests_restructured.sh --role-employee --coverage
```

## 🏷️ Test Markers

Tests are marked with the following pytest markers:

- `@pytest.mark.unit` - Unit tests (isolated components)
- `@pytest.mark.integration` - Integration tests (component interactions)
- `@pytest.mark.e2e` - End-to-end tests (complete workflows)
- `@pytest.mark.role_employee` - Employee role tests
- `@pytest.mark.role_controller` - Controller role tests
- `@pytest.mark.role_admin` - Admin role tests
- `@pytest.mark.api_auth` - Authentication API tests
- `@pytest.mark.api_travel` - Travel API tests
- `@pytest.mark.api_user` - User API tests
- `@pytest.mark.api_admin` - Admin API tests

## 🔧 Configuration

- **pytest.ini**: Updated with new markers and test paths
- **conftest.py**: Shared fixtures and test configuration
- Test fixtures automatically handle user authentication and setup
- Backend auto-start for integration tests

## ✅ Coverage Goals

The restructured test suite ensures:
- **100% API endpoint coverage** - All endpoints tested
- **Complete role-based testing** - Every role's capabilities tested
- **Security testing** - Access restrictions verified
- **Workflow testing** - End-to-end user journeys tested
- **Error handling** - Invalid inputs and edge cases covered

## 📊 Test Execution

Run the complete test suite to verify:
1. All API endpoints are accessible and functional
2. Role-based access control works correctly
3. Complete user workflows function end-to-end
4. Security restrictions are properly enforced
5. Data validation and business logic work correctly

The restructured test suite provides comprehensive coverage while maintaining clear organization and easy maintenance.
