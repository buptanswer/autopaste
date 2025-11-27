"""
一键打包脚本 - 将Python脚本打包成exe可执行文件
使用方法：直接运行此脚本即可
"""

import os
import sys
import shutil
import subprocess

# 配置项
SCRIPT_NAME = "autopaste.py"              # 要打包的脚本名称
OUTPUT_NAME = "密码自动输入工具"           # 生成的exe名称
ICON_FILE = None                          # 图标文件（可选），如 "app.ico" 或 None

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(msg):
    """打印步骤信息"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}>>> {msg}{Colors.END}")

def print_success(msg):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_warning(msg):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def check_file_exists(filename):
    """检查文件是否存在"""
    if not os.path.exists(filename):
        print_error(f"找不到文件: {filename}")
        return False
    return True

def install_pyinstaller():
    """安装PyInstaller"""
    print_step("检查 PyInstaller...")
    try:
        import PyInstaller
        print_success("PyInstaller 已安装")
        return True
    except ImportError:
        print_warning("PyInstaller 未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print_success("PyInstaller 安装成功")
            return True
        except subprocess.CalledProcessError:
            print_error("PyInstaller 安装失败")
            return False

def check_dependencies():
    """检查必要的依赖是否已安装"""
    print_step("检查依赖...")
    
    required_modules = {
        'pywin32': ['win32clipboard', 'win32con'],
        'keyboard': ['keyboard'],
    }
    
    missing_packages = []
    
    for package, modules in required_modules.items():
        for module in modules:
            try:
                __import__(module)
                print_success(f"{module} 已安装")
            except ImportError:
                print_error(f"{module} 未安装")
                if package not in missing_packages:
                    missing_packages.append(package)
    
    if missing_packages:
        print_warning(f"\n缺少以下依赖包: {', '.join(missing_packages)}")
        choice = input("是否自动安装? (Y/n): ").strip().lower()
        
        if choice != 'n':
            for package in missing_packages:
                print(f"\n正在安装 {package}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print_success(f"{package} 安装成功")
                except subprocess.CalledProcessError:
                    print_error(f"{package} 安装失败")
                    return False
        else:
            print_error("缺少必要依赖，无法继续")
            return False
    
    return True

def clean_build_files():
    """清理之前的构建文件"""
    print_step("清理旧的构建文件...")
    dirs_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = [f"{OUTPUT_NAME}.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print_success(f"已删除: {dir_name}/")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print_success(f"已删除: {file_name}")

def build_exe():
    """构建exe文件"""
    print_step("开始打包...")
    
    # 构建PyInstaller命令（使用python -m调用，兼容性更好）
    cmd = [
        sys.executable,           # 当前Python解释器
        "-m", "PyInstaller",      # 作为模块调用
        "--onefile",              # 单文件模式
        "--uac-admin",            # 请求管理员权限
        "--clean",                # 清理临时文件
        "--name", OUTPUT_NAME,    # 输出文件名
        # 不使用 --noconsole，保留控制台查看错误
    ]
    
    # 添加图标（如果有）
    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd.extend(["--icon", ICON_FILE])
        print_success(f"使用图标: {ICON_FILE}")
    
    # 添加隐藏导入（确保这些模块被打包）
    hidden_imports = [
        "win32clipboard",
        "win32con",
        "keyboard",
        "ctypes",
        "ctypes.wintypes",
    ]
    for module in hidden_imports:
        cmd.extend(["--hidden-import", module])
    
    # 排除不需要的模块以减小体积（但不排除我们需要的）
    exclude_modules = [
        "matplotlib", "numpy", "pandas", "scipy", 
        "tkinter", "pytest", "IPython"
    ]
    for module in exclude_modules:
        cmd.extend(["--exclude-module", module])
    
    # 添加脚本名称
    cmd.append(SCRIPT_NAME)
    
    # 显示完整命令
    print(f"\n执行命令: {' '.join(cmd)}\n")
    print("-" * 60)
    
    try:
        # 执行打包
        subprocess.check_call(cmd)
        print("-" * 60)
        print_success("打包完成！")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"打包失败: {e}")
        return False

def get_file_size(filepath):
    """获取文件大小（MB）"""
    size_bytes = os.path.getsize(filepath)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb

def show_result():
    """显示打包结果"""
    print_step("打包结果")
    
    exe_path = os.path.join("dist", f"{OUTPUT_NAME}.exe")
    
    if os.path.exists(exe_path):
        size_mb = get_file_size(exe_path)
        abs_path = os.path.abspath(exe_path)
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*60}")
        print(f"  打包成功！")
        print(f"{'='*60}{Colors.END}\n")
        print(f"📁 文件位置: {abs_path}")
        print(f"📊 文件大小: {size_mb:.2f} MB")
        print(f"\n{Colors.YELLOW}使用方法:{Colors.END}")
        print(f"  1. 右键点击 {OUTPUT_NAME}.exe")
        print(f"  2. 选择 '以管理员身份运行'")
        print(f"  3. 按 Ctrl+Alt+P 触发自动输入")
        print(f"\n{Colors.GREEN}可以直接发送给其他人使用，无需Python环境！{Colors.END}\n")
        
        # 提示如何减小体积
        if size_mb > 20:
            print_warning(f"文件较大({size_mb:.2f} MB)，可以尝试以下方法减小体积：")
            print("  - 使用 UPX 压缩")
            print("  - 使用 Nuitka 代替 PyInstaller")
            print("  - 移除不需要的依赖库\n")
        
        return True
    else:
        print_error("未找到生成的exe文件")
        return False

def open_dist_folder():
    """打开dist文件夹"""
    dist_path = os.path.abspath("dist")
    if os.path.exists(dist_path):
        try:
            if sys.platform == "win32":
                os.startfile(dist_path)
                print_success("已打开dist文件夹")
            else:
                print(f"dist文件夹位置: {dist_path}")
        except Exception as e:
            print_warning(f"无法打开文件夹: {e}")

def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  Python 项目一键打包工具")
    print(f"{'='*60}{Colors.END}\n")
    
    # 1. 检查源文件
    print_step("检查源文件...")
    if not check_file_exists(SCRIPT_NAME):
        print_error("请确保脚本文件与此打包脚本在同一目录")
        input("\n按回车键退出...")
        return
    print_success(f"找到源文件: {SCRIPT_NAME}")
    
    # 2. 安装PyInstaller
    if not install_pyinstaller():
        input("\n按回车键退出...")
        return
    
    # 3. 检查依赖
    if not check_dependencies():
        input("\n按回车键退出...")
        return
    
    # 4. 清理旧文件
    clean_build_files()
    
    # 5. 开始打包
    if not build_exe():
        print_error("打包失败，请查看上方错误信息")
        input("\n按回车键退出...")
        return
    
    # 6. 显示结果
    if show_result():
        # 7. 询问是否打开文件夹
        try:
            choice = input(f"\n是否打开生成文件所在文件夹? (Y/n): ").strip().lower()
            if choice != 'n':
                open_dist_folder()
        except KeyboardInterrupt:
            print("\n")
    
    print(f"\n{Colors.BOLD}完成！{Colors.END}")
    input("\n按回车键退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}用户取消操作{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"发生错误: {e}")
        input("\n按回车键退出...")
        sys.exit(1)