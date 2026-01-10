#!/usr/bin/env python3
"""
Show what each chunk contains in Ollama streaming
"""
import ollama

print("Analyzing Ollama chunk structure...")
print("=" * 60)

stream = ollama.chat(
    model='llama3.1:8b',
    messages=[{'role': 'user', 'content': 'Count to 5'}],
    stream=True
)

chunk_num = 0
for chunk in stream:
    chunk_num += 1
    content = chunk['message']['content']
    done = chunk.get('done', False)
    
    # Show content representation
    if content:
        print(f"Chunk {chunk_num:2d}: '{content}' (len={len(content)}, bytes={len(content.encode('utf-8'))})")
    
    # Show final chunk with token counts
    if done:
        print("\n" + "=" * 60)
        print("FINAL CHUNK (done=True):")
        print(f"  Content: '{content}'")
        print(f"  Input tokens (prompt_eval_count): {chunk.get('prompt_eval_count', 'N/A')}")
        print(f"  Output tokens (eval_count): {chunk.get('eval_count', 'N/A')}")
        print(f"  Total chunks received: {chunk_num}")
        print("=" * 60)

print("\nConclusion:")
print("- Each chunk = 1 piece of generated text (often 1 token)")
print("- Chunks can be single chars, words, or punctuation")
print("- Token count ≠ chunk count (tokens are semantic units)")
print("- Real token counts only in final chunk when done=True")
