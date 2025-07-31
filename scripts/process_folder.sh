#!/bin/bash

# Process all PDFs in a folder manually
# Usage: ./scripts/process_folder.sh [folder_path]

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <folder_path>"
    echo "Example: $0 /Users/user/Documents/PDFs"
    echo ""
    echo "This will process all PDF files in the folder one by one."
    exit 1
fi

FOLDER_PATH="$1"

# Validate folder exists
if [ ! -d "$FOLDER_PATH" ]; then
    echo "❌ Folder does not exist: $FOLDER_PATH"
    exit 1
fi

echo "🚀 Processing all PDFs in: $FOLDER_PATH"
echo "📋 Checking prerequisites..."
./scripts/check_status.sh

cd src

# Find and process all PDF files
pdf_count=0
for pdf_file in "$FOLDER_PATH"/*.pdf; do
    if [ -f "$pdf_file" ]; then
        echo ""
        echo "📄 Processing: $(basename "$pdf_file")"
        uv run python processor/document_pipeline.py "$pdf_file"
        pdf_count=$((pdf_count + 1))
    fi
done

if [ $pdf_count -eq 0 ]; then
    echo "⚠️  No PDF files found in $FOLDER_PATH"
else
    echo ""
    echo "✅ Processed $pdf_count PDF files successfully!"
fi