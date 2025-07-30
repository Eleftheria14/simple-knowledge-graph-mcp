#!/bin/bash
# Convenience wrapper for checking system status
echo "📊 Checking DocsGPT + Knowledge Graph System Status..."
exec "$(dirname "$0")/integrated/status_integrated_system.sh"