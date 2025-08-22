#!/usr/bin/env zsh
set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${CYAN}${BOLD}$1${NC}"
}

# Function to check system requirements
check_requirements() {
    print_header "🔍 Checking System Requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    local python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python ${python_version} ✓"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed"
        exit 1
    fi
    print_success "pip3 ✓"
    
    # Check curl for testing
    if ! command -v curl &> /dev/null; then
        print_warning "curl not found - some tests may not work"
    else
        print_success "curl ✓"
    fi
    
    echo ""
}

# Function to setup environment
setup_environment() {
    print_header "🛠️  Setting Up Environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv .venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source .venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1
    
    # Install dependencies
    print_status "Installing dependencies..."
    if [ -f "backend/requirements.txt" ]; then
        pip install -r backend/requirements.txt > /dev/null 2>&1
        print_success "Backend dependencies installed"
    fi
    
    # Create necessary directories
    print_status "Creating necessary directories..."
    mkdir -p uploads logs frontend static
    
    # Set PYTHONPATH
    export PYTHONPATH="${PWD}:${PYTHONPATH:-}"
    
    echo ""
}

# Function to validate files
validate_files() {
    print_header "📂 Validating Project Files..."
    
    local missing_files=()
    
    # Check essential backend files
    local backend_files=(
        "backend/app/main.py"
        "backend/app/api/v1/routers.py" 
        "backend/requirements.txt"
    )
    
    for file in "${backend_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "$file ✓"
        else
            print_error "$file ✗"
            missing_files+=("$file")
        fi
    done
    
    # Check frontend files
    local frontend_files=(
        "frontend/index.html"
        "frontend/dashboard.html"
        "frontend/travel-form.html"
    )
    
    for file in "${frontend_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "$file ✓"
        else
            print_warning "$file ✗ (will be created if missing)"
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_error "Missing critical files. Please ensure all backend files exist."
        exit 1
    fi
    
    echo ""
}

# Function to run comprehensive tests
run_tests() {
    print_header "🧪 Running Comprehensive Tests..."
    
    # Backend API tests
    print_status "Running backend tests..."
    if [ -d "tests" ]; then
        python -m pytest tests/ -v --tb=short || print_warning "Some backend tests failed"
    else
        print_warning "No test directory found, skipping backend tests"
    fi
    
    # Frontend validation
    print_status "Validating frontend files..."
    local frontend_valid=true
    
    for file in frontend/*.html; do
        if [ -f "$file" ]; then
            # Basic HTML validation
            if grep -q "<!DOCTYPE html>" "$file" && grep -q "</html>" "$file"; then
                print_success "$(basename $file) has valid HTML structure ✓"
            else
                print_warning "$(basename $file) may have HTML issues"
                frontend_valid=false
            fi
        fi
    done
    
    echo ""
}

# Function to start server with health checks
start_server() {
    print_header "🚀 Starting TravelExpense SaaS Application..."
    
    # Check if server is already running
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Server already running on port 8000"
        if [ "$COMMAND" != "restart" ]; then
            print_status "Use './run_local.sh stop' to stop or './run_local.sh restart' to restart"
            return 1
        else
            print_status "Restarting server..."
            stop_server
            sleep 2
        fi
    fi
    
    # Start the FastAPI server
    print_status "Starting FastAPI server..."
    python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
    API_PID=$!
    
    # Store PID for cleanup
    echo $API_PID > .api_pid
    
    # Wait for server to start with timeout
    print_status "Waiting for server to start..."
    local timeout=30
    local count=0
    
    while [ $count -lt $timeout ]; do
        if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
            break
        fi
        sleep 1
        count=$((count + 1))
        echo -n "."
    done
    echo ""
    
    if [ $count -ge $timeout ]; then
        print_error "❌ Server failed to start within ${timeout} seconds"
        kill $API_PID 2>/dev/null || true
        rm -f .api_pid
        return 1
    fi
    
    # Comprehensive health check
    print_status "Running health checks..."
    
    # Test API endpoints
    local endpoints=(
        "http://localhost:8000/"
        "http://localhost:8000/landingpage" 
        "http://localhost:8000/api/v1/"
        "http://localhost:8000/api/v1/landingpage"
        "http://localhost:8000/api/v1/dashboard"
        "http://localhost:8000/api/v1/travel-form"
        "http://localhost:8000/docs"
    )
    
    local working_endpoints=()
    local failed_endpoints=()
    
    for endpoint in "${endpoints[@]}"; do
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null || echo "000")
        if [[ "$http_code" =~ ^(200|30[0-9])$ ]]; then
            working_endpoints+=("$endpoint")
            print_success "$(echo $endpoint | sed 's|http://localhost:8000||') ✓ ($http_code)"
        else
            failed_endpoints+=("$endpoint")
            print_warning "$(echo $endpoint | sed 's|http://localhost:8000||') ✗ ($http_code)"
        fi
    done
    
    echo ""
    print_header "🎉 TravelExpense SaaS is Ready!"
    
    echo -e "${BOLD}📱 ACCESS POINTS:${NC}"
    echo "  🏠 Landing Page:    http://localhost:8000/"
    echo "  🏠 Alt Landing:     http://localhost:8000/landingpage" 
    echo "  📊 Dashboard:       http://localhost:8000/api/v1/dashboard"
    echo "  ✈️  Travel Form:     http://localhost:8000/api/v1/travel-form"
    echo "  📚 API Docs:        http://localhost:8000/docs"
    echo ""
    
    echo -e "${BOLD}✨ FEATURES AVAILABLE:${NC}"
    echo "  ✅ User Registration & Authentication"
    echo "  ✅ Role-based Access (Employee/Manager/Admin)"
    echo "  ✅ Travel Expense Management"
    echo "  ✅ Receipt Upload & OCR Processing"
    echo "  ✅ PDF Export & Reporting"
    echo "  ✅ Modern Responsive UI"
    echo ""
    
    echo -e "${BOLD}🛠️  MANAGEMENT:${NC}"
    echo "  Stop Server:   ./run_local.sh stop"
    echo "  Restart:       ./run_local.sh restart"
    echo "  Run Tests:     ./run_local.sh test"
    echo "  Check Status:  ./run_local.sh status"
    echo ""
    
    if [ ${#failed_endpoints[@]} -gt 0 ]; then
        print_warning "Some endpoints are not responding correctly. Check logs for details."
    fi
    
    print_status "🎯 Ready to use! Open http://localhost:8000/ in your browser"
    print_status "Press Ctrl+C to stop the server"
    
    # Wait for Ctrl+C
    trap 'print_status "Stopping server..."; stop_server; exit 0' INT
    wait $API_PID
}

# Function to stop server
stop_server() {
    print_header "🛑 Stopping TravelExpense Server..."
    
    # Kill any process using port 8000
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_status "Stopping server on port 8000..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    # Remove PID file if it exists
    if [ -f ".api_pid" ]; then
        API_PID=$(cat .api_pid)
        kill $API_PID 2>/dev/null || true
        rm -f .api_pid
        print_success "Server process stopped"
    fi
    
    print_success "✅ TravelExpense server stopped"
}

# Function to show comprehensive status
show_status() {
    print_header "📊 TravelExpense System Status"
    
    # Check server status
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_success "🟢 Server is running on http://localhost:8000"
        
        # Test endpoints
        local endpoints=(
            "http://localhost:8000/"
            "http://localhost:8000/api/v1/dashboard"
            "http://localhost:8000/docs"
        )
        
        echo ""
        print_status "Endpoint Status:"
        for endpoint in "${endpoints[@]}"; do
            local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null || echo "000")
            local endpoint_path="${endpoint#http://localhost:8000}"
            if [ -z "$endpoint_path" ]; then
                endpoint_path="/"
            fi
            if [[ "$http_code" =~ ^(200|30[0-9])$ ]]; then
                print_success "  $endpoint_path ✓ ($http_code)"
            else
                print_error "  $endpoint_path ✗ ($http_code)"
            fi
        done
    else
        print_error "🔴 Server is not running"
    fi
    
    # Check files
    echo ""
    print_status "File Status:"
    local files=("backend/app/main.py" "frontend/index.html" ".venv/bin/activate")
    for file in "${files[@]}"; do
        if [ -f "$file" ] || [ -d "$file" ]; then
            print_success "  $file ✓"
        else
            print_error "  $file ✗"
        fi
    done
    
    # Check database
    echo ""
    print_status "Database Status:"
    if [ -f "app.db" ]; then
        local db_size=$(du -h app.db | cut -f1)
        print_success "  SQLite database exists (${db_size})"
    else
        print_warning "  Database will be created on first start"
    fi
    
    echo ""
}

# Function to run all tests
run_all_tests() {
    print_header "🧪 Running Complete Test Suite..."
    
    # Ensure environment is set up
    source .venv/bin/activate 2>/dev/null || {
        print_error "Virtual environment not found. Run setup first."
        return 1
    }
    
    export PYTHONPATH="${PWD}:${PYTHONPATH:-}"
    
    # Run backend tests
    if [ -d "tests" ]; then
        print_status "Running backend API tests..."
        python -m pytest tests/ -v --tb=short || print_warning "Some backend tests failed"
    else
        print_warning "No test directory found"
    fi
    
    # Test server if running
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_status "Testing live server endpoints..."
        local test_passed=0
        local test_total=0
        
        local test_endpoints=(
            "http://localhost:8000/|Landing Page"
            "http://localhost:8000/landingpage|Alternative Landing"
            "http://localhost:8000/api/v1/|API Landing"
            "http://localhost:8000/api/v1/dashboard|Dashboard"
            "http://localhost:8000/api/v1/travel-form|Travel Form"
            "http://localhost:8000/docs|API Documentation"
        )
        
        for test_item in "${test_endpoints[@]}"; do
            local endpoint_url=$(echo "$test_item" | cut -d'|' -f1)
            local test_name=$(echo "$test_item" | cut -d'|' -f2)
            test_total=$((test_total + 1))
            
            local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint_url" 2>/dev/null || echo "000")
            if [[ "$http_code" =~ ^(200|30[0-9])$ ]]; then
                print_success "  $test_name ✓ ($http_code)"
                test_passed=$((test_passed + 1))
            else
                print_error "  $test_name ✗ ($http_code)"
            fi
        done
        
        echo ""
        if [ $test_passed -eq $test_total ]; then
            print_success "🎉 All endpoint tests passed! ($test_passed/$test_total)"
        else
            print_warning "⚠️  Some tests failed ($test_passed/$test_total passed)"
        fi
    else
        print_warning "Server not running. Start server first to run live tests."
    fi
    
    echo ""
}

# Function to show usage
show_usage() {
    echo -e "${BOLD}TravelExpense SaaS - Local Development Tool${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo -e "${BOLD}Commands:${NC}"
    echo "  ${GREEN}start${NC}      Start the application (default)"
    echo "  ${GREEN}stop${NC}       Stop the application server"
    echo "  ${GREEN}restart${NC}    Restart the application server"
    echo "  ${GREEN}status${NC}     Show comprehensive system status"
    echo "  ${GREEN}test${NC}       Run complete test suite"
    echo "  ${GREEN}setup${NC}      Setup/reset development environment"
    echo "  ${GREEN}help${NC}       Show this help message"
    echo ""
    echo -e "${BOLD}Examples:${NC}"
    echo "  $0              # Start the app with full validation"
    echo "  $0 start        # Start the app"
    echo "  $0 test         # Run all tests"
    echo "  $0 status       # Check what's running"
    echo ""
    echo -e "${BOLD}What happens when you run this:${NC}"
    echo "  1. ✅ System requirements check"
    echo "  2. 🛠️  Environment setup (venv, dependencies)"
    echo "  3. 📂 File validation"
    echo "  4. 🧪 Comprehensive testing"
    echo "  5. 🚀 Server startup with health checks"
    echo "  6. 🌐 Ready to use at http://localhost:8000"
}

# Parse command line arguments
COMMAND=${1:-start}

# Ensure we're in the right directory
cd "$(dirname "$0")"

case $COMMAND in
    stop)
        stop_server
        exit 0
        ;;
    status)
        show_status
        exit 0
        ;;
    test)
        check_requirements
        setup_environment
        run_all_tests
        exit 0
        ;;
    setup)
        check_requirements
        setup_environment
        validate_files
        print_success "✅ Setup complete! Run './run_local.sh start' to launch the app"
        exit 0
        ;;
    restart)
        stop_server
        sleep 2
        COMMAND="start"  # Continue to start
        ;;
    start)
        ;;
    help|--help|-h)
        show_usage
        exit 0
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        echo ""
        show_usage
        exit 1
        ;;
esac

# Main execution for start command
print_header "🚀 TravelExpense SaaS - Complete Startup Sequence"
echo ""

# Run all setup and validation steps
check_requirements
setup_environment  
validate_files
run_tests

# Start the server
start_server
