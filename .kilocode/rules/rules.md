# 工作区特定LLM规则

## Python虚拟环境激活规则

### 规则说明
在执行Python相关代码时，**必须**先激活虚拟环境。这是为了避免污染系统环境，确保依赖包的正确隔离和使用。

**重要：禁止直接执行python命令，必须使用Activate脚本加上 && 符号组合执行。**

### 激活命令示例

#### Windows PowerShell
```powershell
.\.venv\Scripts\Activate.ps1 && python your_script.py
```

#### Linux / macOS
```bash
source .venv/bin/activate && python your_script.py
```

#### Windows CMD
```cmd
.\.venv\Scripts\activate.bat && python your_script.py
```

### 重要注意事项

1. **点号（dot）的重要性**：
   - 在Windows PowerShell和CMD中，**必须**在路径前加上点号（`.`）
   - 点号表示当前目录，确保脚本从正确的位置执行
   - 示例：`.\.venv\Scripts\Activate.ps1`（正确） vs `\venv\Scripts\Activate.ps1`（错误）

2. **虚拟环境路径确认**：
   - 确保虚拟环境目录（`.venv`）存在于项目根目录
   - 如果使用不同的虚拟环境目录名，请相应调整路径

3. **命令组合**：
   - 使用 `&&` 运算符将激活命令和Python命令组合在一起
   - 这样可以确保Python命令在虚拟环境激活后执行

4. **验证激活状态**：
   - 激活后，命令行提示符通常会显示虚拟环境名称
   - 可以使用 `pip list` 确认使用的是虚拟环境中的包

### 示例使用场景

```powershell
# 运行测试
.\.venv\Scripts\Activate.ps1 && python -m pytest tests/

# 安装开发依赖
.\.venv\Scripts\Activate.ps1 && pip install -e .[dev]

# 执行临时测试代码
.\.venv\Scripts\Activate.ps1 && python tests/draft/test_code.py
```

遵循此规则可以确保Python代码在正确的环境中执行，避免依赖冲突和环境污染问题。