#!/bin/bash
# Restore read-only protection for GROBID files

echo "🔒 Protecting GROBID integration files..."

# Make GROBID tool read-only
chmod 444 src/processor/tools/grobid_tool.py

# Verify protection
if [[ $(stat -f "%OLp" src/processor/tools/grobid_tool.py) == "444" ]]; then
    echo "✅ GROBID tool is now read-only (444)"
else
    echo "❌ Failed to protect GROBID tool"
    exit 1
fi

echo "🔒 GROBID protection restored successfully"
echo ""
echo "Protected files:"
echo "  - src/processor/tools/grobid_tool.py (444)"
echo ""
echo "To modify if absolutely necessary:"
echo "  chmod 644 src/processor/tools/grobid_tool.py"
echo "  # make changes"
echo "  ./scripts/protect_grobid.sh  # restore protection"