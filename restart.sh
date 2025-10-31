#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: ./restart.sh [backend|frontend|db|all]"
    echo ""
    echo "Examples:"
    echo "  ./restart.sh backend    # Restart only Django backend"
    echo "  ./restart.sh frontend   # Restart only React frontend"
    echo "  ./restart.sh all        # Restart all services"
    echo ""
    echo "💡 Hot reload should work automatically, but use this if you need to restart a service."
    exit 1
fi

SERVICE=$1

case $SERVICE in
    "backend")
        echo "🔄 Restarting Django backend..."
        docker-compose restart backend
        echo "✅ Backend restarted! Hot reload should continue working."
        ;;
    "frontend")
        echo "🔄 Restarting React frontend..."
        docker-compose restart frontend
        echo "✅ Frontend restarted! Hot reload should continue working."
        ;;
    "db")
        echo "🔄 Restarting database..."
        docker-compose restart db
        echo "✅ Database restarted!"
        ;;
    "all")
        echo "🔄 Restarting all services..."
        docker-compose restart
        echo "✅ All services restarted!"
        ;;
    *)
        echo "❌ Unknown service: $SERVICE"
        echo "Available services: backend, frontend, db, all"
        exit 1
        ;;
esac
