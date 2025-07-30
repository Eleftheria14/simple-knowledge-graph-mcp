#!/bin/bash
# Convenience wrapper for starting the integrated system
echo "🚀 Starting DocsGPT + Knowledge Graph Integration System..."
exec "$(dirname "$0")/integrated/start_integrated_docsgpt.sh"