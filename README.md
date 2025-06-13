# Album Scanner

一个用于扫描和管理相册的工具，采用模块化架构设计。

## 功能特点
- 扫描本地相册文件
- 组织和分类照片
- 提供相册管理功能
- 模块化代码结构，易于维护和扩展

## 新增功能
- 主界面自适应窗口缩放，内容自动调整
- 图片浏览支持多种缩放模式（适应窗口、原始大小、填充），可通过界面按钮或快捷键（f:适应窗口，o:原始大小，l:填充）切换
- 支持键盘快捷键切换图片与缩放模式
- 模块化架构重构，代码结构更清晰

## 项目结构
```
album-scanner/
├── main.py              # 主应用程序入口
├── config.py            # 配置管理模块
├── image_utils.py       # 图片处理工具模块
├── ui_components.py     # UI组件模块
├── requirements.txt     # 依赖文件
└── README.md           # 项目文档
```

### 模块说明

#### main.py
应用程序主入口，包含 `PhotoAlbumApp` 主类，负责协调各个模块的工作。

#### config.py
配置管理模块，包含 `ConfigManager` 类，负责：
- 配置文件的读取和保存
- 用户设置的管理
- 上次使用路径的记录

#### image_utils.py
图片处理工具模块，包含 `ImageProcessor` 类，负责：
- 扫描文件夹中的图片文件
- 创建图片缩略图
- 图片的缩放和处理

#### ui_components.py
UI组件模块，包含多个界面组件类：
- `StyleManager`: 样式管理器
- `NavigationBar`: 导航栏组件
- `AlbumGrid`: 相册网格显示组件
- `ImageViewer`: 图片查看器组件

## 依赖说明
本项目使用以下第三方库：

- **Pillow (PIL)**：用于图片处理和显示，支持多种图片格式的读取和缩略图生成
- **ttkthemes**：提供现代化的主题外观
- **tkinter**：Python标准GUI库，用于创建用户界面（通常Python已预装）

## 安装说明
1. 克隆仓库
2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法
```bash
python main.py
```

## 配置
应用程序会自动保存您上次选择的相册路径，以便下次启动时快速访问。配置信息存储在以下位置：
- Windows: `C:\Users\<用户名>\.album_scanner_config.json`
- macOS/Linux: `~/.album_scanner_config.json`

该JSON文件包含以下字段：
- `last_path`: 上次选择的相册文件夹路径

无需手动编辑此文件，应用程序会在您浏览并选择新文件夹时自动更新配置。当您下次启动应用时，将自动加载上次使用的路径。

## 开发说明

### 扩展新功能
由于采用了模块化设计，您可以轻松扩展新功能：

1. **添加新的图片处理功能**：在 `image_utils.py` 中扩展 `ImageProcessor` 类
2. **添加新的UI组件**：在 `ui_components.py` 中创建新的组件类
3. **添加新的配置选项**：在 `config.py` 中扩展 `ConfigManager` 类
4. **修改应用程序逻辑**：在 `main.py` 中修改主应用程序类

### 代码规范
- 使用类和模块进行代码组织
- 每个模块都有明确的职责
- 添加适当的注释和文档字符串
- 处理异常情况并提供用户友好的错误信息

## 许可证
[MIT](LICENSE)