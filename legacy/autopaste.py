import pyautogui
import pyperclip
import keyboard
import time
import sys
import os
import subprocess
import ctypes

# ================= 配置区 =================
# 按键按下到松开的持续时间（非常重要，太短会被忽略）
KEY_HOLD_DURATION = 0.08

# 两个字符之间的间隔时间
KEY_INTERVAL = 0.1
# =========================================

def install(package):
    """自动调用 pip 安装缺失的库"""
    print(f"🔄 正在尝试自动安装 '{package}'...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ '{package}' 安装成功！")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ '{package}' 自动安装失败。")
        return False

def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_environment():
    """环境与权限自检"""
    print("=" * 60)
    print(f"🔍 当前运行环境: {sys.executable}")
    
    if is_admin():
        print("✅ 权限检查通过：当前已拥有管理员权限。")
    else:
        print("⛔ 严重警告：当前【未拥有】管理员权限！")
        print("   启动器会直接屏蔽非管理员的输入信号。")
        print("👉 请关闭，右键选择【以管理员身份运行】。")
    
    if ".venv" not in sys.executable and "venv" not in sys.executable:
        print("⚠️ 提示: 使用全局 Python 环境。")
    print("-" * 60)

check_environment()

# 尝试导入 pydirectinput
try:
    import pydirectinput
except ImportError:
    if install("pydirectinput"):
        import pydirectinput
    else:
        HAS_DIRECTINPUT = False

if 'pydirectinput' in sys.modules:
    HAS_DIRECTINPUT = True
    # 禁用 pydirectinput 默认的自动暂停，由我们手动控制
    pydirectinput.PAUSE = 0.0
else:
    HAS_DIRECTINPUT = False

def press_key_hardware(char):
    """
    使用 pydirectinput 进行底层的硬件级模拟。
    手动处理特殊符号的 Shift 组合，因为游戏引擎通常不识别组合键字符串。
    """
    # 常用符号映射表：需要按住 Shift 才能输入的字符
    # 注意：这基于标准美式键盘布局
    SHIFT_MAP = {
        '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
        '_': '-', '+': '=', '{': '[', '}': ']', '|': '\\', ':': ';', '"': "'", '<': ',', '>': '.', '?': '/',
        '~': '`'
    }

    try:
        if char.isupper():
            # 大写字母：按住 Shift -> 按字母 -> 松开 Shift
            pydirectinput.keyDown('shift')
            time.sleep(0.02)
            pydirectinput.keyDown(char.lower())
            time.sleep(KEY_HOLD_DURATION) # 保持按住
            pydirectinput.keyUp(char.lower())
            time.sleep(0.02)
            pydirectinput.keyUp('shift')
            
        elif char in SHIFT_MAP:
            # 特殊符号：按住 Shift -> 按对应按键 -> 松开 Shift
            mapped_key = SHIFT_MAP[char]
            pydirectinput.keyDown('shift')
            time.sleep(0.02)
            pydirectinput.keyDown(mapped_key)
            time.sleep(KEY_HOLD_DURATION)
            pydirectinput.keyUp(mapped_key)
            time.sleep(0.02)
            pydirectinput.keyUp('shift')
            
        else:
            # 普通字符（小写字母、数字）
            pydirectinput.keyDown(char)
            time.sleep(KEY_HOLD_DURATION) # 保持按住
            pydirectinput.keyUp(char)
            
    except Exception as e:
        print(f"⚠️ 无法识别的字符 '{char}'，尝试通用输入...")
        try:
            pydirectinput.press(char)
        except:
            pass

def type_clipboard_content():
    try:
        text = pyperclip.paste()
        if not text:
            print("❌ 剪贴板为空！")
            return

        print(f"⚡ 准备输入 (长度: {len(text)})...")
        print("   请勿触碰鼠标键盘...")
        
        time.sleep(0.5)
        
        # 确保修饰键释放
        if HAS_DIRECTINPUT:
            pydirectinput.keyUp('ctrl')
            pydirectinput.keyUp('alt')
            pydirectinput.keyUp('shift')
        
        # 强制点击聚焦点
        if HAS_DIRECTINPUT:
            pydirectinput.click()
        else:
            pyautogui.click()
            
        time.sleep(0.2) # 给一点时间让输入框响应点击

        print("⚡ 正在执行硬件模拟输入...")
        
        for char in text:
            if HAS_DIRECTINPUT:
                # 强制使用硬件模拟逻辑
                press_key_hardware(char)
            else:
                # 降级方案
                pyautogui.write(char)
            
            # 字符间隔
            time.sleep(KEY_INTERVAL)
        
        print("✅ 输入完成！")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("   自动模拟输入工具 (强制硬件模拟版)   ")
    print("-" * 60)
    print("⚠️ 专治各种顽固启动器 (战网/Steam/Vanguard等)")
    print("1. 必须管理员权限运行")
    print("2. 本版本已移除 keyboard 库的软输入，强制使用 ScanCode")
    print("3. 输入速度较慢是正常的，为了欺骗反作弊检测")
    print("-" * 60)
    
    if not is_admin():
        print("\n🛑 警告：没有管理员权限，硬件模拟大概率失效！\n")

    print("🚀 等待快捷键 [ Ctrl+Alt+J ] ... (ESC退出)")

    keyboard.add_hotkey('ctrl+alt+j', type_clipboard_content)
    keyboard.wait('esc')
    print("\n👋 程序已退出。")

if __name__ == "__main__":
    main()