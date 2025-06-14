# 🚀 开发指南

相册扫描器的开发环境设置、贡献指南和项目路线图。

## 📋 目录

- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [测试指南](#测试指南)
- [贡献流程](#贡献流程)
- [发布流程](#发布流程)
- [项目路线图](#项目路线图)

## 💻 开发环境设置

### 基础环境

#### Python环境
```bash
# 推荐使用Python 3.9+
python --version  # 确保版本 >= 3.7

# 推荐使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

#### 克隆和安装
```bash
# 1. Fork并克隆项目
git clone https://github.com/YOUR_USERNAME/album-scanner.git
cd album-scanner

# 2. 安装开发依赖
pip install -r requirements-dev.txt

# 3. 安装项目为可编辑模式
pip install -e .

# 4. 设置pre-commit钩子
pre-commit install
```

### IDE配置

#### VS Code推荐配置
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

#### VS Code推荐扩展
```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",
    "ms-python.isort",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

#### PyCharm配置
1. **Python解释器**: 设置为项目虚拟环境
2. **代码风格**: 导入并应用Black配置
3. **类型检查**: 启用MyPy检查
4. **测试框架**: 配置pytest为默认测试运行器

### 开发工具链

#### 代码质量工具
```bash
# 代码格式化
black .

# 导入排序
isort .

# 代码检查
flake8 .

# 类型检查
mypy .

# 安全检查
bandit -r .
```

#### 测试工具
```bash
# 运行所有测试
pytest

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 运行特定测试
pytest tests/test_album_scanner.py -v
```

## 📝 代码规范

### Python代码风格

#### 基本原则
- 遵循 **PEP 8** 编码规范
- 使用 **Black** 进行代码格式化
- 使用 **isort** 管理导入语句
- 使用 **Type Hints** 提供类型注解

#### 命名规范
```python
# 文件名：使用下划线分隔
album_scanner.py
# 已移除：ui_components.py (已模块化)

# 类名：使用帕斯卡命名法
class AlbumScanner:
class ImageViewer:

# 函数和变量：使用蛇形命名法
def scan_directory():
def load_image():
album_count = 0

# 常量：使用大写字母
MAX_CACHE_SIZE = 100
SUPPORTED_FORMATS = ['.jpg', '.png']

# 私有成员：使用单下划线前缀
def _private_method(self):
self._private_attribute = value
```

#### 文档字符串
```python
def scan_directory(path: str, recursive: bool = True) -> List[Album]:
    """扫描指定目录中的相册。
    
    Args:
        path: 要扫描的目录路径
        recursive: 是否递归扫描子目录，默认为True
        
    Returns:
        相册对象列表，按名称排序
        
    Raises:
        FileNotFoundError: 当指定路径不存在时
        PermissionError: 当没有访问权限时
        
    Examples:
        >>> scanner = AlbumScanner()
        >>> albums = scanner.scan_directory("/path/to/photos")
        >>> print(f"找到 {len(albums)} 个相册")
    """
```

#### 类型注解
```python
from typing import List, Dict, Optional, Union, Callable
from pathlib import Path

class AlbumScanner:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config: Dict[str, Any] = config or {}
        self.albums: List[Album] = []
        self._cache: Dict[str, List[Path]] = {}
    
    def scan_directory(self, path: Union[str, Path]) -> List[Album]:
        """扫描目录并返回相册列表"""
        path = Path(path) if isinstance(path, str) else path
        return self._process_directory(path)
```

### Git提交规范

#### 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 提交类型
- **feat**: 新功能
- **fix**: 错误修复
- **docs**: 文档更新
- **style**: 代码格式调整
- **refactor**: 代码重构
- **test**: 测试相关
- **chore**: 构建或辅助工具变动

#### 示例提交
```bash
feat(scanner): 添加RAW格式图片支持

- 添加CR2, NEF, ARW格式支持
- 实现RAW文件缩略图生成
- 更新支持格式列表文档

Closes #42
```

## 🧪 测试指南

### 测试结构
```
tests/
├── __init__.py
├── conftest.py              # pytest配置和fixtures
├── test_album_scanner.py    # 扫描器测试
├── test_image_utils.py      # 图片工具测试
├── test_ui_components.py    # UI组件测试（已模块化）
├── test_config.py           # 配置管理测试
├── fixtures/                # 测试数据
│   ├── images/              # 测试图片
│   └── configs/             # 测试配置
└── integration/             # 集成测试
    └── test_full_workflow.py
```

### 单元测试示例
```python
# tests/test_album_scanner.py
import pytest
from pathlib import Path
from album_scanner import AlbumScanner

class TestAlbumScanner:
    @pytest.fixture
    def scanner(self):
        """创建扫描器实例"""
        return AlbumScanner()
    
    @pytest.fixture
    def sample_images_dir(self, tmp_path):
        """创建示例图片目录"""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        
        # 创建测试图片文件
        (images_dir / "photo1.jpg").touch()
        (images_dir / "photo2.png").touch()
        
        return images_dir
    
    def test_scan_empty_directory(self, scanner, tmp_path):
        """测试扫描空目录"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        albums = scanner.scan_directory(str(empty_dir))
        
        assert albums == []
    
    def test_scan_directory_with_images(self, scanner, sample_images_dir):
        """测试扫描包含图片的目录"""
        albums = scanner.scan_directory(str(sample_images_dir))
        
        assert len(albums) == 1
        assert albums[0].name == "images"
        assert albums[0].image_count == 2
    
    @pytest.mark.parametrize("format", [".jpg", ".png", ".gif"])
    def test_supported_formats(self, scanner, tmp_path, format):
        """测试支持的图片格式"""
        test_dir = tmp_path / "test"
        test_dir.mkdir()
        (test_dir / f"image{format}").touch()
        
        albums = scanner.scan_directory(str(test_dir))
        
        assert len(albums) == 1
        assert albums[0].image_count == 1
```

### UI测试
```python
# tests/test_ui_components.py
import tkinter as tk
import pytest
from ui import AlbumGrid, ImageViewer  # 从统一入口导入

class TestUIComponents:
    @pytest.fixture
    def root(self):
        """创建测试根窗口"""
        root = tk.Tk()
        yield root
        root.destroy()
    
    def test_album_grid_creation(self, root):
        """测试相册网格创建"""
        album_data = [
            {'name': 'Test Album', 'path': '/test/path', 'image_count': 10}
        ]
        
        grid = AlbumGrid(root, album_data)
        
        assert grid.album_count == 1
    
    def test_image_viewer_zoom(self, root):
        """测试图片查看器缩放功能"""
        viewer = ImageViewer(root)
        
        initial_zoom = viewer.zoom_level
        viewer.zoom_in()
        
        assert viewer.zoom_level > initial_zoom
```

### 性能测试
```python
# tests/test_performance.py
import time
import pytest
from album_scanner import AlbumScanner

class TestPerformance:
    def test_scan_performance(self, large_image_directory):
        """测试大型目录扫描性能"""
        scanner = AlbumScanner()
        
        start_time = time.time()
        albums = scanner.scan_directory(large_image_directory)
        end_time = time.time()
        
        scan_time = end_time - start_time
        
        # 假设1000张图片应该在10秒内完成扫描
        assert scan_time < 10.0
        assert len(albums) > 0
    
    def test_memory_usage(self, scanner):
        """测试内存使用情况"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 执行大量操作
        for _ in range(100):
            scanner.scan_directory("/test/path")
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存增长不应超过100MB
        assert memory_increase < 100 * 1024 * 1024
```

### 测试运行
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_album_scanner.py

# 运行带标记的测试
pytest -m "not slow"

# 生成覆盖率报告
pytest --cov=. --cov-report=html --cov-report=term

# 运行性能测试
pytest tests/test_performance.py -v
```

## 🤝 贡献流程

### 1. 准备工作
```bash
# Fork项目到你的GitHub账户
# 克隆你的fork
git clone https://github.com/YOUR_USERNAME/album-scanner.git
cd album-scanner

# 添加上游仓库
git remote add upstream https://github.com/ttf248/album-scanner.git

# 创建开发分支
git checkout -b feature/your-feature-name
```

### 2. 开发过程
```bash
# 开发你的功能
# 确保遵循代码规范
black .
isort .
flake8 .

# 运行测试
pytest

# 添加测试用例（如果需要）
# 更新文档（如果需要）
```

### 3. 提交代码
```bash
# 添加修改的文件
git add .

# 提交代码（遵循提交规范）
git commit -m "feat: 添加新功能描述"

# 推送到你的fork
git push origin feature/your-feature-name
```

### 4. 创建Pull Request
1. 在GitHub上创建Pull Request
2. 填写PR模板中的所有必要信息
3. 确保所有CI检查通过
4. 响应代码审查意见

### Pull Request模板
```markdown
## 📝 变更说明
简要描述此PR的目的和内容

## 🔄 变更类型
- [ ] 新功能 (feat)
- [ ] 错误修复 (fix)
- [ ] 文档更新 (docs)
- [ ] 代码重构 (refactor)
- [ ] 性能优化 (perf)
- [ ] 测试相关 (test)

## 🧪 测试
- [ ] 添加了新的测试用例
- [ ] 现有测试全部通过
- [ ] 手动测试已完成

## 📋 检查清单
- [ ] 代码遵循项目规范
- [ ] 已添加/更新相关文档
- [ ] 已添加/更新测试用例
- [ ] 提交信息符合规范

## 📸 截图（如果适用）
添加截图来展示UI变化

## 🔗 相关Issue
Fixes #issue_number
```

## 📦 发布流程

### 版本号规范
采用语义化版本控制 (SemVer)：
- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能新增
- **修订版本号**: 向下兼容的问题修正

### 发布步骤
```bash
# 1. 更新版本号
# 在 __init__.py 或 version.py 中更新版本

# 2. 更新CHANGELOG.md
# 记录新版本的变更内容

# 3. 创建发布分支
git checkout -b release/v2.1.0

# 4. 最终测试
pytest
python main.py  # 手动测试

# 5. 合并到main分支
git checkout main
git merge release/v2.1.0

# 6. 创建标签
git tag -a v2.1.0 -m "发布版本 v2.1.0"
git push origin v2.1.0

# 7. 创建GitHub Release
# 在GitHub上创建Release，包含变更日志和下载链接
```

## 🗺️ 项目路线图

### 版本 2.1.0 (进行中)
#### 🎯 核心功能增强
- [ ] **图片编辑功能**
  - [ ] 基础裁剪工具
  - [ ] 旋转和翻转
  - [ ] 亮度/对比度调整
  - [ ] 滤镜效果（黑白、怀旧等）

- [ ] **批量操作**
  - [ ] 批量重命名
  - [ ] 批量移动/复制
  - [ ] 批量格式转换
  - [ ] 批量旋转

#### 🔍 搜索和筛选
- [ ] **智能搜索**
  - [ ] 按文件名搜索
  - [ ] 按拍摄日期筛选
  - [ ] 按文件大小筛选
  - [ ] 按相册名称搜索

- [ ] **高级筛选**
  - [ ] 按图片尺寸筛选
  - [ ] 按颜色主题筛选
  - [ ] 按EXIF信息筛选

### 版本 2.2.0 (计划中)
#### ☁️ 云存储集成
- [ ] **云平台支持**
  - [ ] Google Drive集成
  - [ ] OneDrive集成
  - [ ] iCloud集成
  - [ ] Dropbox集成

- [ ] **同步功能**
  - [ ] 自动同步收藏
  - [ ] 跨设备配置同步
  - [ ] 离线访问支持

#### 🎨 界面增强
- [ ] **主题系统**
  - [ ] 深色模式
  - [ ] 自定义主题
  - [ ] 动态主题切换
  - [ ] 系统主题跟随

- [ ] **响应式设计**
  - [ ] 4K高分辨率适配
  - [ ] 触摸屏支持
  - [ ] 多显示器支持

### 版本 2.3.0 (远期规划)
#### 🤖 AI功能
- [ ] **智能分类**
  - [ ] 人脸识别分组
  - [ ] 场景自动分类
  - [ ] 重复图片检测
  - [ ] 图片质量评估

- [ ] **智能推荐**
  - [ ] 精选图片推荐
  - [ ] 相似图片查找
  - [ ] 智能相册创建

#### 📱 跨平台支持
- [ ] **移动端应用**
  - [ ] iOS应用
  - [ ] Android应用
  - [ ] 跨平台同步

- [ ] **Web版本**
  - [ ] 浏览器版本
  - [ ] 在线图片管理
  - [ ] 分享功能

#### 🔌 插件系统
- [ ] **插件架构**
  - [ ] 插件API设计
  - [ ] 插件管理器
  - [ ] 插件商店

- [ ] **官方插件**
  - [ ] RAW格式支持插件
  - [ ] 水印添加插件
  - [ ] 社交媒体分享插件
  - [ ] 打印功能插件

## 🏗️ 架构演进计划

### 短期目标（6个月内）
1. **性能优化**
   - 优化大型相册加载速度
   - 减少内存占用
   - 提升响应速度

2. **稳定性提升**
   - 增加错误恢复机制
   - 完善异常处理
   - 提升兼容性

### 中期目标（1年内）
1. **模块化重构**
   - 插件系统实现
   - 服务化架构
   - API标准化

2. **云原生支持**
   - 容器化部署
   - 微服务架构
   - 弹性扩展

### 长期目标（2年内）
1. **智能化转型**
   - AI功能集成
   - 机器学习优化
   - 智能推荐算法

2. **生态系统构建**
   - 开发者社区
   - 第三方集成
   - 商业化探索

## 📈 贡献统计

### 当前贡献者
- **核心开发者**: 1名
- **活跃贡献者**: 待招募
- **社区贡献者**: 待发展

### 如何成为贡献者
1. **代码贡献**: 提交高质量的PR
2. **文档贡献**: 改进项目文档
3. **测试贡献**: 提交测试用例和bug报告
4. **设计贡献**: UI/UX设计优化
5. **翻译贡献**: 多语言支持

### 贡献者权益
- **代码署名**: 在项目中署名
- **决策参与**: 参与重要决策讨论
- **优先支持**: 优先获得技术支持
- **学习机会**: 参与技术交流和学习

---

🔙 [返回主文档](README.md) | 🏗️ [架构设计](ARCHITECTURE.md) | 📋 [更新日志](CHANGELOG.md)
---

🔙 [返回主文档](README.md) | 🏗️ [架构设计](ARCHITECTURE.md) | 📋 [更新日志](CHANGELOG.md)
