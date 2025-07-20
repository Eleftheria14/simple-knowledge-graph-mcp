#!/bin/bash

# n8n Docker Management Script
# Usage: ./scripts/n8n_manager.sh [start|stop|restart|logs|status]

CONTAINER_NAME="n8n"
N8N_PORT="5678"
N8N_DATA_DIR="$HOME/.n8n"

case "$1" in
    start)
        echo "🚀 Starting n8n..."
        if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
            echo "ℹ️  n8n is already running"
        else
            docker run -d \
                --name $CONTAINER_NAME \
                -p $N8N_PORT:5678 \
                -v $N8N_DATA_DIR:/home/node/.n8n \
                -e N8N_BASIC_AUTH_ACTIVE=true \
                -e N8N_BASIC_AUTH_USER=admin \
                -e N8N_BASIC_AUTH_PASSWORD=password123 \
                -e N8N_SECURE_COOKIE=false \
                -e N8N_RUNNERS_ENABLED=true \
                n8nio/n8n
            
            echo "⏳ Waiting for n8n to start..."
            sleep 10
            echo "✅ n8n is starting up!"
        fi
        echo "🌐 Access n8n at: http://localhost:$N8N_PORT"
        echo "🔐 Username: admin | Password: password123"
        ;;
    
    stop)
        echo "🛑 Stopping n8n..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        echo "✅ n8n stopped"
        ;;
    
    restart)
        echo "🔄 Restarting n8n..."
        $0 stop
        sleep 2
        $0 start
        ;;
    
    logs)
        echo "📋 n8n logs (last 50 lines):"
        docker logs $CONTAINER_NAME --tail 50 -f
        ;;
    
    status)
        if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
            echo "✅ n8n is running"
            echo "🌐 Access at: http://localhost:$N8N_PORT"
            echo "📊 Container status:"
            docker ps --filter name=$CONTAINER_NAME
        else
            echo "❌ n8n is not running"
            echo "💡 Run './scripts/n8n_manager.sh start' to start it"
        fi
        ;;
    
    *)
        echo "n8n Docker Management Script"
        echo ""
        echo "Usage: $0 [start|stop|restart|logs|status]"
        echo ""
        echo "Commands:"
        echo "  start   - Start n8n container"
        echo "  stop    - Stop and remove n8n container"
        echo "  restart - Restart n8n container"
        echo "  logs    - Show n8n logs (follow mode)"
        echo "  status  - Check if n8n is running"
        echo ""
        echo "Access: http://localhost:$N8N_PORT"
        echo "Auth: admin / password123"
        ;;
esac