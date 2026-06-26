import asyncio
import sys
import logging
from tlb_cli import tlb
from orchestrator_cli import run_fusion

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

async def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py '<task_description>'")
        sys.exit(1)
        
    task_description = sys.argv[1]
    
    print("[*] Initializing Token Load Balancer (TLB)...")
    tlb.init_db()
    
    print(f"[*] Task: {task_description}")
    blueprint = await run_fusion(task_description)
    
    if blueprint:
        print("\n" + "="*50)
        print("ULTIMATE IMPLEMENTATION BLUEPRINT (AgyFusion 2.0)")
        print("="*50)
        print(blueprint)
        
        with open("blueprint.md", "w") as f:
            f.write(blueprint)
        print("\n[*] Blueprint saved to blueprint.md")
    else:
        print("\n[!] Fusion process failed.")

if __name__ == "__main__":
    asyncio.run(main())
