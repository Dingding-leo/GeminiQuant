import os

MODEL_SONNET = "claude-4.6-sonnet"
MODEL_OPUS = "claude-4.8-opus"
MODEL_GEMINI_PRO = "gemini-3.1-pro-high"
MODEL_GEMINI_FLASH = "gemini-3.5-flash-high"

# 为了绝对的物理隔离，我们将利用环境变量 HOME 进行进程欺骗，并结合 Binary Patch 引擎分离
USER_HOME = os.path.expanduser("~")
AGY_HOMES_DIR = os.path.join(USER_HOME, ".gemini", "agy_homes")
BIN_DIR = os.path.join(AGY_HOMES_DIR, "bin")

CONFIG_PATHS = [
    {
        "home": os.path.join(AGY_HOMES_DIR, "home_1"),
        "bin": os.path.join(BIN_DIR, "agy_1")
    },
    {
        "home": os.path.join(AGY_HOMES_DIR, "home_2"),
        "bin": os.path.join(BIN_DIR, "agy_2")
    },
    {
        "home": os.path.join(AGY_HOMES_DIR, "home_3"),
        "bin": os.path.join(BIN_DIR, "agy_3")
    }
]

DB_PATH = os.path.join(AGY_HOMES_DIR, "tlb_state.db")
COOLDOWN_SECONDS = 5 * 3600  # 5 hours
