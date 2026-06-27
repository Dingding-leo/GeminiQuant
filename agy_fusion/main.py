#!/usr/bin/env python3
import asyncio
import sys
import os

# Make sure we can import local modules regardless of cwd
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from tlb_cli import tlb
from orchestrator_cli import run_fusion
from ui import print_header, print_success, print_error, print_warning, print_step, Colors

async def process_task(task_description):
    print(f"\n{Colors.CYAN}{Colors.BOLD}Target:{Colors.RESET} {task_description}\n")
    blueprint = await run_fusion(task_description)
    
    if blueprint:
        print_header("ULTIMATE IMPLEMENTATION BLUEPRINT (AgyFusion 2.0)")
        print(blueprint)
        
        blueprint_path = os.path.join(os.getcwd(), "blueprint.md")
        with open(blueprint_path, "w") as f:
            f.write(blueprint)
        print_success(f"\n[*] Blueprint saved to {blueprint_path}")
    else:
        print_error("\n[!] Fusion process failed.")

async def main():
    print_step("Initializing Token Load Balancer (TLB)...")
    tlb.init_db()
    
    if len(sys.argv) > 1:
        # Join all arguments so quotes are not strictly required
        task_description = " ".join(sys.argv[1:])
        await process_task(task_description)
    else:
        # Interactive REPL mode
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}=================================================={Colors.RESET}")
        print(f"{Colors.MAGENTA}{Colors.BOLD}          AgyFusion 2.0 Interactive CLI           {Colors.RESET}")
        print(f"{Colors.MAGENTA}{Colors.BOLD}=================================================={Colors.RESET}")
        print(f"{Colors.GREY}Type your task and press Enter. (Type 'exit' to quit){Colors.RESET}")
        
        try:
            import readline
        except ImportError:
            pass
            
        while True:
            try:
                task_description = input(f"\n{Colors.GREEN}fusion>{Colors.RESET} ").strip()
                if not task_description:
                    continue
                if task_description.lower() in ['exit', 'quit']:
                    print_success("Goodbye!")
                    break
                await process_task(task_description)
            except (KeyboardInterrupt, EOFError):
                print_success("\nGoodbye!")
                break

if __name__ == "__main__":
    asyncio.run(main())
