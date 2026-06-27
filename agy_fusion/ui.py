import sys
import asyncio
import itertools

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    GREY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

async def spinner(message):
    chars = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    try:
        while True:
            # Clear line first to prevent trailing characters when message updates
            sys.stdout.write(f"\r\033[K{Colors.CYAN}{next(chars)}{Colors.RESET} {message}")
            sys.stdout.flush()
            await asyncio.sleep(0.08)
    except asyncio.CancelledError:
        pass

async def run_with_spinner(message, coro):
    spin_task = asyncio.create_task(spinner(message))
    try:
        res = await coro
        spin_task.cancel()
        sys.stdout.write(f"\r\033[K{Colors.GREEN}✔{Colors.RESET} {message} {Colors.GREY}(Done){Colors.RESET}\n")
        return res
    except Exception as e:
        spin_task.cancel()
        sys.stdout.write(f"\r\033[K{Colors.RED}✖{Colors.RESET} {message} {Colors.RED}(Failed){Colors.RESET}\n")
        raise

def print_header(text):
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}❖ {text}{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}{text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}{text}{Colors.RESET}")
    
def print_warning(text):
    print(f"{Colors.YELLOW}{text}{Colors.RESET}")

def print_step(text):
    print(f"{Colors.CYAN}➜{Colors.RESET} {text}")
