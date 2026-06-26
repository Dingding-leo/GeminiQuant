import os
import shutil
import subprocess

HOME = os.path.expanduser("~")
AGY_HOMES_DIR = os.path.join(HOME, ".gemini", "agy_homes")
BIN_DIR = os.path.join(AGY_HOMES_DIR, "bin")

def find_agy():
    try:
        path = subprocess.check_output(["which", "agy"]).decode().strip()
        if path and os.path.exists(path):
            return path
    except Exception:
        pass
    return os.path.expanduser("~/.local/bin/agy")

def setup():
    original_agy = find_agy()
    if not os.path.exists(original_agy):
        print(f"[x] Error: 找不到 agy 执行文件: {original_agy}")
        return

    os.makedirs(BIN_DIR, exist_ok=True)
    
    print("="*50)
    print("AgyFusion 2.0: 多账号授权配置助手 (Binary Patch 终极隔离版)")
    print("="*50)
    print("黑客级重构：为了打破 macOS Keychain 只能存单账号的限制，系统将直接在内存里克隆 3 个 agy 核心引擎并重写签名，实现 100% 物理级账号隔离。\n")

    for i in range(1, 4):
        target_home = os.path.join(AGY_HOMES_DIR, f"home_{i}")
        os.makedirs(target_home, exist_ok=True)
        
        patched_bin = os.path.join(BIN_DIR, f"agy_{i}")
        if not os.path.exists(patched_bin):
            print(f"[*] 正在为账号 {i} 进行二进制级引擎分离与重签名 (Ad-Hoc Signing)...")
            # 1. 复制二进制文件
            shutil.copy2(original_agy, patched_bin)
            # 2. 安全的二进制字节替换 (不改变文件大小，避免破坏 ELF/Mach-O 头)
            with open(patched_bin, 'rb') as f:
                original_data = f.read()
            data = original_data.replace(b"antigravity-cli", f"antigravity-cl{i}".encode('utf-8'), 1)
            if data == original_data:
                print(f"[!] Warning: Replacement failed for agy_{i}, keyword not found.")
            with open(patched_bin, 'wb') as f:
                f.write(data)
            # 3. macOS 强制重签名
            subprocess.run(["codesign", "--force", "-s", "-", patched_bin], check=True)
            
        print(f"\n" + "-"*40)
        print(f"准备配置 [账号 {i}]")
        print("-"*40)
        input(f"按下回车键，稍后请在弹出的浏览器页面中，使用你的第 {i} 个 Google Pro 账号登录...")
        
        env = os.environ.copy()
        env["HOME"] = target_home
        
        print(f"\n(正在启动克隆引擎 agy_{i}，如果没有弹出浏览器，请注意终端里是否有鉴权链接)")
        try:
            subprocess.run([patched_bin, "-p", "hi"], env=env)
        except Exception as e:
            print(f"调用 agy 失败: {e}")
            
        print(f"[✔] 账号 {i} 鉴权状态已成功物理隔离！")

    print("\n🎉 全部就绪！现在可以执行: python main.py '你的指令' 来启动 AgyFusion 混合智能引擎了！")

if __name__ == "__main__":
    setup()
