# 📋 安装部署指南

详细的相册扫描器安装、配置和部署说明。

## 📋 目录

- [系统要求](#系统要求)
- [安装方式](#安装方式)
- [依赖管理](#依赖管理)
- [配置说明](#配置说明)
- [部署选项](#部署选项)
- [升级指南](#升级指南)

## 💻 系统要求

### 基本要求
- **Python版本**: 3.7+ (推荐3.9+)
- **内存**: 最低2GB，推荐4GB+
- **存储空间**: 100MB程序空间 + 图片存储空间
- **显示器**: 最低分辨率1024x768，推荐1920x1080+

### 操作系统支持
| 操作系统 | 版本要求 | 状态 | 说明 |
|----------|----------|------|------|
| Windows | 10/11 | ✅ 完全支持 | 推荐系统 |
| macOS | 10.14+ | ✅ 完全支持 | 需要Xcode Command Line Tools |
| Linux | Ubuntu 18.04+, CentOS 7+ | ✅ 完全支持 | 需要额外GUI库 |

### Python版本兼容性
| Python版本 | 支持状态 | 说明 |
|------------|----------|------|
| 3.7 | ✅ 支持 | 最低要求版本 |
| 3.8 | ✅ 支持 | 稳定版本 |
| 3.9 | ✅ 推荐 | 推荐版本，性能最佳 |
| 3.10 | ✅ 支持 | 最新特性支持 |
| 3.11+ | ⚠️ 测试中 | 可能需要依赖更新 |

## 🚀 安装方式

### 方式一：Git克隆安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/ttf248/album-scanner.git
cd album-scanner

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行程序
python main.py
```

### 方式二：直接下载安装

```bash
# 1. 下载源码包
wget https://github.com/ttf248/album-scanner/archive/main.zip
unzip main.zip
cd album-scanner-main

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行程序
python main.py
```

### 方式三：开发环境安装

```bash
# 1. 克隆仓库
git clone https://github.com/ttf248/album-scanner.git
cd album-scanner

# 2. 安装开发依赖
pip install -r requirements-dev.txt

# 3. 安装为可编辑包
pip install -e .

# 4. 运行程序
album-scanner
```

## 📦 依赖管理

### 核心依赖
```txt
Pillow>=8.0.0          # 图片处理库
ttkthemes>=3.2.0       # GUI主题支持
```

### 可选依赖
```txt
# 开发依赖
pytest>=6.0.0         # 测试框架
black>=21.0.0          # 代码格式化
flake8>=3.9.0          # 代码检查
mypy>=0.910            # 类型检查

# 性能优化依赖
numpy>=1.19.0          # 数值计算加速
opencv-python>=4.5.0  # 高级图片处理
```

### 依赖安装选项

#### 最小安装
```bash
pip install Pillow ttkthemes
```

#### 完整安装
```bash
pip install -r requirements.txt
```

#### 开发安装
```bash
pip install -r requirements-dev.txt
```

### 依赖问题排查

#### Pillow安装问题
```bash
# Windows用户可能需要
pip install --upgrade pip
pip install Pillow --upgrade

# macOS用户可能需要
brew install libjpeg libpng libtiff
pip install Pillow

# Linux用户可能需要
sudo apt-get install python3-pil python3-pil.imagetk
# 或
sudo yum install python3-pillow python3-pillow-tk
```

#### ttkthemes问题
```bash
# 如果主题加载失败，尝试重新安装
pip uninstall ttkthemes
pip install ttkthemes --no-cache-dir
```

## ⚙️ 配置说明

### 配置文件位置
```
Windows: C:\Users\<用户名>\.album_scanner\settings.json
macOS: /Users/<用户名>/.album_scanner/settings.json
Linux: /home/<用户名>/.album_scanner/settings.json
```

### 默认配置
```json
{
  "window": {
    "width": 1200,
    "height": 800,
    "x": 100,
    "y": 100,
    "maximized": false
  },
  "ui": {
    "theme": "default",
    "font_family": "SF Pro Display",
    "font_size": 12,
    "grid_columns": "auto",
    "thumbnail_size": 200
  },
  "scanner": {
    "supported_formats": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"],
    "recursive_scan": true,
    "max_depth": 10,
    "cache_thumbnails": true
  },
  "viewer": {
    "default_zoom": "fit",
    "slideshow_interval": 3,
    "smooth_zoom": true,
    "preload_images": true
  },
  "favorites": {
    "max_items": 50,
    "auto_cleanup": true
  },
  "history": {
    "max_items": 20,
    "auto_cleanup": true
  }
}
```

### 高级配置选项

#### 性能优化配置
```json
{
  "performance": {
    "max_memory_usage": "1GB",
    "thumbnail_cache_size": 100,
    "preload_count": 5,
    "async_loading": true,
    "worker_threads": 4
  }
}
```

#### 界面自定义
```json
{
  "ui_custom": {
    "colors": {
      "primary": "#007AFF",
      "secondary": "#5856D6",
      "background": "#F2F2F7",
      "text": "#000000"
    },
    "animations": {
      "enabled": true,
      "duration": 300,
      "easing": "ease-out"
    }
  }
}
```

### 配置文件管理

#### 重置配置
```bash
# 删除配置文件以恢复默认设置
rm ~/.album_scanner/settings.json
```

#### 备份配置
```bash
# 备份当前配置
cp ~/.album_scanner/settings.json ~/.album_scanner/settings.backup.json
```

#### 导入/导出配置
```bash
# 导出配置到当前目录
cp ~/.album_scanner/settings.json ./my_settings.json

# 导入配置
cp ./my_settings.json ~/.album_scanner/settings.json
```

## 🌐 部署选项

### 单用户部署（推荐）
直接在用户目录下运行，配置自动保存到用户目录。

```bash
cd ~/album-scanner
python main.py
```

### 多用户部署
在系统共享目录安装，每个用户有独立配置。

```bash
# 安装到系统目录
sudo cp -r album-scanner /opt/
sudo chmod +x /opt/album-scanner/main.py

# 创建启动脚本
sudo tee /usr/local/bin/album-scanner << 'EOF'
#!/bin/bash
cd /opt/album-scanner
python main.py "$@"
EOF
sudo chmod +x /usr/local/bin/album-scanner
```

### 容器化部署
```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3-tk \
    python3-pil \
    python3-pil.imagetk \
    && rm -rf /var/lib/apt/lists/*

# 复制源码
COPY . /app
WORKDIR /app

# 安装Python依赖
RUN pip install -r requirements.txt

# 设置环境变量
ENV DISPLAY=:0

# 运行程序
CMD ["python", "main.py"]
```

### 便携式部署
创建完全独立的便携式版本。

```bash
# 使用PyInstaller打包
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "*.py:." main.py

# 或使用cx_Freeze
pip install cx_Freeze
python setup.py build
```

## 📊 性能优化

### 内存优化
```python
# 在配置文件中设置
{
  "performance": {
    "max_memory_usage": "512MB",  # 限制内存使用
    "garbage_collect_interval": 100,  # 垃圾回收间隔
    "thumbnail_cache_size": 50  # 缩略图缓存数量
  }
}
```

### 存储优化
```python
# 缓存目录设置
{
  "cache": {
    "enabled": true,
    "directory": "~/.album_scanner/cache",
    "max_size": "100MB",
    "cleanup_interval": "7d"
  }
}
```

### 网络优化
```python
# 如果使用网络存储
{
  "network": {
    "timeout": 30,
    "retry_count": 3,
    "concurrent_downloads": 2
  }
}
```

## 🔄 升级指南

### 版本检查
```bash
# 检查当前版本
python main.py --version

# 检查最新版本
git fetch origin
git log --oneline HEAD..origin/main
```

### 升级步骤

#### Git用户升级
```bash
# 1. 备份配置
cp ~/.album_scanner/settings.json ~/settings.backup.json

# 2. 拉取最新代码
git pull origin main

# 3. 更新依赖
pip install -r requirements.txt --upgrade

# 4. 运行程序
python main.py
```

#### 手动升级
```bash
# 1. 下载新版本
wget https://github.com/ttf248/album-scanner/archive/main.zip

# 2. 备份旧版本
mv album-scanner album-scanner-backup

# 3. 解压新版本
unzip main.zip
mv album-scanner-main album-scanner

# 4. 恢复配置
cp album-scanner-backup/settings.json album-scanner/

# 5. 安装依赖
cd album-scanner
pip install -r requirements.txt

# 6. 运行程序
python main.py
```

### 升级注意事项
1. **备份数据**：升级前务必备份配置文件和收藏数据
2. **依赖冲突**：新版本可能需要更新依赖包
3. **配置兼容性**：检查新版本的配置文件格式变化
4. **测试功能**：升级后测试主要功能是否正常

### 回滚操作
如果升级后出现问题，可以回滚到之前版本：

```bash
# Git用户
git checkout <previous-commit>

# 手动用户
rm -rf album-scanner
mv album-scanner-backup album-scanner
```

## 🛠️ 开发环境设置

### IDE配置推荐

#### VS Code配置
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true
}
```

#### PyCharm配置
1. 设置Python解释器为虚拟环境
2. 配置代码风格为Black
3. 启用类型检查
4. 配置运行调试配置

### 调试配置
```json
{
  "name": "Album Scanner Debug",
  "type": "python",
  "request": "launch",
  "program": "main.py",
  "args": ["--debug"],
  "console": "integratedTerminal",
  "cwd": "${workspaceFolder}"
}
```

## 📞 获取帮助

### 常见问题
请查看 [故障排除文档](TROUBLESHOOTING.md)

### 社区支持
- GitHub Issues: https://github.com/ttf248/album-scanner/issues
- 讨论区: https://github.com/ttf248/album-scanner/discussions

### 商业支持
如需定制开发或技术支持，请联系项目维护者。

---

🔙 [返回主文档](README.md) | ⌨️ [快捷键文档](SHORTCUTS.md) | 🔧 [故障排除](TROUBLESHOOTING.md)
