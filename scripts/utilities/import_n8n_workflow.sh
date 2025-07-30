#!/bin/bash

echo "🔄 Importing DocsGPT-LlamaParse workflow into n8n..."

# Check if n8n is running
if ! curl -s http://localhost:5678/rest/active-workflows > /dev/null; then
    echo "❌ n8n is not accessible at localhost:5678"
    echo "   Please ensure n8n is running with: ./scripts/utilities/n8n_manager.sh start"
    exit 1
fi

# Path to the workflow file
WORKFLOW_FILE="/Users/aimiegarces/Agents/workflows/docsgpt_llamaparse_workflow.json"

if [ ! -f "$WORKFLOW_FILE" ]; then
    echo "❌ Workflow file not found: $WORKFLOW_FILE"
    exit 1
fi

echo "📄 Workflow file: $WORKFLOW_FILE"

# Import workflow using n8n CLI (if available) or API
if command -v n8n > /dev/null; then
    echo "🔧 Using n8n CLI to import workflow..."
    n8n import:workflow --input="$WORKFLOW_FILE"
else
    echo "🌐 Using n8n API to import workflow..."
    
    # Try to import via API
    RESPONSE=$(curl -s -X POST http://localhost:5678/rest/workflows \
        -H "Content-Type: application/json" \
        -d @"$WORKFLOW_FILE")
    
    if echo "$RESPONSE" | grep -q '"id"'; then
        echo "✅ Workflow imported successfully!"
        echo "🔗 Access n8n at: http://localhost:5678"
        echo "📝 Login with: admin / password123"
        echo ""
        echo "🎯 Next steps:"
        echo "   1. Open n8n web interface"
        echo "   2. Find 'DocsGPT-LlamaParse-Integration' workflow"
        echo "   3. Activate the workflow"
        echo "   4. Test the webhook endpoint"
    else
        echo "❌ Failed to import workflow"
        echo "Response: $RESPONSE"
        echo ""
        echo "💡 Manual import instructions:"
        echo "   1. Open http://localhost:5678"
        echo "   2. Click 'Create new workflow'"
        echo "   3. Click '...' menu → 'Import from file'"
        echo "   4. Select: $WORKFLOW_FILE"
    fi
fi

echo ""
echo "🔗 Webhook URL will be: http://localhost:5678/webhook/docsgpt-batch-process"
echo "🧪 Test with:"
echo 'curl -X POST http://localhost:5678/webhook/docsgpt-batch-process \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{"batch_id":"test-123","user_id":"test","files":[{"path":"/test/sample.pdf","name":"sample.pdf"}]}'"'"''