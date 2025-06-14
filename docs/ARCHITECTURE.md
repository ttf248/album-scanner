# 🏗️ 架构设计文档

漫画扫描器的技术架构、设计原则和模块化实现详解。

## 📋 目录

- [项目架构概览](#项目架构概览)
- [模块化设计](#模块化设计)
- [技术栈详解](#技术栈详解)
- [设计模式](#设计模式)
- [性能优化](#性能优化)
- [扩展性设计](#扩展性设计)

## 🏛️ 项目架构概览

### 整体架构图
```
┌─────────────────────────────────────────────────────────┐
│                   漫画扫描器 v2.0                         │
├─────────────────────────────────────────────────────────┤
│  🎨 表现层 (Presentation Layer)                         │
│  ├── ui/__init__.py         # 统一UI导出接口            │
│  ├── components/*.py        # 模块化UI组件              │
│  ├── fallback_ui.py        # 备用界面                   │
│  └── 主题系统               # iPhone风格设计             │
├─────────────────────────────────────────────────────────┤
│  🎮 控制层 (Control Layer)                              │
│  ├── app_manager.py        # 应用管理器                 │
│  ├── album_viewer.py       # 漫画查看器                 │
│  └── main.py               # 应用入口                   │
├─────────────────────────────────────────────────────────┤
│  💼 业务层 (Business Layer)                             │
│  ├── album_scanner.py      # 漫画扫描服务               │
│  ├── album_favorites.py    # 收藏管理器                 │
│  ├── album_history.py      # 历史记录管理               │
│  └── image_utils.py        # 图片处理工具               │
├─────────────────────────────────────────────────────────┤
│  💾 数据层 (Data Layer)                                 │
│  ├── config.py             # 配置管理器                 │
│  └── ~/.album_scanner/     # 用户数据目录               │
└─────────────────────────────────────────────────────────┘
```

### 文件结构详解
```
album-scanner/
├── 📱 应用入口
│   └── main.py               # 简化的启动器，职责单一
├── 🎮 核心控制层
│   ├── app_manager.py        # 主应用逻辑和生命周期管理
│   └── album_viewer.py       # 图片查看器管理器
├── 💼 业务服务层
│   ├── album_scanner.py      # 漫画扫描核心服务
│   ├── album_history.py      # 历史记录业务逻辑
│   ├── album_favorites.py    # 收藏功能业务逻辑
│   └── image_utils.py        # 图片处理和工具函数
├── 🎨 用户界面层
│   ├── __init__.py          # 统一UI模块导出接口
│   ├── components/          # 模块化UI组件集合
│   │   ├── style_manager.py # 样式和主题管理
│   │   ├── navigation_bar.py# 导航栏组件
│   │   ├── album_grid.py    # 漫画网格显示
│   │   ├── image_viewer.py  # 图片查看器
│   │   └── status_bar.py    # 状态栏组件
│   └── fallback_ui.py       # 备用UI和错误恢复界面
├── 💾 数据配置层
│   └── config.py             # 配置管理和数据持久化
├── 📚 项目文档
│   ├── README.md            # 项目介绍和快速开始
│   ├── INSTALLATION.md      # 安装部署指南
│   ├── SHORTCUTS.md         # 快捷键文档
│   ├── TROUBLESHOOTING.md   # 故障排除指南
│   ├── ARCHITECTURE.md      # 架构设计文档（本文档）
│   ├── DEVELOPMENT.md       # 开发指南
│   └── CHANGELOG.md         # 更新日志
└── 🗂️ 用户数据
    └── ~/.album_scanner/    # 用户配置和数据目录
        ├── settings.json    # 用户设置文件
        ├── favorites.json   # 收藏数据
        ├── history.json     # 历史记录
        └── cache/           # 缓存目录
```

## 🧩 模块化设计

### 设计原则

#### 🎯 单一职责原则 (SRP)
- **main.py**: 仅负责应用启动
- **app_manager.py**: 专注应用生命周期管理
- **album_scanner.py**: 专注漫画扫描逻辑
- **ui/__init__.py**: 统一UI组件导出和接口管理

#### 🔗 低耦合高内聚
```python
# 模块间通过接口通信，降低耦合
class AlbumScanner:
    def scan_directory(self, path: str) -> List[Album]:
        """扫描接口，与UI层解耦"""
        pass

class AppManager:
    def __init__(self):
        self.scanner = AlbumScanner()  # 依赖注入
```

#### 🛡️ 依赖倒置原则
```python
# 高层模块不依赖低层模块，都依赖抽象
from abc import ABC, abstractmethod

class ImageProcessor(ABC):
    @abstractmethod
    def process_image(self, path: str) -> Image:
        pass

class AppManager:
    def __init__(self, processor: ImageProcessor):
        self.processor = processor  # 依赖抽象而非具体实现
```

### 模块职责划分

#### 📱 main.py - 应用入口
```python
职责:
✅ 程序启动和初始化
✅ 命令行参数处理
✅ 异常捕获和错误报告
❌ 不包含业务逻辑
❌ 不包含UI代码
```

#### 🎮 app_manager.py - 应用管理器
```python
职责:
✅ 应用生命周期管理
✅ 模块间协调
✅ 状态管理
✅ 事件分发
✅ 资源管理
```

#### 💼 业务服务层
```python
album_scanner.py:
✅ 文件系统扫描
✅ 图片识别和分类
✅ 漫画数据结构管理

album_favorites.py:
✅ 收藏状态管理
✅ 收藏数据持久化
✅ 收藏列表操作

album_history.py:
✅ 历史记录管理
✅ 访问记录跟踪
✅ 历史数据清理
```

#### 🎨 UI模块层
```python
ui/__init__.py:
✅ 统一UI组件导出
✅ 模块接口管理
✅ 版本信息维护
✅ 公共导入路径

components/*.py:
✅ 独立UI组件实现
✅ 组件间低耦合
✅ 可复用设计
```

## 🛠️ 技术栈详解

### 核心技术栈

#### 🐍 Python 3.7+
- **选择原因**: 跨平台、丰富的图片处理库、快速开发
- **最低版本**: 3.7（f-string支持、dataclass支持）
- **推荐版本**: 3.9+（性能优化、类型提示增强）

#### 🎨 Tkinter + ttkthemes
```python
优势:
✅ Python标准库，无额外依赖
✅ 跨平台兼容性好
✅ ttkthemes提供现代化主题
✅ 轻量级，启动快速

技术实现:
- 使用ttk组件提供现代化外观
- 自定义主题实现iPhone风格
- 响应式布局适配不同屏幕
```

#### 📸 Pillow (PIL Fork)
```python
功能特点:
✅ 支持所有主流图片格式
✅ 高效的图片处理和缩放
✅ EXIF信息提取
✅ 颜色空间转换

性能优化:
- 懒加载减少内存占用
- 多线程图片处理
- 智能缓存机制
```

### 辅助工具

#### 📁 文件系统处理
```python
import os
import pathlib
from typing import Generator

def scan_images(path: pathlib.Path) -> Generator[pathlib.Path, None, None]:
    """高效的递归文件扫描"""
    for item in path.rglob("*"):
        if item.is_file() and item.suffix.lower() in SUPPORTED_FORMATS:
            yield item
```

#### 🧵 并发处理
```python
import threading
import concurrent.futures
from queue import Queue

class AsyncImageLoader:
    """异步图片加载器"""
    def __init__(self, max_workers: int = 4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers)
        self.cache = {}
```

## 🎨 设计模式

### 单例模式 - 配置管理
```python
class ConfigManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.load_config()
            self._initialized = True
```

### 观察者模式 - 事件系统
```python
class EventSystem:
    def __init__(self):
        self.observers = {}
    
    def subscribe(self, event_type: str, callback: callable):
        if event_type not in self.observers:
            self.observers[event_type] = []
        self.observers[event_type].append(callback)
    
    def emit(self, event_type: str, data=None):
        for callback in self.observers.get(event_type, []):
            callback(data)
```

### 工厂模式 - UI组件创建
```python
class UIComponentFactory:
    @staticmethod
    def create_album_card(parent, album_data):
        """创建漫画卡片组件"""
        return AlbumCard(parent, album_data)
    
    @staticmethod
    def create_image_viewer(parent):
        """创建图片查看器组件"""
        return ImageViewer(parent)
```

### 策略模式 - 图片加载策略
```python
class ImageLoadStrategy(ABC):
    @abstractmethod
    def load_image(self, path: str) -> Image:
        pass

class HighQualityLoader(ImageLoadStrategy):
    def load_image(self, path: str) -> Image:
        return Image.open(path)

class ThumbnailLoader(ImageLoadStrategy):
    def load_image(self, path: str) -> Image:
        img = Image.open(path)
        img.thumbnail((200, 200))
        return img
```

## ⚡ 性能优化

### 内存管理

#### 智能缓存系统
```python
from functools import lru_cache
from weakref import WeakValueDictionary

class SmartCache:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = WeakValueDictionary()  # 弱引用缓存
        self.access_order = []
    
    @lru_cache(maxsize=128)
    def get_thumbnail(self, path: str) -> Image:
        """LRU缓存缩略图"""
        return self._load_thumbnail(path)
```

#### 延迟加载
```python
class LazyImageLoader:
    def __init__(self, path: str):
        self.path = path
        self._image = None
    
    @property
    def image(self) -> Image:
        if self._image is None:
            self._image = Image.open(self.path)
        return self._image
```

### 异步处理

#### 后台扫描
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncAlbumScanner:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def scan_directory_async(self, path: str):
        """异步扫描目录"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self._scan_directory_sync, 
            path
        )
```

#### 非阻塞UI更新
```python
def update_ui_safely(func):
    """确保UI更新在主线程执行"""
    def wrapper(*args, **kwargs):
        if threading.current_thread() is threading.main_thread():
            return func(*args, **kwargs)
        else:
            # 调度到主线程执行
            root.after_idle(lambda: func(*args, **kwargs))
    return wrapper
```

## 🔧 扩展性设计

### 插件系统架构
```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.hooks = {}
    
    def register_plugin(self, name: str, plugin: Plugin):
        """注册插件"""
        self.plugins[name] = plugin
        plugin.initialize(self)
    
    def execute_hook(self, hook_name: str, *args, **kwargs):
        """执行钩子函数"""
        for plugin in self.plugins.values():
            if hasattr(plugin, hook_name):
                getattr(plugin, hook_name)(*args, **kwargs)
```

### 主题系统扩展
```python
class ThemeManager:
    def __init__(self):
        self.themes = {}
        self.current_theme = None
    
    def register_theme(self, name: str, theme: Theme):
        """注册自定义主题"""
        self.themes[name] = theme
    
    def apply_theme(self, name: str):
        """应用主题"""
        if name in self.themes:
            self.current_theme = self.themes[name]
            self.current_theme.apply()
```

### 格式支持扩展
```python
class FormatHandler(ABC):
    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        pass
    
    @abstractmethod
    def load_image(self, file_path: str) -> Image:
        pass

class FormatRegistry:
    def __init__(self):
        self.handlers = []
    
    def register_handler(self, handler: FormatHandler):
        """注册新的格式处理器"""
        self.handlers.append(handler)
```

## 🔒 安全性考虑

### 文件系统安全
```python
import os
from pathlib import Path

def safe_path_join(base: str, *paths: str) -> str:
    """安全的路径拼接，防止路径遍历攻击"""
    base_path = Path(base).resolve()
    target_path = base_path.joinpath(*paths).resolve()
    
    # 确保目标路径在基础路径内
    if not str(target_path).startswith(str(base_path)):
        raise ValueError("Path traversal detected")
    
    return str(target_path)
```

### 输入验证
```python
def validate_image_file(file_path: str) -> bool:
    """验证图片文件的安全性"""
    try:
        with Image.open(file_path) as img:
            img.verify()  # 验证图片完整性
        return True
    except Exception:
        return False
```

## 📊 监控和日志

### 性能监控
```python
import time
import psutil
from functools import wraps

def performance_monitor(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        print(f"{func.__name__}: {end_time - start_time:.2f}s, "
              f"Memory: {(end_memory - start_memory) / 1024 / 1024:.2f}MB")
        
        return result
    return wrapper
```

### 日志系统
```python
import logging
from pathlib import Path

def setup_logging():
    """设置日志系统"""
    log_dir = Path.home() / ".album_scanner" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )
```

## 🚀 未来架构演进

### 微服务化
```python
# 未来可以将扫描服务独立为微服务
class ScannerService:
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
    
    async def scan_remote(self, path: str) -> List[Album]:
        """远程扫描服务"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{self.host}:{self.port}/scan",
                json={"path": path}
            ) as response:
                return await response.json()
```

### 云存储集成
```python
class CloudStorageAdapter(ABC):
    @abstractmethod
    async def list_images(self, path: str) -> List[str]:
        pass
    
    @abstractmethod
    async def download_image(self, path: str) -> bytes:
        pass

class GoogleDriveAdapter(CloudStorageAdapter):
    """Google Drive适配器"""
    pass

class OneDriveAdapter(CloudStorageAdapter):
    """OneDrive适配器"""
    pass
```

---

🔙 [返回主文档](README.md) | 🚀 [开发指南](DEVELOPMENT.md) | 📋 [更新日志](CHANGELOG.md)
