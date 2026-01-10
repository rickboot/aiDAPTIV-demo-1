#!/usr/bin/env python3
"""
Check the LAST chunk for token usage data
"""
import ollama
import json

print("Checking LAST chunk for token data...")
print("=" * 60)

stream = ollama.chat(
    model='llama3.1:8b',
    messages=[{'role': 'user', 'content': 'Say hello in 10 words'}],
    stream=True
)

last_chunk = None
for chunk in stream:
    last_chunk = chunk

print("\nLAST CHUNK:")
print(json.dumps(last_chunk, indent=2, default=str))
print("\n" + "=" * 60)

if 'eval_count' in last_chunk:
    print(f"✓ Output tokens: {last_chunk['eval_count']}")
if 'prompt_eval_count' in last_chunk:
    print(f"✓ Input tokens: {last_chunk['prompt_eval_count']}")
if 'eval_count' in last_chunk and 'prompt_eval_count' in last_chunk:
    total = last_chunk['eval_count'] + last_chunk['prompt_eval_count']
    print(f"✓ Total tokens: {total}")
