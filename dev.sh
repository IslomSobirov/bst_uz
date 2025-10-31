#!/bin/bash

echo "🚀 Starting Boosty development environment with hot reload..."

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Start services in detached mode
echo "🔧 Starting services..."
docker-compose up -d db

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Start backend
echo "🐍 Starting Django backend..."
docker-compose up -d backend

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Start frontend
echo "⚛️  Starting React frontend..."
docker-compose up -d frontend

# Show logs
echo "📋 Showing logs (Ctrl+C to stop watching logs, containers will keep running)..."
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "🗄️  Database: localhost:5432"
echo ""
echo "💡 Hot reload is enabled! Make changes to your code and they'll automatically reload."
echo "🛑 To stop all services: docker-compose down"
echo "📊 To view logs: docker-compose logs -f [service_name]"

# Follow logs
docker-compose logs -f
