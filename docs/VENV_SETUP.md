# NocoDB Python SDK 虚拟环境设置指南

## 概述
本文档提供NocoDB Python SDK项目的虚拟环境设置说明，确保开发环境的标准化和隔离。

## 虚拟环境状态
✅ 虚拟环境已创建：`.venv/`  
✅ 项目依赖已安装  
✅ 环境测试通过  

## 激活虚拟环境

### Linux / macOS (bash/zsh)
```bash
# 激活虚拟环境
source .venv/bin/activate

# 验证激活
python --version  # 应显示 Python 3.13.1
pip list          # 应显示项目依赖包
```

### Windows PowerShell
```powershell
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 验证激活
python --version  # 应显示 Python 3.13.1
pip list          # 应显示项目依赖包
```

### Windows 命令提示符 (CMD)
```cmd
# 激活虚拟环境
.venv\Scripts\activate.bat

# 验证激活
python --version
pip list
```

### 退出虚拟环境（所有环境）
```bash
deactivate
```

## 项目依赖管理

### 安装项目依赖
```bash
# 在虚拟环境激活状态下
pip install -e .
```

### 更新依赖
```bash
# 更新所有依赖到最新版本
pip install --upgrade -e .

# 更新特定包
pip install --upgrade requests
```

### 生成依赖列表
```bash
# 生成requirements.txt（可选）
pip freeze > requirements.txt
```

## 开发工作流

### 1. 开始开发

#### Linux / macOS
```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行项目测试套件
python -m pytest tests/
```

#### Windows PowerShell
```powershell
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1


# 运行项目测试套件
python -m pytest tests/
```

#### Windows CMD
```cmd
# 激活虚拟环境
.venv\Scripts\activate.bat

# 运行项目测试套件
python -m pytest tests/
```

### 2. 安装开发工具（可选）
```bash
# 安装代码质量工具
pip install black ruff pylint

# 安装测试工具
pip install pytest pytest-cov
```

### 3. VSCode集成
在VSCode中设置Python解释器：
1. 打开命令面板 (`Ctrl+Shift+P`)
2. 输入 "Python: Select Interpreter"
3. 选择虚拟环境的Python解释器：
   - **Windows**: `.venv\Scripts\python.exe`
   - **Linux/macOS**: `.venv/bin/python`

## 虚拟环境目录结构

### Windows 环境
```
.venv/
├── Scripts/           # Windows可执行文件
│   ├── python.exe     # 虚拟环境Python解释器
│   ├── pip.exe        # 虚拟环境包管理器
│   ├── activate.ps1   # PowerShell激活脚本
│   └── activate.bat   # CMD激活脚本
├── Lib/               # Python库文件
│   └── site-packages/ # 安装的第三方包
└── pyvenv.cfg        # 虚拟环境配置
```

### Linux/macOS 环境
```
.venv/
├── bin/               # 可执行文件
│   ├── python         # 虚拟环境Python解释器
│   ├── pip            # 虚拟环境包管理器
│   └── activate       # bash激活脚本
├── lib/               # Python库文件
│   └── python3.x/     # Python版本特定目录
│       └── site-packages/ # 安装的第三方包
└── pyvenv.cfg        # 虚拟环境配置
```

## 已安装的包
- `nocodb-py==0.0.0` - 本项目（可编辑模式）
- `requests==2.32.5` - HTTP客户端库
- `certifi==2025.11.12` - SSL证书
- `charset-normalizer==3.4.4` - 字符编码检测
- `idna==3.11` - 国际化域名处理
- `urllib3==2.6.2` - HTTP库

## 故障排除

### 常见问题
1. **激活脚本无法执行**
   - 解决方案：检查执行策略 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

2. **包导入错误**
   - 解决方案：重新安装依赖 `pip install -e .`

3. **Python版本不匹配**
   - 解决方案：确保使用Python 3.9+版本

### 重新创建虚拟环境

#### Linux / macOS
```bash
# 删除现有环境
rm -rf .venv

# 重新创建
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

#### Windows PowerShell
```powershell
# 删除现有环境
Remove-Item -Recurse -Force .venv

# 重新创建
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

#### Windows CMD
```cmd
# 删除现有环境
rmdir /s /q .venv

# 重新创建
python -m venv .venv
.venv\Scripts\activate.bat
pip install -e .
```

## 版本控制
虚拟环境目录 `.venv/` 已添加到 `.gitignore`，不应提交到版本控制。

## 环境验证
运行测试脚本验证环境完整性：

预期输出应包含：
- ✅ Python版本信息
- ✅ NocoDB SDK模块导入成功
- ✅ 依赖包版本信息
- ✅ 测试通过确认

### 多平台兼容性检查
确保以下命令在所有环境中都能正常工作：
- `python --version` - 显示正确的Python版本
- `pip list` - 显示已安装的包列表
- `python -c "import nocodb_py; print('SDK导入成功')"` - 验证SDK模块导入

---

*最后更新：2025-12-23*