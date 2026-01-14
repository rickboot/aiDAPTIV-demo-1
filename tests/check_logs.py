import asyncio
import sys
import os
import json

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.orchestrator import SimulationOrchestrator

async def check_model_swaps():
    print("--- Starting Model Swap Verification Log ---")
    
    # Initialize simulation: CES scenario, Standard tier
    orchestrator = SimulationOrchestrator("ces2026", "standard", aidaptiv_enabled=True)
    
    # Force mock Ollama for this test to avoid real API calls
    orchestrator.use_ollama = True
    
    # Documents in CES 2026 typically start with Dossier (Text) then Images
    # We want to see:
    # 1. Start with llama (default)
    # 2. Status: Loading llava (for images)
    # 3. Memory: model_weights changes
    # 4. Status: Loading llama (for next text batch)
    
    current_model = None
    swap_count = 0
    
    print("Running simulation and capturing model events...\n")
    
    try:
        # We only need to run the first 20 docs or so to see a few swaps
        count = 0
        async for event in orchestrator.run_simulation():
            event_type = event.get("type")
            
            if event_type == "status":
                msg = event.get("message", "")
                if "Loading" in msg or "Offloading" in msg:
                    print(f"[STATUS] {msg}")
            
            elif event_type == "memory":
                data = event.get("data", {})
                model = data.get("loaded_model")
                weights = data.get("model_weights_gb")
                
                if model != current_model:
                    print(f"[MEMORY] Model Changed: {current_model} -> {model} ({weights} GB)")
                    current_model = model
                    swap_count += 1
            
            elif event_type == "document":
                doc_name = event.get("data", {}).get("name")
                doc_cat = event.get("data", {}).get("category")
                # print(f"  Processed: {doc_name} ({doc_cat})")
                count += 1
            
            if swap_count >= 3 or count > 30:
                print("\nStopping simulation: Verification target reached.")
                break
                
    except Exception as e:
        print(f"\n[ERROR] Exception during verification: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n--- Verification Summary ---")
    if swap_count >= 2:
        print(f"✅ SUCCESS: Verified {swap_count} model swaps in the logs.")
    else:
        print(f"❌ FAILED: Only found {swap_count} model swaps. Check logic.")

if __name__ == "__main__":
    asyncio.run(check_model_swaps())
