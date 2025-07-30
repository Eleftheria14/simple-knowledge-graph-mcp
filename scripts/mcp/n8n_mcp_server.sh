#!/bin/bash

# n8n MCP Server Docker Management Script
# Usage: ./scripts/n8n_mcp_server.sh [start|stop|restart|logs|status]

CONTAINER_NAME="n8n-mcp-server"
MCP_PORT="3001"
DATA_DIR="$HOME/.n8n-mcp"

case "$1" in
    start)
        echo "🚀 Starting n8n MCP Server..."
        
        # Create data directory if it doesn't exist
        mkdir -p $DATA_DIR
        
        if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
            echo "ℹ️  n8n MCP server is already running"
        else
            echo "📊 Starting n8n MCP server container..."
            docker run -d \
                --name $CONTAINER_NAME \
                -p $MCP_PORT:3000 \
                -v $DATA_DIR:/app/data \
                -e NODE_ENV=production \
                ghcr.io/czlonkowski/n8n-mcp:latest
            
            echo "⏳ Waiting for n8n MCP server to start..."
            sleep 5
            echo "✅ n8n MCP server is starting up!"
        fi
        echo "🌐 n8n MCP Server running on port: $MCP_PORT"
        echo "📁 Data directory: $DATA_DIR"
        ;;
    
    stop)
        echo "🛑 Stopping n8n MCP Server..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        echo "✅ n8n MCP server stopped"
        ;;
    
    restart)
        echo "🔄 Restarting n8n MCP Server..."
        $0 stop
        sleep 2
        $0 start
        ;;
    
    logs)
        echo "📋 n8n MCP Server logs (last 50 lines):"
        docker logs $CONTAINER_NAME --tail 50 -f
        ;;
    
    status)
        if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
            echo "✅ n8n MCP server is running"
            echo "🌐 Server port: $MCP_PORT"
            echo "📁 Data directory: $DATA_DIR"
            echo "📊 Container status:"
            docker ps --filter name=$CONTAINER_NAME
        else
            echo "❌ n8n MCP server is not running"
            echo "💡 Run './scripts/n8n_mcp_server.sh start' to start it"
        fi
        ;;
    
    *)
        echo "n8n MCP Server Docker Management Script"
        echo ""
        echo "Usage: $0 [start|stop|restart|logs|status]"
        echo ""
        echo "Commands:"
        echo "  start   - Start n8n MCP server container"
        echo "  stop    - Stop and remove n8n MCP server container"
        echo "  restart - Restart n8n MCP server container"
        echo "  logs    - Show n8n MCP server logs (follow mode)"
        echo "  status  - Check if n8n MCP server is running"
        echo ""
        echo "This server makes Claude Desktop an expert at n8n workflows"
        echo "Configure in Claude Desktop settings to use this MCP server"
        ;;
esac