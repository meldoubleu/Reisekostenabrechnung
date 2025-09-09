#!/usr/bin/env bash
# Enhanced test runner for role-based and API endpoint testing

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}${BOLD}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Parse command line arguments
TEST_TYPE="all"
COVERAGE="false"
VERBOSE="false"
ROLE=""
API_GROUP=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --role-employee|-re)
            TEST_TYPE="role"
            ROLE="employee"
            shift
            ;;
        --role-controller|-rc)
            TEST_TYPE="role"
            ROLE="controller"
            shift
            ;;
        --role-admin|-ra)
            TEST_TYPE="role"
            ROLE="admin"
            shift
            ;;
        --api-auth|-aa)
            TEST_TYPE="api"
            API_GROUP="auth"
            shift
            ;;
        --api-travel|-at)
            TEST_TYPE="api"
            API_GROUP="travel"
            shift
            ;;
        --api-user|-au)
            TEST_TYPE="api"
            API_GROUP="user"
            shift
            ;;
        --api-admin|-aad)
            TEST_TYPE="api"
            API_GROUP="admin"
            shift
            ;;
        --unit|-u)
            TEST_TYPE="unit"
            shift
            ;;
        --integration|-i)
            TEST_TYPE="integration"
            shift
            ;;
        --e2e|-e)
            TEST_TYPE="e2e"
            shift
            ;;
        --coverage|-c)
            COVERAGE="true"
            shift
            ;;
        --verbose|-v)
            VERBOSE="true"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Test Type Options:"
            echo "  -u,  --unit           Run only unit tests"
            echo "  -i,  --integration    Run only integration tests"
            echo "  -e,  --e2e           Run only end-to-end tests"
            echo ""
            echo "Role-based Options:"
            echo "  -re, --role-employee  Run employee role tests"
            echo "  -rc, --role-controller Run controller role tests"
            echo "  -ra, --role-admin     Run admin role tests"
            echo ""
            echo "API Endpoint Options:"
            echo "  -aa, --api-auth       Run authentication API tests"
            echo "  -at, --api-travel     Run travel API tests"
            echo "  -au, --api-user       Run user API tests"
            echo "  -aad,--api-admin      Run admin API tests"
            echo ""
            echo "General Options:"
            echo "  -c,  --coverage       Generate coverage report"
            echo "  -v,  --verbose        Verbose output"
            echo "  -h,  --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all tests"
            echo "  $0 --role-employee    # Run only employee role tests"
            echo "  $0 --api-auth         # Run only auth API tests"
            echo "  $0 --integration -c   # Run integration tests with coverage"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_header "🧪 TravelExpense Role-Based & API Test Suite"
echo "=============================================="

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    print_success "Virtual environment activated"
else
    print_warning "Virtual environment not found, using system Python"
fi

# Check if backend is running for integration/e2e tests
if [[ "$TEST_TYPE" == "integration" || "$TEST_TYPE" == "e2e" || "$TEST_TYPE" == "all" || "$TEST_TYPE" == "role" || "$TEST_TYPE" == "api" ]]; then
    if ! curl -s "http://localhost:8000/" > /dev/null 2>&1; then
        print_warning "Backend not running. Starting backend for tests..."
        ./scripts/run_local.sh start &
        BACKEND_PID=$!
        sleep 5
        if ! curl -s "http://localhost:8000/" > /dev/null 2>&1; then
            print_error "Failed to start backend. Please start manually with ./run_local.sh"
            exit 1
        fi
        print_success "Backend started for testing"
        CLEANUP_BACKEND=true
    else
        print_success "Backend is already running"
        CLEANUP_BACKEND=false
    fi
fi

# Prepare pytest arguments
PYTEST_ARGS=""

if [[ "$VERBOSE" == "true" ]]; then
    PYTEST_ARGS="$PYTEST_ARGS -v"
fi

if [[ "$COVERAGE" == "true" ]]; then
    PYTEST_ARGS="$PYTEST_ARGS --cov=backend --cov-report=html --cov-report=term-missing --cov-report=xml"
fi

# Run tests based on type and filters
case $TEST_TYPE in
    "unit")
        print_header "🔧 Running Unit Tests"
        pytest tests/ -m "unit" $PYTEST_ARGS
        ;;
    "integration")
        print_header "🔗 Running Integration Tests"
        pytest tests/ -m "integration" $PYTEST_ARGS
        ;;
    "e2e")
        print_header "🎯 Running End-to-End Tests"
        pytest tests/ -m "e2e" $PYTEST_ARGS
        ;;
    "role")
        case $ROLE in
            "employee")
                print_header "👤 Running Employee Role Tests"
                pytest tests/role_based/test_employee_complete.py $PYTEST_ARGS
                ;;
            "controller")
                print_header "👨‍💼 Running Controller Role Tests"
                pytest tests/role_based/test_controller_complete.py $PYTEST_ARGS
                ;;
            "admin")
                print_header "👨‍💻 Running Admin Role Tests"
                pytest tests/role_based/test_admin_complete.py $PYTEST_ARGS
                ;;
        esac
        ;;
    "api")
        case $API_GROUP in
            "auth")
                print_header "🔐 Running Authentication API Tests"
                pytest tests/api_coverage/test_all_endpoints.py::TestAuthEndpoints $PYTEST_ARGS
                ;;
            "travel")
                print_header "✈️ Running Travel API Tests"
                pytest tests/api_coverage/test_all_endpoints.py::TestTravelEndpoints $PYTEST_ARGS
                ;;
            "user")
                print_header "👥 Running User API Tests"
                pytest tests/api_coverage/test_all_endpoints.py::TestUserEndpoints $PYTEST_ARGS
                ;;
            "admin")
                print_header "🛡️ Running Admin API Tests"
                pytest tests/api_coverage/test_all_endpoints.py::TestAdminEndpoints $PYTEST_ARGS
                ;;
        esac
        ;;
    "all")
        print_header "🧪 Running Complete Test Suite"
        echo ""
        
        print_info "Running Role-based Tests..."
        echo ""
        
        print_info "👤 Employee Role Tests..."
        pytest tests/role_based/test_employee_complete.py $PYTEST_ARGS || true
        echo ""
        
        print_info "👨‍💼 Controller Role Tests..."
        pytest tests/role_based/test_controller_complete.py $PYTEST_ARGS || true
        echo ""
        
        print_info "👨‍💻 Admin Role Tests..."
        pytest tests/role_based/test_admin_complete.py $PYTEST_ARGS || true
        echo ""
        
        print_info "Running API Endpoint Coverage Tests..."
        pytest tests/api_coverage/test_all_endpoints.py $PYTEST_ARGS || true
        echo ""
        
        print_info "Running Legacy Test Suite..."
        pytest tests/ -m "not (unit or integration or e2e)" --ignore=tests/role_based --ignore=tests/api_coverage $PYTEST_ARGS || true
        ;;
esac

# Cleanup if we started the backend
if [[ "$CLEANUP_BACKEND" == "true" ]]; then
    print_info "Stopping test backend..."
    kill $BACKEND_PID 2>/dev/null || true
    sleep 2
fi

# Show coverage report location if generated
if [[ "$COVERAGE" == "true" ]]; then
    echo ""
    print_success "Coverage report generated:"
    print_info "HTML: htmlcov/index.html"
    print_info "XML: coverage.xml"
fi

echo ""
print_success "Test suite completed!"

# Deactivate virtual environment
if [ -f ".venv/bin/activate" ]; then
    deactivate
fi
