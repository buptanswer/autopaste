print("测试导入...")
try:
    import ctypes
    print("✓ ctypes")
except Exception as e:
    print(f"✗ ctypes: {e}")

try:
    import win32clipboard
    print("✓ win32clipboard")
except Exception as e:
    print(f"✗ win32clipboard: {e}")

try:
    import win32con
    print("✓ win32con")
except Exception as e:
    print(f"✗ win32con: {e}")

try:
    import keyboard
    print("✓ keyboard")
except Exception as e:
    print(f"✗ keyboard: {e}")

print("\n所有导入测试完成")
input("按回车键退出...")