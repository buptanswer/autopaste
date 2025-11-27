import ctypes
import time
import win32clipboard
import win32con
from ctypes import wintypes
import sys
import atexit

# 定义Windows API常量
INPUT_KEYBOARD = 1
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_KEYUP = 0x0002

# 定义结构体
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD)
    ]

class INPUTUNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT)
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUTUNION)
    ]

# 加载Windows API
user32 = ctypes.WinDLL('user32', use_last_error=True)
SendInput = user32.SendInput
SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
SendInput.restype = wintypes.UINT

# 全局变量
keyboard_module = None
registered_hotkeys = []
input_delay = 5  # 默认每个字符延迟5毫秒
wait_time = 2    # 默认等待2秒

def is_admin():
    """检查是否以管理员身份运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def send_unicode_char(char):
    """发送单个Unicode字符"""
    try:
        # 按下键
        input_down = INPUT()
        input_down.type = INPUT_KEYBOARD
        input_down.union.ki = KEYBDINPUT(
            wVk=0,
            wScan=ord(char),
            dwFlags=KEYEVENTF_UNICODE,
            time=0,
            dwExtraInfo=None
        )
        
        # 释放键
        input_up = INPUT()
        input_up.type = INPUT_KEYBOARD
        input_up.union.ki = KEYBDINPUT(
            wVk=0,
            wScan=ord(char),
            dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
            time=0,
            dwExtraInfo=None
        )
        
        # 发送输入
        inputs = (INPUT * 2)(input_down, input_up)
        result = SendInput(2, inputs, ctypes.sizeof(INPUT))
        
        if result != 2:
            print(f"警告: 字符 '{char}' 发送失败")
            return False
        return True
    except Exception as e:
        print(f"发送字符出错: {e}")
        return False

def send_unicode_string(text, delay_ms=None):
    """发送Unicode字符串"""
    if delay_ms is None:
        delay_ms = input_delay
    
    success_count = 0
    for i, char in enumerate(text):
        if send_unicode_char(char):
            success_count += 1
        time.sleep(delay_ms / 1000.0)
        
        # 每50个字符显示一次进度
        if (i + 1) % 50 == 0:
            print(f"  进度: {i + 1}/{len(text)} 字符")
    
    return success_count

def get_clipboard_text():
    """获取剪贴板文本"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                return text
            else:
                win32clipboard.CloseClipboard()
                return ""
        except Exception as e:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                print(f"读取剪贴板失败: {e}")
                return ""
    return ""

def on_hotkey():
    """热键触发的处理函数"""
    print(f"\n[{time.strftime('%H:%M:%S')}] 检测到热键触发")
    
    # 获取剪贴板内容
    text = get_clipboard_text()
    
    if not text:
        print("❌ 剪贴板为空或无法读取")
        return
    
    # 显示预览
    preview = text[:50] + "..." if len(text) > 50 else text
    print(f"✓ 剪贴板内容: {preview}")
    print(f"✓ 总长度: {len(text)} 字符")
    print(f"⏱ 等待 {wait_time} 秒，请切换到目标输入框...")
    
    time.sleep(wait_time)
    
    print("⌨ 开始输入...")
    start_time = time.time()
    
    success_count = send_unicode_string(text)
    
    elapsed_time = time.time() - start_time
    print(f"✓ 输入完成！")
    print(f"  - 成功: {success_count}/{len(text)} 字符")
    print(f"  - 用时: {elapsed_time:.2f} 秒")
    print()

def cleanup():
    """清理资源，注销热键"""
    global keyboard_module, registered_hotkeys
    
    if keyboard_module and registered_hotkeys:
        print("\n正在清理热键注册...")
        try:
            for hotkey in registered_hotkeys:
                keyboard_module.remove_hotkey(hotkey)
            registered_hotkeys.clear()  # 清空列表，防止重复清理
            print("✓ 热键已清理")
        except Exception as e:
            print(f"清理热键时出错: {e}")
    elif not registered_hotkeys:
        # 如果列表已空，说明已经清理过了，静默跳过
        pass

def show_settings():
    """显示当前设置"""
    print("\n当前设置:")
    print(f"  - 输入延迟: {input_delay} 毫秒/字符")
    print(f"  - 切换等待: {wait_time} 秒")
    print()

def change_settings():
    """修改设置"""
    global input_delay, wait_time
    
    print("\n=== 设置修改 ===")
    print("1. 修改输入延迟（当前: {} 毫秒）".format(input_delay))
    print("2. 修改等待时间（当前: {} 秒）".format(wait_time))
    print("3. 返回")
    
    try:
        choice = input("请选择 (1-3): ").strip()
        
        if choice == '1':
            new_delay = input(f"输入新的延迟时间（毫秒，建议1-20，当前{input_delay}）: ").strip()
            try:
                input_delay = max(1, min(100, int(new_delay)))
                print(f"✓ 已设置为 {input_delay} 毫秒")
            except:
                print("❌ 无效输入")
        
        elif choice == '2':
            new_wait = input(f"输入新的等待时间（秒，建议1-5，当前{wait_time}）: ").strip()
            try:
                wait_time = max(1, min(10, int(new_wait)))
                print(f"✓ 已设置为 {wait_time} 秒")
            except:
                print("❌ 无效输入")
    except:
        pass

def main():
    global keyboard_module, registered_hotkeys
    
    print("=" * 60)
    print("  底层键盘输入工具 v2.0 (管理员模式)")
    print("=" * 60)
    print()
    
    # 检查管理员权限
    if not is_admin():
        print("❌ 错误：此程序必须以管理员身份运行！")
        print("\n请右键点击 Python 或命令提示符，选择 '以管理员身份运行'")
        print("然后再执行此脚本\n")
        input("按回车键退出...")
        sys.exit(1)
    
    print("✓ 管理员权限已确认")
    print()
    
    # 检查并导入依赖
    try:
        import keyboard
        keyboard_module = keyboard
    except ImportError:
        print("缺少 keyboard 模块，正在尝试安装...")
        try:
            import os
            os.system("pip install keyboard")
            import keyboard
            keyboard_module = keyboard
            print("✓ keyboard 模块安装成功")
        except:
            print("❌ 安装失败，请手动执行: pip install keyboard")
            input("按回车键退出...")
            sys.exit(1)
    
    print("使用说明：")
    print("1. 复制要输入的内容到剪贴板")
    print("2. 点击目标输入框使其获得焦点")
    print("3. 按 Ctrl+Alt+P 开始自动输入")
    print("4. 按 S 键打开设置菜单")
    print("5. 按 ESC 退出程序")
    print()
    print("提示：默认等待 2 秒后开始输入，给你时间切换窗口")
    print("=" * 60)
    print()
    
    # 注册清理函数
    atexit.register(cleanup)
    
    try:
        # 注册热键 Ctrl+Alt+P (很少冲突)
        hotkey_combo = 'ctrl+alt+p'
        keyboard_module.add_hotkey(hotkey_combo, on_hotkey, suppress=False)
        registered_hotkeys.append(hotkey_combo)
        
        print(f"✓ 热键已注册: {hotkey_combo.upper()}")
        show_settings()
        print("程序运行中...\n")
        
        # 主循环
        while True:
            try:
                if keyboard_module.is_pressed('esc'):
                    print("\n收到退出信号...")
                    break
                elif keyboard_module.is_pressed('s'):
                    change_settings()
                    time.sleep(0.5)  # 防止重复触发
                time.sleep(0.1)
            except KeyboardInterrupt:
                break
        
    except Exception as e:
        print(f"错误: {e}")
        input("按回车键退出...")
    finally:
        cleanup()
        print("程序已安全退出")

if __name__ == "__main__":
    main()