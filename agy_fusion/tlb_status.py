import sqlite3
import time
import json
import math
from config import DB_PATH

def format_time(seconds):
    if seconds <= 0:
        return "READY"
    hours = math.floor(seconds / 3600)
    minutes = math.floor((seconds % 3600) / 60)
    secs = math.floor(seconds % 60)
    return f"{hours:02d}h {minutes:02d}m {secs:02d}s"

def show_status():
    print("=" * 60)
    print(" " * 15 + "AGY FUSION TOKEN LOAD BALANCER")
    print("=" * 60)
    
    current_time = time.time()
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT config_id, status, reset_timestamp, config_data FROM config_pool ORDER BY config_id")
            rows = cursor.fetchall()
            
            if not rows:
                print("[!] TLB Database is empty. Please run a task to initialize.")
                return

            print(f"{'ACCOUNT ID':<12} | {'STATUS':<12} | {'COOLDOWN TIME LEFT':<20}")
            print("-" * 60)
            
            for row in rows:
                config_id = row[0]
                status = row[1]
                reset_timestamp = row[2]
                
                # Check if an exhausted account is actually ready now
                if status == 'exhausted' and current_time >= reset_timestamp:
                    status = 'active'
                    reset_timestamp = 0
                
                time_left = max(0, reset_timestamp - current_time)
                
                # Colors
                green = "\033[92m"
                red = "\033[91m"
                reset = "\033[0m"
                
                status_color = green if status == 'active' else red
                status_text = f"{status_color}{status.upper()}{reset}"
                
                time_str = format_time(time_left)
                if status == 'active':
                    time_str = f"{green}N/A{reset}"
                else:
                    time_str = f"{red}{time_str}{reset}"
                
                print(f"{config_id:<12} | {status_text:<21} | {time_str:<20}")
                
    except sqlite3.OperationalError:
        print("[!] Cannot open TLB Database. Have you run any tasks yet?")
        
    print("=" * 60)

if __name__ == '__main__':
    show_status()
