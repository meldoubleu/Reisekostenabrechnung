#!/usr/bin/env bash
# Essential Features Test Runner - Focus on Core Functionality

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

print_header "🧪 Essential Features Test Suite"
echo "=================================="

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    print_success "Virtual environment activated"
else
    print_warning "Virtual environment not found, using system Python"
fi

# Check if backend is running
BACKEND_RUNNING=false
if curl -s "http://localhost:8000/" > /dev/null 2>&1; then
    print_success "Backend is already running"
    BACKEND_RUNNING=true
    CLEANUP_BACKEND=false
else
    print_warning "Backend not running. Starting backend for tests..."
    ./scripts/run_local.sh start &
    BACKEND_PID=$!
    sleep 8
    
    if curl -s "http://localhost:8000/" > /dev/null 2>&1; then
        print_success "Backend started for testing"
        BACKEND_RUNNING=true
        CLEANUP_BACKEND=true
    else
        print_error "Failed to start backend. Please start manually with ./run_local.sh"
        exit 1
    fi
fi

if [ "$BACKEND_RUNNING" = true ]; then
    echo ""
    print_header "🎯 Running Essential Feature Tests"
    echo ""
    
    # Run the essential tests
    print_info "Testing Core Authentication..."
    pytest tests/test_essential_features.py::TestCoreAuthentication -v
    
    echo ""
    print_info "Testing Travel Management..."
    pytest tests/test_essential_features.py::TestTravelManagement -v
    
    echo ""
    print_info "Testing User Management..."
    pytest tests/test_essential_features.py::TestUserManagement -v
    
    echo ""
    print_info "Testing Basic Security..."
    pytest tests/test_essential_features.py::TestBasicSecurity -v
    
    echo ""
    print_info "Testing System Health..."
    pytest tests/test_essential_features.py::TestSystemHealth -v
    
    echo ""
    print_info "Testing Complete Workflows..."
    pytest tests/test_essential_features.py::TestCompleteWorkflow -v
    
    echo ""
    print_header "📊 Test Summary"
    echo ""
    
    # Run all essential tests and get summary
    pytest -c pytest-essential.ini tests/test_essential_features.py --tb=short -q
    
    if [ $? -eq 0 ]; then
        print_success "All essential features are working correctly!"
    else
        print_warning "Some tests failed, but core functionality may still be working"
    fi
else
    print_error "Cannot run tests without backend"
    exit 1
fi

# Cleanup if we started the backend
if [[ "$CLEANUP_BACKEND" == "true" ]]; then
    echo ""
    print_info "Stopping test backend..."
    kill $BACKEND_PID 2>/dev/null || true
    sleep 2
fi

echo ""
print_header "✅ Essential Features Testing Complete"
echo ""
print_info "Key Features Tested:"
echo "  • User Authentication (login, registration, profile access)"
echo "  • Travel Management (create, view, update travel expenses)"
echo "  • User Management (admin user creation)"
echo "  • Basic Security (authentication required, role restrictions)"
echo "  • System Health (API accessibility, endpoint availability)"
echo "  • Complete Workflows (end-to-end user journeys)"

# Deactivate virtual environment
if [ -f ".venv/bin/activate" ]; then
    deactivate
fi
