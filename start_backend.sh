#!/bin/bash

# Quick start script for EvRAG backend

echo "🚀 Starting EvRAG Backend..."
echo ""

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cat > .env << EOF
DATABASE_URL=sqlite+aiosqlite:///./evrag.db
REDIS_URL=redis://localhost:6379/0
ENV=development
LOG_LEVEL=INFO
EOF
    echo "✅ Created .env file (using SQLite - no PostgreSQL needed)."
fi

echo ""

# Start the server
echo "🎯 Starting FastAPI server..."
echo "   API will be available at: http://localhost:8000"
echo "   Docs available at: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

