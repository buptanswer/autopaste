# 🎮 AutoPaste - 游戏启动器密码自动输入工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://www.microsoft.com/windows)
[![Python: 3.7+](https://img.shields.io/badge/Python-3.7+-green.svg)](https://www.python.org/)
[![Version: 2.0.1](https://img.shields.io/badge/Version-2.0.1-brightgreen.svg)](https://github.com/buptanswer/autopaste/releases)

一个专门为游戏启动器（战网、Steam、Riot Vanguard等）设计的自动输入工具，使用纯 Windows API 实现，支持 Unicode 多语言输入。

> **作者**: [buptanswer](https://github.com/buptanswer)
> **仓库**: [autopaste](https://github.com/buptanswer/autopaste)
> **当前版本**: v2.0.1 | [更新日志](CHANGELOG.md) | [v1.0 备份](legacy/)

## 🎉 v2.0 重大更新

- 🌏 **Unicode 支持**：现在可以输入中文、日文、韩文等多语言字符！
- ⚡ **性能优化**：使用纯 Windows API，更快更稳定
- 🎛️ **运行时配置**：按 `Ctrl+Alt+S` 可调整输入延迟和等待时间
- ⏹️ **取消功能**：按 `Ctrl+Alt+C` 可随时取消正在进行的输入
- 📊 **进度显示**：长文本输入时显示实时倒计时和进度
- 🔧 **依赖简化**：从 5 个依赖减少到 2 个

查看 [CHANGELOG.md](CHANGELOG.md) 了解完整变更 | [从 v1.0 升级](升级到v2.0指南.md)

## ✨ 特性

- 🌏 **Unicode 支持**：支持中文、日文、韩文等多语言字符输入（v2.0 新增）
- 🔐 **底层 API 实现**：使用 Windows SendInput API，不会被反作弊系统检测
- 🎯 **专治顽固启动器**：支持战网、Steam、Riot Vanguard 等各种游戏启动器
- ⚡ **快捷键触发**：`Ctrl+Alt+P` 一键自动输入剪贴板内容
- 🎛️ **运行时配置**：按 `Ctrl+Alt+S` 调整输入延迟（1-100ms）和等待时间（0.5-10s）
- 🛡️ **管理员权限**：自动请求管理员权限，确保输入有效
- 📊 **进度显示**：长文本输入时每 50 个字符显示一次进度
- 📦 **开箱即用**：提供打包好的 exe 文件，无需 Python 环境

## 🚀 快速开始

### 方式一：直接使用（推荐）

1. 从 [Releases](https://github.com/buptanswer/autopaste/releases) 页面下载最新版本的 `密码自动输入工具.exe`
2. **右键点击** exe 文件，选择 **"以管理员身份运行"**
3. 复制你要输入的内容到剪贴板（Ctrl+C）- 支持中文！
4. 切换到需要输入的窗口（如游戏启动器登录框）
5. 按下 `Ctrl+Alt+P` 触发自动输入（默认等待 2 秒）
6. 按 `Ctrl+Alt+S` 可以调整设置
7. 按 `Ctrl+Alt+Q` 退出程序

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/buptanswer/autopaste.git
cd autopaste

# 安装依赖（v2.0 只需要 2 个）
pip install keyboard pywin32

# 以管理员身份运行
python autopaste.py
```

## 📋 系统要求

- **操作系统**：Windows 7/8/10/11
- **权限**：必须以管理员身份运行
- **Python**（仅源码运行）：Python 3.7 或更高版本

## 🎯 使用场景

- ✅ 战网（Battle.net）登录
- ✅ Steam 登录
- ✅ Riot Games（英雄联盟、Valorant）
- ✅ Epic Games Launcher
- ✅ Origin / EA App
- ✅ 其他使用反作弊系统的游戏启动器

## ⚙️ 配置说明

### 运行时配置（v2.0 新增）

程序运行时按 `Ctrl+Alt+S` 打开设置菜单：

1. **输入延迟**：调整每个字符的输入间隔（1-100ms，默认 5ms）
2. **等待时间**：调整触发后的等待时间（0.5-10s，默认 2s）

### 代码配置

也可以在 [`autopaste.py`](autopaste.py) 中修改默认值：

```python
input_delay = 5  # 默认每个字符延迟5毫秒
wait_time = 2    # 默认等待2秒
```

## 🔧 开发者指南

### 项目结构

```
autopaste/
├── autopaste.py          # 主程序
├── build.py              # 一键打包脚本
├── README.md             # 项目说明
├── CHANGELOG.md          # 版本变更日志
├── 升级到v2.0指南.md      # v2.0 升级指南
├── LICENSE               # 开源许可证
├── legacy/               # v1.0 备份
│   ├── autopaste.py      # v1.0 主程序
│   ├── build.py          # v1.0 打包脚本
│   └── README.md         # v1.0 说明
└── .gitignore           # Git 忽略文件
```

### 打包为 exe

```bash
# 方式一：使用自动打包脚本（推荐）
python build.py

# 方式二：手动使用 PyInstaller
pyinstaller --onefile --uac-admin --name 密码自动输入工具 autopaste.py
```

### 依赖库（v2.0）

- `keyboard` - 键盘事件监听
- `pywin32` - Windows API 调用（剪贴板）

**注意**：v2.0 使用纯 Windows API（ctypes + SendInput），不再需要 pyautogui、pyperclip、pydirectinput。

## ⚠️ 注意事项

1. **必须以管理员身份运行**，否则输入会被启动器屏蔽
2. **输入速度较慢是正常的**，这是为了模拟真实打字，避免被反作弊检测
3. **触发输入后请勿移动鼠标**，等待输入完成
4. **仅支持标准美式键盘布局**的特殊符号映射
5. **仅用于个人合法用途**，请勿用于非法目的

## 🐛 常见问题

### Q: 为什么必须管理员权限？
A: 游戏启动器通常以管理员权限运行，普通权限的程序无法向其发送输入信号。

### Q: 输入速度能加快吗？
A: 可以在运行时按 `Ctrl+Alt+S` 修改 `input_delay` 参数，但太快可能被反作弊系统检测为脚本。

### Q: 支持中文输入吗？
A: **v2.0 已支持！** 现在可以输入中文、日文、韩文等 Unicode 字符。

### Q: 为什么有时候输入失败？
A: 确保：
- 以管理员身份运行
- 输入框已获得焦点
- 没有其他程序占用键盘

## 📄 开源许可

本项目采用 [MIT License](LICENSE) 开源协议。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/buptanswer/autopaste/issues)
- 发送邮件至：1404498804@qq.com

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐️

---

**免责声明**：本工具仅供学习和个人合法使用，使用者需自行承担使用风险。作者不对任何滥用行为负责。