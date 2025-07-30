#!/bin/bash
# Convenience wrapper for stopping the integrated system
echo "🛑 Stopping DocsGPT + Knowledge Graph Integration System..."
exec "$(dirname "$0")/integrated/stop_integrated_system.sh"