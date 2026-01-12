#!/bin/bash

# Quick start script for EvRAG frontend

echo "🚀 Starting EvRAG Frontend..."
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚙️  Creating .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
fi

echo ""
echo "🎯 Starting Next.js development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo ""

npm run dev

