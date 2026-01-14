#!/usr/bin/env python3
"""
Test if LLaVA vision model returns token counts the same way
"""
import ollama
import json
from pathlib import Path

print("Testing LLaVA token count support...")
print("=" * 60)

# Find an image to test with
img_path = Path("data/realstatic/ces2026/images/infographics/intel_panther_lake_1767950563347.png")
if not img_path.exists():
    print(f"ERROR: Image not found at {img_path}")
    exit(1)

# Encode image
import base64
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode('utf-8')

print(f"Testing with image: {img_path.name}")
print("Sending to llava:13b...")

stream = ollama.chat(
    model='llava:13b',
    messages=[{
        'role': 'user',
        'content': 'Describe this image in one sentence.',
        'images': [img_b64]
    }],
    stream=True
)

last_chunk = None
chunk_count = 0
for chunk in stream:
    chunk_count += 1
    last_chunk = chunk

print(f"\nReceived {chunk_count} chunks")
print("\nLAST CHUNK from LLaVA:")
print(json.dumps(last_chunk, indent=2, default=str))

print("\n" + "=" * 60)
if last_chunk and 'prompt_eval_count' in last_chunk:
    print(f"✓ Vision model DOES return token counts!")
    print(f"  Input tokens: {last_chunk.get('prompt_eval_count', 'N/A')}")
    print(f"  Output tokens: {last_chunk.get('eval_count', 'N/A')}")
else:
    print(f"✗ Vision model does NOT return token counts")
    print(f"  Available keys: {list(last_chunk.keys()) if last_chunk else 'None'}")
