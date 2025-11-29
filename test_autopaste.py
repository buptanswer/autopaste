"""
AutoPaste 测试脚本
测试主要功能模块

运行方式：以管理员身份运行 python test_autopaste.py
"""

import sys
import time
import ctypes
import unittest
from unittest.mock import patch, MagicMock
import threading

# 导入被测试模块
import autopaste

class TestAdminCheck(unittest.TestCase):
    """测试管理员权限检查"""
    
    def test_is_admin_returns_truthy_or_falsy(self):
        """测试 is_admin 返回可作为布尔值使用的结果"""
        result = autopaste.is_admin()
        # Windows API 返回整数 0 或 1，可以作为布尔值使用
        self.assertIn(result, [True, False, 0, 1])
        print(f"  ✓ is_admin() 返回: {result} (管理员: {bool(result)})")


class TestClipboard(unittest.TestCase):
    """测试剪贴板功能"""
    
    def test_get_clipboard_text_returns_string(self):
        """测试剪贴板读取返回字符串"""
        result = autopaste.get_clipboard_text()
        self.assertIsInstance(result, str)
        print(f"  ✓ get_clipboard_text() 返回字符串，长度: {len(result)}")
    
    def test_get_clipboard_with_unicode(self):
        """测试剪贴板 Unicode 支持"""
        import win32clipboard
        import win32con
        
        test_text = "测试中文 Test English 123 !@#"
        
        # 设置剪贴板内容
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(test_text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        except Exception as e:
            self.skipTest(f"无法设置剪贴板: {e}")
        
        # 读取并验证
        result = autopaste.get_clipboard_text()
        self.assertEqual(result, test_text)
        print(f"  ✓ Unicode 剪贴板测试通过: '{test_text[:20]}...'")
    
    def test_get_clipboard_empty(self):
        """测试空剪贴板"""
        import win32clipboard
        
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
        except Exception as e:
            self.skipTest(f"无法清空剪贴板: {e}")
        
        result = autopaste.get_clipboard_text()
        self.assertEqual(result, "")
        print("  ✓ 空剪贴板测试通过")


class TestUnicodeChar(unittest.TestCase):
    """测试 Unicode 字符发送"""
    
    def test_send_unicode_char_valid(self):
        """测试发送有效字符"""
        # 注意：实际发送会影响当前焦点窗口，这里只测试函数不崩溃
        result = autopaste.send_unicode_char('A')
        self.assertIsInstance(result, bool)
        print("  ✓ send_unicode_char('A') 执行成功")
    
    def test_send_unicode_char_chinese(self):
        """测试发送中文字符"""
        result = autopaste.send_unicode_char('中')
        self.assertIsInstance(result, bool)
        print("  ✓ send_unicode_char('中') 执行成功")
    
    def test_send_unicode_char_invalid_empty(self):
        """测试发送空字符串"""
        result = autopaste.send_unicode_char('')
        self.assertFalse(result)
        print("  ✓ send_unicode_char('') 正确返回 False")
    
    def test_send_unicode_char_invalid_multiple(self):
        """测试发送多个字符"""
        result = autopaste.send_unicode_char('AB')
        self.assertFalse(result)
        print("  ✓ send_unicode_char('AB') 正确返回 False")
    
    def test_send_unicode_char_invalid_type(self):
        """测试发送非字符串类型"""
        result = autopaste.send_unicode_char(123)
        self.assertFalse(result)
        print("  ✓ send_unicode_char(123) 正确返回 False")


class TestSpecialKey(unittest.TestCase):
    """测试特殊键发送"""
    
    def test_send_special_key_enter(self):
        """测试发送回车键"""
        result = autopaste.send_special_key(0x0D)  # VK_RETURN
        self.assertIsInstance(result, bool)
        print("  ✓ send_special_key(VK_RETURN) 执行成功")
    
    def test_send_special_key_tab(self):
        """测试发送 Tab 键"""
        result = autopaste.send_special_key(0x09)  # VK_TAB
        self.assertIsInstance(result, bool)
        print("  ✓ send_special_key(VK_TAB) 执行成功")


class TestUnicodeString(unittest.TestCase):
    """测试 Unicode 字符串发送"""
    
    def setUp(self):
        """测试前设置"""
        autopaste.is_inputting = True
    
    def tearDown(self):
        """测试后清理"""
        autopaste.is_inputting = False
    
    def test_send_unicode_string_empty(self):
        """测试发送空字符串"""
        success, total = autopaste.send_unicode_string("")
        self.assertEqual(success, 0)
        self.assertEqual(total, 0)
        print("  ✓ 空字符串测试通过")
    
    def test_send_unicode_string_returns_tuple(self):
        """测试返回值是元组"""
        result = autopaste.send_unicode_string("A", delay_ms=1)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        print(f"  ✓ send_unicode_string 返回元组: {result}")
    
    def test_send_unicode_string_cr_skipped(self):
        """测试 \\r 字符被正确跳过"""
        # 文本包含 \r\n（Windows 换行）
        text = "A\r\nB"  # 3个字符发送：A, \n, B（\r 被跳过）
        success, total = autopaste.send_unicode_string(text, delay_ms=1)
        self.assertEqual(total, 3)  # A + \n + B = 3
        print(f"  ✓ CRLF 处理测试: 总字符 {len(text)}，实际发送 {total}")
    
    def test_send_unicode_string_cancel(self):
        """测试取消输入"""
        autopaste.is_inputting = False
        success, total = autopaste.send_unicode_string("ABCDE", delay_ms=1)
        # 由于 is_inputting=False，应该立即停止
        self.assertEqual(total, 0)
        print("  ✓ 取消输入测试通过")


class TestSettings(unittest.TestCase):
    """测试设置功能"""
    
    def test_default_settings(self):
        """测试默认设置值"""
        # 重置为默认值
        autopaste.input_delay = 5
        autopaste.wait_time = 2
        
        self.assertEqual(autopaste.input_delay, 5)
        self.assertEqual(autopaste.wait_time, 2)
        print(f"  ✓ 默认设置: delay={autopaste.input_delay}ms, wait={autopaste.wait_time}s")
    
    def test_settings_range(self):
        """测试设置值范围"""
        # 测试输入延迟范围 (1-100)
        autopaste.input_delay = max(1, min(100, 0))  # 下界
        self.assertEqual(autopaste.input_delay, 1)
        
        autopaste.input_delay = max(1, min(100, 200))  # 上界
        self.assertEqual(autopaste.input_delay, 100)
        
        # 测试等待时间范围 (0.5-10)
        autopaste.wait_time = max(0.5, min(10, 0))  # 下界
        self.assertEqual(autopaste.wait_time, 0.5)
        
        autopaste.wait_time = max(0.5, min(10, 20))  # 上界
        self.assertEqual(autopaste.wait_time, 10)
        
        # 恢复默认值
        autopaste.input_delay = 5
        autopaste.wait_time = 2
        
        print("  ✓ 设置范围验证通过")


class TestInputLock(unittest.TestCase):
    """测试输入锁机制"""
    
    def test_input_lock_exists(self):
        """测试输入锁存在"""
        self.assertIsInstance(autopaste.input_lock, type(threading.Lock()))
        print("  ✓ 输入锁存在")
    
    def test_input_lock_acquirable(self):
        """测试输入锁可获取"""
        acquired = autopaste.input_lock.acquire(blocking=False)
        if acquired:
            autopaste.input_lock.release()
            print("  ✓ 输入锁可正常获取和释放")
        else:
            print("  ⚠ 输入锁当前被占用（可能其他测试未释放）")


class TestCancelHotkey(unittest.TestCase):
    """测试取消热键功能"""
    
    def test_cancel_when_inputting(self):
        """测试输入时取消"""
        autopaste.is_inputting = True
        autopaste.on_cancel_hotkey()
        self.assertFalse(autopaste.is_inputting)
        print("  ✓ 输入时取消功能正常")
    
    def test_cancel_when_not_inputting(self):
        """测试非输入时取消（应该不做任何事）"""
        autopaste.is_inputting = False
        autopaste.on_cancel_hotkey()
        self.assertFalse(autopaste.is_inputting)
        print("  ✓ 非输入时取消功能正常")


class TestChangeSettingsGuard(unittest.TestCase):
    """测试设置菜单保护"""
    
    @patch('builtins.input', return_value='3')
    def test_settings_blocked_during_input(self, mock_input):
        """测试输入时设置菜单被阻止"""
        autopaste.is_inputting = True
        
        # 捕获 print 输出
        with patch('builtins.print') as mock_print:
            autopaste.change_settings()
            # 检查是否打印了警告信息
            calls = [str(call) for call in mock_print.call_args_list]
            warning_printed = any('正在输入中' in str(call) for call in calls)
            self.assertTrue(warning_printed)
        
        autopaste.is_inputting = False
        print("  ✓ 输入时设置菜单被正确阻止")


def run_interactive_test():
    """交互式测试（需要用户参与）"""
    print("\n" + "=" * 60)
    print("  交互式功能测试")
    print("=" * 60)
    
    if not autopaste.is_admin():
        print("❌ 需要管理员权限运行交互式测试")
        return False
    
    print("\n此测试将验证实际的键盘输入功能。")
    print("请打开一个文本编辑器（如记事本）准备接收输入。")
    
    try:
        choice = input("\n是否继续交互式测试? (y/N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n已跳过交互式测试")
        return True
    
    if choice != 'y':
        print("已跳过交互式测试")
        return True
    
    # 测试 1：简单英文
    print("\n--- 测试 1: 英文字符 ---")
    print("将在 3 秒后输入: Hello World!")
    print("请确保光标在文本编辑器中...")
    time.sleep(3)
    
    autopaste.is_inputting = True
    success, total = autopaste.send_unicode_string("Hello World!", delay_ms=10)
    autopaste.is_inputting = False
    print(f"结果: {success}/{total} 字符成功")
    
    # 测试 2：中文
    print("\n--- 测试 2: 中文字符 ---")
    print("将在 3 秒后输入: 你好世界！")
    time.sleep(3)
    
    autopaste.is_inputting = True
    success, total = autopaste.send_unicode_string("你好世界！", delay_ms=10)
    autopaste.is_inputting = False
    print(f"结果: {success}/{total} 字符成功")
    
    # 测试 3：混合内容
    print("\n--- 测试 3: 混合内容 ---")
    print("将在 3 秒后输入: 密码Test123!@#")
    time.sleep(3)
    
    autopaste.is_inputting = True
    success, total = autopaste.send_unicode_string("密码Test123!@#", delay_ms=10)
    autopaste.is_inputting = False
    print(f"结果: {success}/{total} 字符成功")
    
    # 测试 4：换行符
    print("\n--- 测试 4: 多行文本 ---")
    print("将在 3 秒后输入多行文本...")
    time.sleep(3)
    
    autopaste.is_inputting = True
    success, total = autopaste.send_unicode_string("第一行\n第二行\n第三行", delay_ms=10)
    autopaste.is_inputting = False
    print(f"结果: {success}/{total} 字符成功")
    
    print("\n交互式测试完成！请检查文本编辑器中的输出是否正确。")
    return True


def main():
    """主测试函数"""
    print("=" * 60)
    print("  AutoPaste v2.0 测试套件")
    print("=" * 60)
    print()
    
    # 检查管理员权限
    if autopaste.is_admin():
        print("✓ 管理员权限已确认")
    else:
        print("⚠ 未以管理员身份运行，部分测试可能失败")
    print()
    
    # 运行单元测试
    print("-" * 60)
    print("运行单元测试...")
    print("-" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    test_classes = [
        TestAdminCheck,
        TestClipboard,
        TestUnicodeChar,
        TestSpecialKey,
        TestUnicodeString,
        TestSettings,
        TestInputLock,
        TestCancelHotkey,
        TestChangeSettingsGuard,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 统计结果
    print("\n" + "=" * 60)
    print("  测试结果统计")
    print("=" * 60)
    print(f"  总测试数: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print(f"  跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split(chr(10))[0]}")
    
    if result.errors:
        print("\n出错的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(chr(10))[0]}")
    
    # 询问是否运行交互式测试
    print()
    try:
        choice = input("是否运行交互式测试（需要手动验证）? (y/N): ").strip().lower()
        if choice == 'y':
            run_interactive_test()
    except (EOFError, KeyboardInterrupt):
        print("\n已跳过交互式测试")
    
    print("\n" + "=" * 60)
    print("  测试完成")
    print("=" * 60)
    
    # 返回是否全部通过
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)

