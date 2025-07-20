# n8n Batch Processing Trial Branch

This branch is dedicated to experimenting with n8n batch processing integration while keeping the main branch stable.

## Branch Purpose
- **Experiment** with n8n workflow automation
- **Build** FastAPI wrapper around existing MCP tools
- **Test** batch processing capabilities
- **Iterate** safely without affecting production system

## Current Status: Phase 0 Complete ✅
- ✅ n8n installed and running locally
- ✅ Safari-compatible configuration
- ✅ Management scripts created
- ✅ Comprehensive workflow documentation

## Development Approach

### Safe Experimentation
- **Main branch preserved** - Your working MCP system stays untouched
- **Feature branch isolation** - All n8n experiments happen here
- **Easy rollback** - Can switch back to main anytime
- **Incremental commits** - Small, testable changes

### Trial Phases
1. **Phase 1**: Build FastAPI wrapper (THIS BRANCH)
2. **Phase 2**: Create basic n8n workflow
3. **Phase 3**: Add multi-provider LLM support
4. **Phase 4**: Production-ready features

### Merge Strategy
- **Test thoroughly** in this branch first
- **Create PR** when ready to merge stable features
- **Code review** before merging to main
- **Preserve main stability** at all times

## Quick Commands for This Branch

### n8n Management
```bash
# Start n8n for development
./scripts/n8n_manager.sh start

# Check n8n status
./scripts/n8n_manager.sh status

# Access n8n interface
open http://localhost:5678
```

### Branch Management
```bash
# Switch to trial branch
git checkout feature/n8n-batch-processing

# Switch back to stable main
git checkout main

# Check which branch you're on
git branch

# Push trial changes
git add . && git commit -m "Trial: description" && git push
```

### Development Workflow
```bash
# Start your existing MCP system
./scripts/start_services.sh
./scripts/start_mcp_server.sh

# In parallel, start n8n for testing
./scripts/n8n_manager.sh start

# Both systems running independently
```

## Files Added in This Branch
- `N8N_TRIAL_README.md` - This documentation
- Future: `src/api/` - FastAPI wrapper
- Future: `n8n_workflows/` - Export n8n workflow definitions
- Future: `tests/api/` - API endpoint tests

## Benefits of Branch Approach
- ✅ **Risk-free experimentation** - Main system always works
- ✅ **Easy comparison** - Can test both approaches
- ✅ **Gradual integration** - Merge pieces when ready
- ✅ **Team collaboration** - Others can review before merge
- ✅ **Version control** - Full history of n8n development

## Next Steps
1. **Explore n8n interface** (Phase 0 - current)
2. **Build FastAPI wrapper** (Phase 1 - next)
3. **Create simple workflow** (Phase 2)
4. **Test batch processing** (Phase 3)
5. **Merge stable features** back to main

This approach ensures your excellent existing MCP system remains stable while we build the n8n batch processing capabilities.