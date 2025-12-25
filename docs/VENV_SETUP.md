# NocoDB Python SDK 虚拟环境设置指南

## 概述
本文档为NocoDB Python SDK项目提供完整的虚拟环境建立指导，帮助开发者在不同计算机上快速设置标准化的开发环境。

## 前置条件
在开始设置之前，请确保满足以下要求：

### Python版本要求
- **Python 3.9+**：项目需要Python 3.9或更高版本
- 验证Python版本：`python --version` 或 `python3 --version`

### 系统要求
- **Windows**：Windows 10/11，PowerShell 5.1+ 或 CMD
- **Linux/macOS**：bash或zsh shell环境
- **磁盘空间**：至少100MB可用空间

### 包管理器
- **pip**：确保pip包管理器可用
- 验证pip：`pip --version` 或 `pip3 --version`

## 创建虚拟环境

### 步骤1：创建虚拟环境目录

#### Linux / macOS (bash/zsh)
```bash
# 创建虚拟环境
python -m venv .venv

# 验证创建成功
ls -la .venv/
```

#### Windows PowerShell
```powershell
# 创建虚拟环境
python -m venv .venv

# 验证创建成功
Get-ChildItem .venv/
```

#### Windows 命令提示符 (CMD)
```cmd
# 创建虚拟环境
python -m venv .venv

# 验证创建成功
dir .venv
```

### 步骤2：激活虚拟环境

#### Linux / macOS (bash/zsh)
```bash
# 激活虚拟环境
source .venv/bin/activate

# 验证激活（提示符应显示虚拟环境名称）
echo $VIRTUAL_ENV
```

#### Windows PowerShell
```powershell
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 验证激活（提示符应显示虚拟环境名称）
$env:VIRTUAL_ENV
```

#### Windows 命令提示符 (CMD)
```cmd
# 激活虚拟环境
.venv\Scripts\activate.bat

# 验证激活（提示符应显示虚拟环境名称）
echo %VIRTUAL_ENV%
```

### 退出虚拟环境（所有环境）
```bash
deactivate
```

## 安装项目依赖

### 步骤3：安装基础依赖
在虚拟环境激活状态下，安装项目依赖：

```bash
# 安装项目核心依赖
pip install -e .
```

### 步骤4：安装开发工具（推荐）
```bash
# 安装开发依赖（代码质量、测试工具）
pip install -e .[dev]
```

开发依赖包括：
- **代码质量工具**：black, ruff, pylint
- **测试工具**：pytest, pytest-cov
- **环境管理**：python-dotenv
- **类型提示**：types-requests

### 依赖管理操作

#### 更新依赖
```bash
# 更新所有依赖到最新版本
pip install --upgrade -e .

# 更新特定包
pip install --upgrade requests
```

#### 生成依赖列表（可选）
```bash
# 生成requirements.txt用于部署
pip freeze > requirements.txt
```

## 验证环境设置

### 步骤5：环境验证测试
运行以下命令验证环境设置是否成功：

```bash
# 验证Python版本
python --version

# 验证依赖包安装
pip list | grep nocodb-py

# 验证SDK模块导入
python -c "import nocodb_py; print('✅ NocoDB SDK导入成功')"

# 运行基础测试
python -m pytest tests/ -v
```

预期结果：
- ✅ Python版本显示正确（3.9+）
- ✅ nocodb-py包出现在已安装包列表中
- ✅ SDK模块导入成功
- ✅ 基础测试通过

## 开发工作流

### 日常开发流程

#### 开始开发会话
每次开始开发时，首先激活虚拟环境：

```bash
# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# 或
.venv\Scripts\activate.bat  # Windows CMD

# 验证环境状态
python -c "import nocodb_py"
```

#### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_api.py

# 带覆盖率的测试
pytest --cov=nocodb_py tests/
```

### VSCode集成
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

## 核心依赖包
成功安装后，虚拟环境中将包含以下核心包：

### 必需依赖
- `nocodb-py` - 本项目（可编辑模式安装）
- `requests` - HTTP客户端库
- `certifi` - SSL证书验证
- `charset-normalizer` - 字符编码检测
- `idna` - 国际化域名处理
- `urllib3` - HTTP连接池管理

### 开发依赖（可选）
- `pytest` - 测试框架
- `pytest-cov` - 测试覆盖率
- `black` - 代码格式化
- `ruff` - 代码质量检查
- `pylint` - 静态代码分析
- `python-dotenv` - 环境变量管理
- `types-requests` - 类型提示支持

## 故障排除

### 常见问题及解决方案

#### 1. 虚拟环境创建失败
**问题**：`python -m venv .venv` 命令失败
**解决方案**：
- 检查Python安装：`python --version`
- 确保venv模块可用：`python -c "import venv; print('venv模块可用')"`
- 在Windows上尝试使用管理员权限

#### 2. 激活脚本无法执行（Windows PowerShell）
**问题**：执行策略阻止脚本运行
**解决方案**：
```powershell
# 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 或永久允许（推荐用于开发）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 3. 包导入错误
**问题**：`ImportError: No module named 'nocodb_py'`
**解决方案**：
- 确认虚拟环境已激活
- 重新安装依赖：`pip install -e .`
- 检查Python解释器路径是否正确

#### 4. Python版本不匹配
**问题**：项目需要Python 3.9+但系统版本较低
**解决方案**：
- 升级Python到3.9+版本
- 或使用pyenv等版本管理工具

### 重新创建虚拟环境
如果遇到无法解决的问题，可以重新创建虚拟环境：

#### Linux / macOS
```bash
# 删除现有环境
rm -rf .venv

# 重新创建并安装
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

#### Windows PowerShell
```powershell
# 删除现有环境
Remove-Item -Recurse -Force .venv

# 重新创建并安装
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

#### Windows CMD
```cmd
# 删除现有环境
rmdir /s /q .venv

# 重新创建并安装
python -m venv .venv
.venv\Scripts\activate.bat
pip install -e .[dev]
```

## 版本控制注意事项
虚拟环境目录 `.venv/` 已添加到 `.gitignore` 文件，不应提交到版本控制。每个开发者需要在本地创建自己的虚拟环境。

---

*最后更新：2025-12-25*