import ctypes
import time
import win32clipboard
import win32con
from ctypes import wintypes
import sys
import atexit
import threading

# 定义Windows API常量
INPUT_KEYBOARD = 1
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_KEYUP = 0x0002

# 定义结构体 - 修复 64 位 Windows 兼容性
# ULONG_PTR 在 64 位系统上是 8 字节，使用 c_void_p 来正确表示

class KEYBDINPUT(ctypes.Structure):
    """键盘输入结构体"""
    _fields_ = [
        ("wVk", wintypes.WORD),          # 2 bytes
        ("wScan", wintypes.WORD),        # 2 bytes
        ("dwFlags", wintypes.DWORD),     # 4 bytes
        ("time", wintypes.DWORD),        # 4 bytes
        ("dwExtraInfo", ctypes.c_void_p) # 8 bytes on 64-bit (ULONG_PTR)
    ]

class MOUSEINPUT(ctypes.Structure):
    """鼠标输入结构体 - 用于确保联合体大小正确"""
    _fields_ = [
        ("dx", wintypes.LONG),           # 4 bytes
        ("dy", wintypes.LONG),           # 4 bytes
        ("mouseData", wintypes.DWORD),   # 4 bytes
        ("dwFlags", wintypes.DWORD),     # 4 bytes
        ("time", wintypes.DWORD),        # 4 bytes
        ("dwExtraInfo", ctypes.c_void_p) # 8 bytes on 64-bit
    ]

class HARDWAREINPUT(ctypes.Structure):
    """硬件输入结构体"""
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD)
    ]

class INPUTUNION(ctypes.Union):
    """INPUT 联合体 - 包含所有输入类型以确保正确的大小"""
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT)
    ]

class INPUT(ctypes.Structure):
    """输入结构体"""
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
input_lock = threading.Lock()  # 线程锁，防止并发输入
is_inputting = False  # 标记是否正在输入

def is_admin():
    """检查是否以管理员身份运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except (AttributeError, OSError):
        # WindowsError 在 Python 3 中是 OSError 的别名
        return False

def send_unicode_char(char):
    """发送单个Unicode字符"""
    # 输入验证：检查字符是否有效
    if not isinstance(char, str) or len(char) != 1:
        return False
    
    try:
        # 按下键
        input_down = INPUT()
        input_down.type = INPUT_KEYBOARD
        input_down.union.ki.wVk = 0
        input_down.union.ki.wScan = ord(char)
        input_down.union.ki.dwFlags = KEYEVENTF_UNICODE
        input_down.union.ki.time = 0
        input_down.union.ki.dwExtraInfo = None
        
        # 释放键
        input_up = INPUT()
        input_up.type = INPUT_KEYBOARD
        input_up.union.ki.wVk = 0
        input_up.union.ki.wScan = ord(char)
        input_up.union.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
        input_up.union.ki.time = 0
        input_up.union.ki.dwExtraInfo = None
        
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
    """发送Unicode字符串，返回 (成功数, 实际需发送数)"""
    global is_inputting
    
    if delay_ms is None:
        delay_ms = input_delay
    
    if not text:
        return 0, 0
    
    success_count = 0
    total_to_send = 0  # 实际需要发送的字符数（不含 \r）
    
    for i, char in enumerate(text):
        # 检查是否应该取消输入
        if not is_inputting:
            print("\n⚠ 输入已取消")
            break
        
        # 处理特殊字符：换行符需要发送回车键
        if char == '\n':
            total_to_send += 1
            # 发送回车键 (VK_RETURN = 0x0D)
            if send_special_key(0x0D):
                success_count += 1
        elif char == '\r':
            # 回车符，跳过（通常与 \n 一起出现）
            continue
        elif char == '\t':
            total_to_send += 1
            # Tab键 (VK_TAB = 0x09)
            if send_special_key(0x09):
                success_count += 1
        else:
            total_to_send += 1
            # 普通字符
            if send_unicode_char(char):
                success_count += 1
        
        time.sleep(delay_ms / 1000.0)
        
        # 每50个字符显示一次进度
        if (i + 1) % 50 == 0:
            print(f"  进度: {i + 1}/{len(text)} 字符")
    
    return success_count, total_to_send

def send_special_key(vk_code):
    """发送特殊键（虚拟键码）"""
    try:
        # 按下键
        input_down = INPUT()
        input_down.type = INPUT_KEYBOARD
        input_down.union.ki.wVk = vk_code
        input_down.union.ki.wScan = 0
        input_down.union.ki.dwFlags = 0
        input_down.union.ki.time = 0
        input_down.union.ki.dwExtraInfo = None
        
        # 释放键
        input_up = INPUT()
        input_up.type = INPUT_KEYBOARD
        input_up.union.ki.wVk = vk_code
        input_up.union.ki.wScan = 0
        input_up.union.ki.dwFlags = KEYEVENTF_KEYUP
        input_up.union.ki.time = 0
        input_up.union.ki.dwExtraInfo = None
        
        # 发送输入
        inputs = (INPUT * 2)(input_down, input_up)
        result = SendInput(2, inputs, ctypes.sizeof(INPUT))
        
        return result == 2
    except Exception as e:
        print(f"发送特殊键出错: {e}")
        return False

def get_clipboard_text():
    """获取剪贴板文本，支持多种格式"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            win32clipboard.OpenClipboard()
            
            # 优先尝试 Unicode 文本格式
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                return text
            # 备选：尝试 ANSI 文本格式
            elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_TEXT)
                win32clipboard.CloseClipboard()
                # 将 ANSI 文本转换为 Unicode
                if isinstance(text, bytes):
                    try:
                        return text.decode('utf-8')
                    except UnicodeDecodeError:
                        return text.decode('gbk', errors='ignore')
                return text
            else:
                win32clipboard.CloseClipboard()
                return ""
        except Exception as e:
            # 确保关闭剪贴板
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                print(f"读取剪贴板失败: {e}")
                return ""
    return ""

def on_hotkey():
    """热键触发的处理函数（线程安全）"""
    global is_inputting
    
    # 使用锁防止并发执行
    if not input_lock.acquire(blocking=False):
        print(f"\n[{time.strftime('%H:%M:%S')}] ⚠ 上一次输入尚未完成，请稍候...")
        return
    
    try:
        print(f"\n[{time.strftime('%H:%M:%S')}] 检测到热键触发")
        
        # 获取剪贴板内容
        text = get_clipboard_text()
        
        if not text:
            print("❌ 剪贴板为空或无法读取")
            print("💡 请先用 Ctrl+C 复制要输入的内容")
            return
        
        # 显示预览（处理特殊字符）
        preview = text[:50].replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        if len(text) > 50:
            preview += "..."
        print(f"✓ 剪贴板内容: {preview}")
        print(f"✓ 总长度: {len(text)} 字符")
        print(f"⏱ 等待 {wait_time} 秒，请切换到目标输入框...")
        print("💡 提示: 等待或输入过程中可按 Ctrl+Alt+C 取消")
        
        # 设置输入标志，允许在等待期间取消
        is_inputting = True
        
        # 分段等待，显示倒计时
        waited = 0
        last_display = -1
        while waited < wait_time:
            if not is_inputting:
                print("\n⚠ 输入已取消")
                return
            # 显示倒计时（支持小于1秒的情况）
            remaining = wait_time - waited
            if wait_time < 1:
                # 短等待时间，显示一位小数
                display_val = round(remaining, 1)
                if display_val != last_display and display_val > 0:
                    print(f"\r⏱ 倒计时: {display_val:.1f} 秒...  ", end="", flush=True)
                    last_display = display_val
            else:
                # 正常等待时间，显示整数秒
                current_second = int(remaining) + 1 if remaining % 1 > 0 else int(remaining)
                if current_second != last_display and current_second > 0:
                    print(f"\r⏱ 倒计时: {current_second} 秒...  ", end="", flush=True)
                    last_display = current_second
            sleep_interval = min(0.1, wait_time - waited)
            time.sleep(sleep_interval)
            waited += sleep_interval
        print("\r" + " " * 30 + "\r", end="")  # 清除倒计时行
        
        # 再次检查是否被取消
        if not is_inputting:
            print("\n⚠ 输入已取消")
            return
        
        print("⌨ 开始输入...")
        start_time = time.time()
        
        success_count, total_count = send_unicode_string(text)
        
        elapsed_time = time.time() - start_time
        print(f"✓ 输入完成！")
        print(f"  - 成功: {success_count}/{total_count} 字符")
        print(f"  - 用时: {elapsed_time:.2f} 秒")
        print()
    finally:
        is_inputting = False
        input_lock.release()

def on_cancel_hotkey():
    """取消输入的热键处理函数"""
    global is_inputting
    # 无论当前状态如何，都尝试取消（并给出反馈）
    if is_inputting:
        is_inputting = False
        print(f"\n[{time.strftime('%H:%M:%S')}] ⚠ 收到取消信号，正在停止输入...")
    else:
        print(f"\n[{time.strftime('%H:%M:%S')}] ℹ 当前没有正在进行的输入")

def cleanup():
    """清理资源，注销热键"""
    global keyboard_module, registered_hotkeys
    
    if keyboard_module and registered_hotkeys:
        print("\n正在清理热键注册...")
        try:
            for hotkey in registered_hotkeys:
                keyboard_module.remove_hotkey(hotkey)
            registered_hotkeys.clear()
            print("✓ 热键已清理")
        except Exception as e:
            print(f"清理热键时出错: {e}")

def change_settings():
    """修改设置"""
    global input_delay, wait_time
    
    # 如果正在输入，不要打开设置菜单
    if is_inputting:
        print(f"\n[{time.strftime('%H:%M:%S')}] ⚠ 正在输入中，请等待输入完成后再修改设置")
        return
    
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
            except (ValueError, TypeError) as e:
                print(f"❌ 无效输入: {e}")
        
        elif choice == '2':
            new_wait = input(f"输入新的等待时间（秒，建议0.5-5，当前{wait_time}）: ").strip()
            try:
                wait_time = max(0.5, min(10, float(new_wait)))
                print(f"✓ 已设置为 {wait_time} 秒")
            except (ValueError, TypeError) as e:
                print(f"❌ 无效输入: {e}")
    except (EOFError, KeyboardInterrupt):
        # 修复：处理用户中断输入的情况
        print("\n设置已取消")
    except Exception as e:
        print(f"设置修改出错: {e}")

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
    
    # 导入依赖
    try:
        import keyboard
        keyboard_module = keyboard
    except ImportError:
        print("❌ 缺少 keyboard 模块")
        print("请手动执行: pip install keyboard pywin32")
        input("按回车键退出...")
        sys.exit(1)
    
    print("使用说明：")
    print("1. 复制要输入的内容到剪贴板")
    print("2. 点击目标输入框使其获得焦点")
    print("3. 按 Ctrl+Alt+P 开始自动输入")
    print("4. 按 Ctrl+Alt+C 取消正在进行的输入")
    print("5. 按 Ctrl+Alt+S 打开设置菜单")
    print("6. 按 Ctrl+Alt+Q 退出程序")
    print()
    print("提示：默认等待 2 秒后开始输入，给你时间切换窗口")
    print("=" * 60)
    print()
    
    # 注册清理函数
    atexit.register(cleanup)
    
    try:
        # 包装函数：在新线程中执行 on_hotkey，避免阻塞热键监听
        def on_hotkey_threaded():
            thread = threading.Thread(target=on_hotkey, daemon=True)
            thread.start()
        
        # 注册热键 Ctrl+Alt+P (很少冲突)
        hotkey_combo = 'ctrl+alt+p'
        keyboard_module.add_hotkey(hotkey_combo, on_hotkey_threaded, suppress=False)
        registered_hotkeys.append(hotkey_combo)
        
        # 注册取消输入热键 Ctrl+Alt+C
        cancel_hotkey_combo = 'ctrl+alt+c'
        keyboard_module.add_hotkey(cancel_hotkey_combo, on_cancel_hotkey, suppress=False)
        registered_hotkeys.append(cancel_hotkey_combo)
        
        # 注册设置热键 Ctrl+Alt+S
        settings_hotkey_combo = 'ctrl+alt+s'
        keyboard_module.add_hotkey(settings_hotkey_combo, change_settings, suppress=False)
        registered_hotkeys.append(settings_hotkey_combo)
        
        # 注册退出热键 Ctrl+Alt+Q
        quit_hotkey_combo = 'ctrl+alt+q'
        quit_flag = [False]  # 使用列表以便在闭包中修改
        def on_quit_hotkey():
            quit_flag[0] = True
        keyboard_module.add_hotkey(quit_hotkey_combo, on_quit_hotkey, suppress=False)
        registered_hotkeys.append(quit_hotkey_combo)
        
        print(f"✓ 热键已注册:")
        print(f"  - 触发输入: {hotkey_combo.upper()}")
        print(f"  - 取消输入: {cancel_hotkey_combo.upper()}")
        print(f"  - 打开设置: {settings_hotkey_combo.upper()}")
        print(f"  - 退出程序: {quit_hotkey_combo.upper()}")
        print(f"\n当前设置:")
        print(f"  - 输入延迟: {input_delay} 毫秒/字符")
        print(f"  - 切换等待: {wait_time} 秒")
        print("\n程序运行中（最小化窗口也可使用热键）...\n")
        
        # 主循环
        while True:
            try:
                if quit_flag[0]:
                    print("\n收到退出信号...")
                    break
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