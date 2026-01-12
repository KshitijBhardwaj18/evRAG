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
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/evrag
REDIS_URL=redis://localhost:6379/0
ENV=development
LOG_LEVEL=INFO
EOF
    echo "✅ Created .env file. Please update DATABASE_URL if needed."
fi

# Check if database exists (simple check)
echo ""
echo "📊 Make sure PostgreSQL is running and database 'evrag' exists:"
echo "   createdb evrag"
echo ""

# Start the server
echo "🎯 Starting FastAPI server..."
echo "   API will be available at: http://localhost:8000"
echo "   Docs available at: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

