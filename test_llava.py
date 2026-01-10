#!/usr/bin/env python3
"""
Test script for LLaVA vision model integration
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.ollama_service import OllamaService

async def test_llava():
    """Test LLaVA with a sample image"""
    
    # Initialize ollama service
    ollama_service = OllamaService(host="http://localhost:11434", model="llama3.1:8b")
    
    # Find a test image
    test_image = Path(__file__).parent / "documents" / "ces2026" / "images" / "infographics" / "samsung_ssd_roadmap_1767950527033.png"
    
    if not test_image.exists():
        print(f"❌ Test image not found: {test_image}")
        return False
    
    print(f"✓ Found test image: {test_image.name}")
    print(f"✓ Using model: llava:13b")
    print(f"\n🔍 Analyzing image...")
    
    # Test image analysis
    full_response = ""
    async for thought, metrics in ollama_service.generate_step(
        context="Analyzing competitive intelligence.",
        system_prompt="Describe what you see in this image. What product or technology is being shown?",
        user_prompt="What's the main takeaway from this infographic?",
        model="llava:13b",
        image_paths=[str(test_image)]
    ):
        full_response = thought
    
    if not full_response:
        print(f"\n❌ Analysis failed!")
        return False
    
    print(f"\n✅ Analysis successful!")
    print(f"\n📊 Result:")
    print(f"   Model: llava:13b")
    print(f"   Analysis: {full_response[:200]}...")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_llava())
    sys.exit(0 if success else 1)
