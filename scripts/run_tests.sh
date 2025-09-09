#!/usr/bin/env bash
# Comprehensive test runner for TravelExpense system

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

while [[ $# -gt 0 ]]; do
    case $1 in
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
            echo "Options:"
            echo "  -u, --unit         Run only unit tests"
            echo "  -i, --integration  Run only integration tests"
            echo "  -e, --e2e         Run only end-to-end tests"
            echo "  -c, --coverage     Generate coverage report"
            echo "  -v, --verbose      Verbose output"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Run all tests"
            echo "  $0 --unit --coverage # Run unit tests with coverage"
            echo "  $0 --e2e           # Run only end-to-end tests"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_header "🧪 TravelExpense Comprehensive Test Suite"
echo "=========================================="

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    print_success "Virtual environment activated"
else
    print_warning "Virtual environment not found, using system Python"
fi

# Check if backend is running for integration/e2e tests
if [[ "$TEST_TYPE" == "integration" || "$TEST_TYPE" == "e2e" || "$TEST_TYPE" == "all" ]]; then
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

# Run tests based on type
case $TEST_TYPE in
    "unit")
        print_header "� Running Unit Tests"
        pytest tests/ -m "unit" $PYTEST_ARGS
        ;;
    "integration")
        print_header "🔗 Running Integration Tests"
        pytest tests/ -m "integration" $PYTEST_ARGS
        ;;
    "e2e")
        print_header "🎯 Running End-to-End Tests"
        pytest tests/test_comprehensive_workflow.py $PYTEST_ARGS
        ;;
    "all")
        print_header "🧪 Running All Tests"
        echo ""
        
        print_info "Running Unit Tests..."
        pytest tests/ -m "unit" $PYTEST_ARGS || true
        echo ""
        
        print_info "Running Integration Tests..."
        pytest tests/ -m "integration" $PYTEST_ARGS || true
        echo ""
        
        print_info "Running End-to-End Tests..."
        pytest tests/test_comprehensive_workflow.py $PYTEST_ARGS || true
        echo ""
        
        print_info "Running Additional Tests..."
        pytest tests/ -m "not (unit or integration)" $PYTEST_ARGS || true
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
