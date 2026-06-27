#!/usr/bin/env python3
import asyncio
import sys
import os
import logging

# Make sure we can import local modules regardless of cwd
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from tlb_cli import tlb
from orchestrator_cli import run_fusion

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

async def main():
    if len(sys.argv) < 2:
        print("Usage: fusion '<task_description>'")
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
        
        blueprint_path = os.path.join(os.getcwd(), "blueprint.md")
        with open(blueprint_path, "w") as f:
            f.write(blueprint)
        print(f"\n[*] Blueprint saved to {blueprint_path}")
    else:
        print("\n[!] Fusion process failed.")

if __name__ == "__main__":
    asyncio.run(main())
