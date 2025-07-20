#!/bin/bash

# Docker Cleanup Script for Knowledge Graph MCP

set -e

echo "🧹 Cleaning up Knowledge Graph MCP Docker setup..."
echo ""

# Stop and remove containers
if docker-compose ps -q > /dev/null 2>&1; then
    echo "🛑 Stopping Docker containers..."
    docker-compose down
    echo "   ✅ Containers stopped"
else
    echo "ℹ️  No running containers found"
fi

# Ask if user wants to remove data volumes
read -p "🗑️  Remove all data volumes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing data volumes..."
    docker-compose down -v
    echo "   ✅ Volumes removed"
fi

# Ask if user wants to remove images
read -p "🗑️  Remove Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing Docker images..."
    docker rmi $(docker images -q knowledge-graph-*) 2>/dev/null || echo "   ℹ️  No images to remove"
    echo "   ✅ Images removed"
fi

echo ""
echo "✅ Docker cleanup complete!"
echo ""
echo "💡 To restart from scratch:"
echo "   ./scripts/docker_setup.sh"