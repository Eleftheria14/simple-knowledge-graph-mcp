#!/bin/bash

# Start Document Processor
# Usage: ./scripts/start_processor.sh [watch_folder]

set -e

echo "🚀 Starting Document Processor..."

# Check if Neo4j is running
echo "📋 Checking prerequisites..."
./scripts/check_status.sh

# Check if processor watch folder is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <watch_folder>"
    echo "Example: $0 /Users/user/Documents/PDFs"
    exit 1
fi

WATCH_FOLDER="$1"

# Validate watch folder exists
if [ ! -d "$WATCH_FOLDER" ]; then
    echo "❌ Watch folder does not exist: $WATCH_FOLDER"
    exit 1
fi

echo "📂 Watch folder: $WATCH_FOLDER"

# Start the processor
cd src
echo "🔄 Starting folder watcher..."
uv run python processor/folder_watcher.py "$WATCH_FOLDER"