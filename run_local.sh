#!/usr/bin/env zsh
set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Function to stop server
stop_server() {
    print_status "🛑 Stopping Reisekostenabrechnung..."
    
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
    fi
    
    print_success "✅ Server stopped"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [start|stop|restart|status|test]"
    echo ""
    echo "Commands:"
    echo "  start    - Start the application server (default)"
    echo "  stop     - Stop the application server"
    echo "  restart  - Restart the application server"
    echo "  status   - Show current system status"
    echo "  test     - Run API tests"
    echo ""
    echo "Examples:"
    echo "  $0        # Start server"
    echo "  $0 start  # Start server"
    echo "  $0 stop   # Stop server"
    echo "  $0 test   # Run tests"
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
        exec ./status.sh
        ;;
    test)
        exec python -m pytest tests/ -v
        ;;
    restart)
        stop_server
        sleep 2
        ;;
    start)
        ;;
    help|--help|-h)
        show_usage
        exit 0
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

echo "🚀 Starting Reisekostenabrechnung MVP..."

# Check if setup has been run
if [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found. Running initial setup..."
    ./scripts/dev_setup.sh
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p uploads
mkdir -p logs

# Check if database exists, if not create it
if [ ! -f "app.db" ]; then
    print_status "Database not found. It will be created automatically on first start."
fi

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Server already running on port 8000"
    if [ "$COMMAND" != "restart" ]; then
        print_status "Use './run_local.sh stop' to stop or './run_local.sh restart' to restart"
        exit 1
    else
        print_status "Restarting server..."
    fi
fi

# Start the API server
print_status "Starting FastAPI server..."
export PYTHONPATH="${PWD}:${PYTHONPATH:-}"
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Wait for server to start
print_status "Waiting for server to start..."
sleep 3

# Check if server is running
if curl -s http://localhost:8000/docs > /dev/null; then
    print_success "✅ FastAPI server is running on http://localhost:8000"
    print_success "✅ API Documentation: http://localhost:8000/docs"
    print_success "✅ Travel Form UI: http://localhost:8000/api/v1/ui"
    print_success "✅ Database: SQLite (app.db)"
    print_success "✅ Uploads Directory: ./uploads"
    
    echo ""
    print_status "🎯 Quick Start Guide:"
    echo "  1. Open http://localhost:8000/api/v1/ui in your browser"
    echo "  2. Create a new travel with employee details"
    echo "  3. Upload receipt images/PDFs for OCR processing"
    echo "  4. Export travels as PDF"
    echo "  5. API docs available at http://localhost:8000/docs"
    echo ""
    
    # Store PID for easy cleanup
    echo $API_PID > .api_pid
    
    print_status "Press Ctrl+C to stop the server, or use './run_local.sh stop'"
    
    # Wait for Ctrl+C
    trap 'print_status "Stopping server..."; kill $API_PID 2>/dev/null || true; rm -f .api_pid; exit 0' INT
    wait $API_PID
else
    print_error "❌ Failed to start server"
    kill $API_PID 2>/dev/null || true
    exit 1
fi
