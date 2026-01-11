---
description: Diagnose AG performance issues
---

# Diagnose AG Performance Issues

When AG starts to slow down your system, follow these steps:

## 1. Run the performance monitor
```bash
./.agent/monitor_performance.sh
```

## 2. Check for common issues

### High memory usage
- Look for multiple TypeScript server processes
- Check if ChromaDB is consuming excessive memory
- Verify file watching isn't indexing too many files

### High CPU usage
- Check if Vite dev server is running
- Look for runaway Python processes
- Check for Ollama processes if not needed

## 3. Quick fixes

### Restart TypeScript servers
In AG, open Command Palette (Cmd+Shift+P) and run:
- "TypeScript: Restart TS Server"

### Clear generated files
```bash
rm -rf generated/*
rm -rf backend/generated/*
```

### Clear ChromaDB cache
```bash
rm -rf backend/chroma_db/*
```

### Restart AG
Quit and restart Antigravity completely

## 4. Prevention

Make sure these files exist and are properly configured:
- `.antigravityignore` - Excludes heavy directories from indexing
- `vite.config.ts` - Optimized file watching
- `tsconfig.app.json` - Excludes unnecessary directories

## 5. Monitor over time

Run the performance monitor periodically:
```bash
watch -n 30 ./.agent/monitor_performance.sh
```

This will update every 30 seconds so you can see when the problem starts.
