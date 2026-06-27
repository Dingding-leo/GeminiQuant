import os
import time
import sqlite3
import json
from config import CONFIG_PATHS, DB_PATH, COOLDOWN_SECONDS
from ui import print_warning, print_error

class TokenLoadBalancer:
    def init_db(self):
        with sqlite3.connect(DB_PATH) as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS config_pool (
                    config_id TEXT PRIMARY KEY,
                    config_data TEXT,
                    status TEXT,
                    reset_timestamp REAL
                );
                CREATE TABLE IF NOT EXISTS rr_state (
                    id INTEGER PRIMARY KEY,
                    rr_index INTEGER
                );
            ''')
            for idx, path_dict in enumerate(CONFIG_PATHS):
                config_id = f"config_{idx+1}"
                db.execute('''
                    INSERT OR IGNORE INTO config_pool (config_id, config_data, status, reset_timestamp)
                    VALUES (?, ?, 'active', 0)
                ''', (config_id, json.dumps(path_dict)))
            db.commit()

    def get_active_config(self):
        current_time = time.time()
        with sqlite3.connect(DB_PATH) as db:
            # Wake up exhausted configs
            db.execute('''
                UPDATE config_pool 
                SET status = 'active', reset_timestamp = 0 
                WHERE status = 'exhausted' AND reset_timestamp <= ?
            ''', (current_time,))
            db.commit()

            cursor = db.execute("SELECT config_id, config_data FROM config_pool WHERE status = 'active' ORDER BY config_id")
            rows = cursor.fetchall()
                
        active_configs = [(row[0], json.loads(row[1])) for row in rows]
        
        if not active_configs:
            with sqlite3.connect(DB_PATH) as db:
                cursor = db.execute("SELECT MIN(reset_timestamp) FROM config_pool WHERE status = 'exhausted'")
                next_reset = cursor.fetchone()
            if next_reset and next_reset[0]:
                wait_time = max(0, next_reset[0] - current_time)
                raise Exception(f"All 3 Google Pro accounts are exhausted. Next available in {wait_time/60:.2f} minutes.")
            raise Exception("No active configurations found.")

        # Strict Round-Robin Load Balancing
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT rr_index FROM rr_state WHERE id = 1")
            row = cursor.fetchone()
            current_idx = int(row[0]) if row else 0
            
            selected = active_configs[current_idx % len(active_configs)]
            
            db.execute("INSERT OR REPLACE INTO rr_state (id, rr_index) VALUES (1, ?)", (current_idx + 1,))
            db.commit()
            
        # selected is a tuple (config_id, config_dict)
        config_dict = selected[1]
        config_dict['config_id'] = selected[0]
        return config_dict

    def mark_exhausted(self, config_dict: dict):
        reset_time = time.time() + COOLDOWN_SECONDS
        config_id = config_dict.get('config_id')
        
        if not config_id:
            print_error("mark_exhausted called without a config_id in the dict")
            return
            
        print_warning(f"Marking config {config_dict['home']} ({config_id}) as exhausted. Reset in {COOLDOWN_SECONDS/3600:.1f} hrs.")
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute('''
                UPDATE config_pool 
                SET status = 'exhausted', reset_timestamp = ? 
                WHERE config_id = ?
            ''', (reset_time, config_id))
            
            if cursor.rowcount == 0:
                print_error(f"mark_exhausted failed: {config_id} not found in DB.")
            
            db.commit()

tlb = TokenLoadBalancer()
