#!/usr/bin/env zsh
set -euo pipefail

echo "📊 Reisekostenabrechnung Status"
echo "================================"

# Check if server is running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Server: Running on http://localhost:8000"
    echo "   📋 API Docs: http://localhost:8000/docs"
    echo "   🖥️  Frontend: http://localhost:8000/api/v1/ui"
else
    echo "❌ Server: Not running"
fi

# Check database
if [ -f "app.db" ]; then
    echo "✅ Database: app.db exists"
    
    # Count records
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        TRAVEL_COUNT=$(python3 -c "
import sqlite3
conn = sqlite3.connect('app.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM travels')
count = cursor.fetchone()[0]
conn.close()
print(count)
" 2>/dev/null || echo "0")
        
        RECEIPT_COUNT=$(python3 -c "
import sqlite3
conn = sqlite3.connect('app.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM receipts')
count = cursor.fetchone()[0]
conn.close()
print(count)
" 2>/dev/null || echo "0")
        
        echo "   📈 Travels: $TRAVEL_COUNT"
        echo "   🧾 Receipts: $RECEIPT_COUNT"
    fi
else
    echo "❌ Database: Not found"
fi

# Check uploads directory
if [ -d "uploads" ]; then
    UPLOAD_COUNT=$(find uploads -type f 2>/dev/null | wc -l)
    echo "✅ Uploads: $UPLOAD_COUNT files in ./uploads/"
else
    echo "❌ Uploads: Directory not found"
fi

# Check virtual environment
if [ -d ".venv" ]; then
    echo "✅ Environment: Python venv ready"
else
    echo "❌ Environment: Run ./scripts/dev_setup.sh first"
fi

echo ""
echo "🚀 Quick Commands:"
echo "   Start:  ./run_local.sh start (or just ./run_local.sh)"
echo "   Stop:   ./run_local.sh stop"
echo "   Restart:./run_local.sh restart"
echo "   Test:   ./run_local.sh test"
echo "   Status: ./run_local.sh status"
echo "   Setup:  ./scripts/dev_setup.sh"
