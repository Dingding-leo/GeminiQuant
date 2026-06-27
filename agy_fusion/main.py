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

async def process_task(task_description):
    print(f"\n[*] Task: {task_description}")
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

async def main():
    print("[*] Initializing Token Load Balancer (TLB)...")
    tlb.init_db()
    
    if len(sys.argv) > 1:
        # Join all arguments so quotes are not strictly required
        task_description = " ".join(sys.argv[1:])
        await process_task(task_description)
    else:
        # Interactive REPL mode
        print("="*50)
        print("AgyFusion 2.0 Interactive CLI")
        print("="*50)
        print("Type your task and press Enter. (Type 'exit', Ctrl+C, or Ctrl+D to quit)")
        try:
            import readline
        except ImportError:
            pass
            
        while True:
            try:
                task_description = input("\nfusion> ").strip()
                if not task_description:
                    continue
                if task_description.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                await process_task(task_description)
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    asyncio.run(main())
