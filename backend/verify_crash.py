import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.simulation import SimulationOrchestrator

async def verify_crash():
    print("Starting crash verification...")
    
    # Initialize simulation: PMM scenario, Large tier, aiDAPTIV+ DISABLED
    orchestrator = SimulationOrchestrator("pmm", "large", aidaptiv_enabled=False)
    
    crash_event_received = False
    
    print("Running simulation...")
    try:
        async for event in orchestrator.run_simulation():
            if event["type"] == "crash":
                print("\n✅ Crash event received!")
                print(f"Reason: {event['data']['reason']}")
                print(f"Processed: {event['data']['processed_documents']}/{event['data']['total_documents']}")
                print(f"VRAM Peak: {event['data']['memory_snapshot']['unified_gb']} GB")
                
                # Assertions
                assert event['data']['processed_documents'] > 0, "Should have processed some documents"
                assert event['data']['required_vram_gb'] >= 24.0, "Required VRAM should be high"
                
                crash_event_received = True
                break
            
            elif event["type"] == "progress":
                # Optional: print progress dots
                print(".", end="", flush=True)
                
    except Exception as e:
        print(f"\n❌ Exception during simulation: {e}")
        return

    if crash_event_received:
        print("\n✅ Verification SUCCESS: System crashed as expected.")
    else:
        print("\n❌ Verification FAILED: Simulation completed without crashing.")

if __name__ == "__main__":
    asyncio.run(verify_crash())
