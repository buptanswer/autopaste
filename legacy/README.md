# AutoPaste v1.0 (Legacy Version)

这是 AutoPaste v1.0 的备份版本。

## 📦 包含文件

- `autopaste.py` - v1.0 主程序
- `build.py` - v1.0 打包脚本
- `test_imports.py` - 依赖测试脚本
- `密码自动输入工具.spec` - PyInstaller 配置文件

## ℹ️ 版本信息

- **版本**: v1.0.0
- **发布日期**: 2025-11-27
- **状态**: 已归档（Legacy）

## 🔄 为什么保留 v1.0？

v1.0 使用 `pydirectinput` + `pyautogui` 实现，虽然已被 v2.0 替代，但保留作为：
1. 历史参考
2. 回退备份
3. 学习对比

## 🆕 升级到 v2.0

v2.0 有重大改进：
- ✅ 支持 Unicode/中文输入
- ✅ 更简洁的依赖（从5个减少到2个）
- ✅ 可配置的输入参数
- ✅ 更好的错误处理

查看主目录的 `升级到v2.0指南.md` 了解详情。

## 🔙 如何使用 v1.0

如果需要使用 v1.0：

```bash
# 复制到主目录
copy autopaste.py ..
copy build.py ..

# 打包
cd ..
python build.py
```

## 📝 v1.0 特性

- 硬件级键盘模拟（DirectInput）
- 支持游戏启动器（战网、Steam等）
- 热键：Ctrl+Alt+J
- 仅支持英文字符

## ⚠️ v1.0 限制

- ❌ 不支持中文
- ❌ 不支持 Unicode
- ❌ 依赖较多
- ❌ 无法运行时配置

## 📚 相关文档

- [CHANGELOG.md](../CHANGELOG.md) - 查看版本变更
- [升级到v2.0指南.md](../升级到v2.0指南.md) - 升级指南
- [README.md](../README.md) - 主项目文档

---

**归档时间**: 2025-11-27  
**当前版本**: v2.0.0  
**此版本**: v1.0.0