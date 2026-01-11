#!/bin/bash
# Performance monitoring script for AG slowdown debugging

echo "=== AG Performance Monitor ==="
echo "Timestamp: $(date)"
echo ""

echo "=== System Load ==="
uptime
echo ""

echo "=== Memory Usage ==="
vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%-16s % 16.2f MB\n", "$1:", $2 * $size / 1048576);'
echo ""

echo "=== Top Memory Consumers ==="
ps aux | sort -nrk 4 | head -10
echo ""

echo "=== AG/Node/Python Processes ==="
ps aux | grep -E "(Antigravity|node|python|ollama)" | grep -v grep
echo ""

echo "=== Open Files by AG ==="
lsof -c Antigravity 2>/dev/null | wc -l
echo ""

echo "=== TypeScript Server Processes ==="
ps aux | grep tsserver | grep -v grep
echo ""

echo "=== Disk I/O ==="
iostat -d 1 2 | tail -1
echo ""
