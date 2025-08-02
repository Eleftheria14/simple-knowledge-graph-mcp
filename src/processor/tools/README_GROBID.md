# ⚠️ GROBID Integration - READ ONLY

## IMPORTANT: DO NOT MODIFY GROBID CODE

The file `grobid_tool.py` in this directory is a **READ-ONLY** client wrapper for the official GROBID service.

### What This Code Does:
- **HTTP Client**: Makes API calls to official GROBID Docker container on port 8070
- **TEI XML Parser**: Parses responses from the original GROBID service
- **Data Formatter**: Structures GROBID output for our application

### What This Code Is NOT:
- ❌ **Not GROBID source code** - This is just a client wrapper
- ❌ **Not a fork** - We use the official GROBID Docker image: `lfoppiano/grobid:0.8.0`
- ❌ **Not modified GROBID** - All processing happens in the original container

### Architecture:
```
Our App → grobid_tool.py → HTTP API → Official GROBID Container
                                            ↓
                                    Original GROBID (Java)
                                            ↓
                                    PDF → TEI XML Output
```

### If You Need Changes:
1. **For GROBID behavior**: Use official GROBID parameters in API calls
2. **For parsing logic**: Create a separate parser module
3. **For output format**: Create a separate formatter module

### Official GROBID Resources:
- **Source**: https://github.com/kermitt2/grobid
- **Docker**: https://hub.docker.com/r/lfoppiano/grobid
- **Docs**: https://grobid.readthedocs.io/

---
**File Protection**: `grobid_tool.py` is set to read-only (chmod 444) to prevent accidental modifications.