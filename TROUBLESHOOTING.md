# 🔧 故障排除指南

相册扫描器常见问题的解决方案和故障排除方法。

## 📋 目录

- [常见问题](#常见问题)
- [安装问题](#安装问题)
- [运行问题](#运行问题)
- [性能问题](#性能问题)
- [功能问题](#功能问题)
- [调试方法](#调试方法)

## 🚨 常见问题

### 1. 程序无法启动

#### 症状
- 双击main.py没有反应
- 命令行运行报错
- 窗口闪现后消失

#### 解决方案
```bash
# 1. 检查Python版本
python --version
# 确保版本为3.7+

# 2. 检查依赖包
pip list | grep -E "(Pillow|ttkthemes)"

# 3. 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 4. 使用调试模式启动
python main.py --debug
```

#### 详细排查步骤
1. **Python环境检查**
   ```bash
   which python
   python -c "import sys; print(sys.version)"
   ```

2. **依赖检查**
   ```bash
   python -c "import PIL; print(PIL.__version__)"
   python -c "import tkinter; print('tkinter OK')"
   ```

3. **权限检查**
   ```bash
   ls -la main.py
   chmod +x main.py  # 如果需要
   ```

### 2. 图片加载失败

#### 症状
- 相册扫描结果为空
- 图片显示为空白或错误图标
- 部分图片无法打开

#### 解决方案
```bash
# 1. 检查图片格式支持
python -c "from PIL import Image; print(Image.EXTENSION)"

# 2. 检查文件权限
ls -la /path/to/your/images/

# 3. 检查路径编码
python -c "import os; print(os.listdir('图片路径'))"
```

#### 支持的图片格式
| 格式 | 扩展名 | 状态 | 说明 |
|------|--------|------|------|
| JPEG | .jpg, .jpeg | ✅ | 完全支持 |
| PNG | .png | ✅ | 完全支持，包括透明度 |
| GIF | .gif | ✅ | 支持静态和动态 |
| BMP | .bmp | ✅ | Windows位图 |
| WEBP | .webp | ✅ | 现代Web格式 |
| TIFF | .tiff, .tif | ✅ | 高质量格式 |
| RAW | .raw, .cr2, .nef | ❌ | 需要额外插件 |

### 3. 界面显示异常

#### 症状
- 窗口布局混乱
- 字体显示异常
- 按钮或图标缺失
- 颜色显示不正常

#### 解决方案
```bash
# 1. 重置配置文件
rm ~/.album_scanner/settings.json

# 2. 检查系统字体
python -c "import tkinter.font; print(tkinter.font.families())"

# 3. 重新安装ttkthemes
pip uninstall ttkthemes
pip install ttkthemes --no-cache-dir

# 4. 使用备用界面
python main.py --fallback-ui
```

#### 界面自定义
```json
// 在settings.json中设置
{
  "ui": {
    "theme": "clam",  // 使用系统主题
    "font_family": "Arial",  // 使用系统字体
    "font_size": 10,  // 减小字体大小
    "high_dpi": false  // 禁用高DPI支持
  }
}
```

### 4. 性能问题

#### 症状
- 程序运行缓慢
- 扫描时间过长
- 图片加载慢
- 内存占用过高

#### 解决方案
```bash
# 1. 限制扫描深度
# 在设置中设置max_depth: 3

# 2. 减少缓存大小
# 在设置中设置thumbnail_cache_size: 20

# 3. 关闭预加载
# 在设置中设置preload_images: false

# 4. 监控资源使用
python main.py --monitor-performance
```

#### 性能优化配置
```json
{
  "performance": {
    "max_memory_usage": "512MB",
    "thumbnail_cache_size": 30,
    "preload_count": 2,
    "async_loading": true,
    "worker_threads": 2,
    "gc_interval": 50
  },
  "scanner": {
    "max_depth": 5,
    "batch_size": 50,
    "skip_large_dirs": true,
    "large_dir_threshold": 1000
  }
}
```

## 🔧 安装问题

### Python版本不兼容

#### 问题描述
使用Python 3.6或更低版本时出现语法错误。

#### 解决方案
```bash
# 1. 检查Python版本
python --version

# 2. 升级Python
# Windows: 从python.org下载安装
# macOS: brew install python@3.9
# Linux: sudo apt update && sudo apt install python3.9

# 3. 使用正确的Python版本
python3.9 -m pip install -r requirements.txt
python3.9 main.py
```

### 依赖包安装失败

#### Pillow安装失败
```bash
# Windows
pip install --upgrade pip setuptools wheel
pip install Pillow

# macOS
brew install libjpeg libpng libtiff
pip install Pillow

# Linux (Ubuntu/Debian)
sudo apt-get install python3-dev python3-pil python3-pil.imagetk
pip install Pillow

# Linux (CentOS/RHEL)
sudo yum install python3-devel python3-pillow python3-pillow-tk
pip install Pillow
```

#### ttkthemes安装失败
```bash
# 清除缓存重新安装
pip cache purge
pip install ttkthemes --no-cache-dir --force-reinstall

# 或使用系统包管理器
# Ubuntu: sudo apt install python3-tk
# CentOS: sudo yum install tkinter
```

### 权限问题

#### 文件权限不足
```bash
# 检查文件权限
ls -la main.py

# 添加执行权限
chmod +x main.py

# 检查目录权限
ls -la ~/.album_scanner/
```

#### 写入权限问题
```bash
# 检查配置目录权限
mkdir -p ~/.album_scanner
chmod 755 ~/.album_scanner

# 或使用临时目录
export ALBUM_SCANNER_CONFIG_DIR=/tmp/album_scanner
```

## 🚀 运行问题

### 程序崩溃

#### 获取错误信息
```bash
# 使用调试模式
python main.py --debug

# 查看详细错误
python main.py --verbose 2>&1 | tee debug.log

# 使用Python调试器
python -m pdb main.py
```

#### 常见崩溃原因
1. **内存不足**
   ```json
   {
     "performance": {
       "max_memory_usage": "256MB",
       "thumbnail_cache_size": 10
     }
   }
   ```

2. **路径问题**
   ```bash
   # 检查路径编码
   python -c "import os; print(os.path.exists('your_path'))"
   ```

3. **依赖冲突**
   ```bash
   pip list --outdated
   pip install --upgrade pillow ttkthemes
   ```

### 功能异常

#### 扫描功能问题
```bash
# 手动测试扫描功能
python -c "
from image_utils import ImageProcessor
processor = ImageProcessor()
result = processor.scan_directory('/path/to/test')
print(result)
"
```

#### 图片查看器问题
```bash
# 测试图片查看器
python -c "
from ui_components import ImageViewer
import tkinter as tk
root = tk.Tk()
viewer = ImageViewer(root)
viewer.load_image('/path/to/test.jpg')
root.mainloop()
"
```

#### 收藏功能问题
```bash
# 检查收藏数据
cat ~/.album_scanner/favorites.json

# 重置收藏数据
rm ~/.album_scanner/favorites.json
```

## 🔍 调试方法

### 启用调试模式

#### 命令行参数
```bash
python main.py --debug                # 启用调试输出
python main.py --verbose             # 详细输出
python main.py --log-level=DEBUG     # 设置日志级别
python main.py --profile             # 性能分析
```

#### 环境变量
```bash
export ALBUM_SCANNER_DEBUG=1
export ALBUM_SCANNER_LOG_LEVEL=DEBUG
export ALBUM_SCANNER_PROFILE=1
python main.py
```

### 日志分析

#### 日志文件位置
```
Windows: %APPDATA%\album_scanner\logs\
macOS: ~/Library/Logs/album_scanner/
Linux: ~/.local/share/album_scanner/logs/
```

#### 日志级别
- **DEBUG**: 详细调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

#### 日志分析工具
```bash
# 查看最新日志
tail -f ~/.local/share/album_scanner/logs/app.log

# 过滤错误信息
grep -E "(ERROR|CRITICAL)" ~/.local/share/album_scanner/logs/app.log

# 分析性能问题
grep "performance" ~/.local/share/album_scanner/logs/app.log
```

### 内存分析

#### 内存使用监控
```python
# 添加到main.py开头
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"内存使用: {memory_info.rss / 1024 / 1024:.2f} MB")

# 定期调用
import threading
import time

def memory_monitor():
    while True:
        monitor_memory()
        time.sleep(5)

threading.Thread(target=memory_monitor, daemon=True).start()
```

#### 内存泄漏检测
```bash
# 安装内存分析工具
pip install memory-profiler

# 运行内存分析
python -m memory_profiler main.py
```

### 性能分析

#### 使用cProfile
```bash
python -m cProfile -o profile.stats main.py
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"
```

#### 使用line_profiler
```bash
pip install line_profiler
kernprof -l -v main.py
```

## 🔧 高级故障排除

### 创建最小复现环境

#### 测试脚本
```python
#!/usr/bin/env python3
"""最小测试脚本"""

import sys
import os

def test_basic_imports():
    """测试基本导入"""
    try:
        import tkinter
        print("✅ tkinter导入成功")
    except ImportError as e:
        print(f"❌ tkinter导入失败: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL导入成功")
    except ImportError as e:
        print(f"❌ PIL导入失败: {e}")
        return False
    
    try:
        from ttkthemes import ThemedTk
        print("✅ ttkthemes导入成功")
    except ImportError as e:
        print(f"❌ ttkthemes导入失败: {e}")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    try:
        import tkinter as tk
        from PIL import Image, ImageTk
        
        # 创建测试窗口
        root = tk.Tk()
        root.title("测试窗口")
        
        # 测试图片处理
        # 创建一个简单的测试图片
        test_image = Image.new('RGB', (100, 100), color='red')
        photo = ImageTk.PhotoImage(test_image)
        
        label = tk.Label(root, image=photo)
        label.pack()
        
        # 延迟关闭窗口
        root.after(2000, root.destroy)
        root.mainloop()
        
        print("✅ 基本功能测试通过")
        return True
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

if __name__ == "__main__":
    print("相册扫描器 - 环境测试")
    print("=" * 40)
    
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {os.name}")
    print(f"当前目录: {os.getcwd()}")
    
    if test_basic_imports() and test_basic_functionality():
        print("\n🎉 环境测试全部通过！")
        sys.exit(0)
    else:
        print("\n❌ 环境测试失败，请检查安装")
        sys.exit(1)
```

### 备用启动模式

#### 安全模式
```bash
python main.py --safe-mode
```

#### 最小功能模式
```bash
python main.py --minimal
```

#### 命令行模式
```bash
python main.py --cli
```

### 系统兼容性检查

#### Windows兼容性
```batch
@echo off
echo 检查Windows兼容性...
python --version
python -c "import platform; print(platform.platform())"
python -c "import sys; print('64位' if sys.maxsize > 2**32 else '32位')"
```

#### macOS兼容性
```bash
#!/bin/bash
echo "检查macOS兼容性..."
python3 --version
sw_vers
python3 -c "import platform; print(platform.mac_ver())"
```

#### Linux兼容性
```bash
#!/bin/bash
echo "检查Linux兼容性..."
python3 --version
cat /etc/os-release
python3 -c "import platform; print(platform.linux_distribution())"
```

## 📞 获取帮助

### 报告问题时请提供

1. **系统信息**
   ```bash
   python --version
   pip list
   uname -a  # Linux/macOS
   systeminfo  # Windows
   ```

2. **错误日志**
   ```bash
   python main.py --debug 2>&1 | tee error.log
   ```

3. **配置文件**
   ```bash
   cat ~/.album_scanner/settings.json
   ```

4. **复现步骤**
   - 详细的操作步骤
   - 预期结果
   - 实际结果
   - 错误截图

### 联系方式
- GitHub Issues: https://github.com/ttf248/album-scanner/issues
- 讨论区: https://github.com/ttf248/album-scanner/discussions
- 邮件: [项目维护者邮箱]

### 社区资源
- 常见问题FAQ: [Wiki链接]
- 用户手册: [文档链接]
- 视频教程: [视频链接]

---

🔙 [返回主文档](README.md) | 📋 [安装指南](INSTALLATION.md) | ⌨️ [快捷键文档](SHORTCUTS.md)
