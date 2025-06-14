# 项目结构

```
album-scanner/
├── README.md                 # 项目说明
├── requirements.txt          # Python依赖
├── main.py                  # 程序入口
├── app_manager.py           # 应用程序主管理器
├── src/                     # 源代码目录
│   ├── __init__.py          
│   ├── core/                # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── config.py        # 配置管理
│   │   ├── album_scanner.py # 相册扫描服务
│   │   ├── album_favorites.py # 收藏功能
│   │   ├── album_history.py # 历史记录
│   │   └── album_viewer.py  # 相册查看器
│   ├── ui/                  # 用户界面
│   │   ├── __init__.py
│   │   ├── ui_components.py # UI组件
│   │   └── fallback_ui.py   # 备用UI
│   └── utils/               # 工具模块
│       ├── __init__.py
│       └── image_utils.py   # 图像处理工具
├── docs/                    # 文档目录
│   ├── ARCHITECTURE.md      # 架构说明
│   ├── DEVELOPMENT.md       # 开发指南
│   ├── INSTALLATION.md      # 安装说明
│   ├── SHORTCUTS.md         # 快捷键说明
│   ├── TROUBLESHOOTING.md   # 故障排除
│   └── CHANGELOG.md         # 更新日志
├── .github/                 # GitHub配置
├── .vscode/                 # VS Code配置
└── .venv/                   # 虚拟环境
```

## 模块说明

### 核心模块 (src/core/)
- `config.py`: 应用程序配置管理
- `album_scanner.py`: 相册扫描和索引功能
- `album_favorites.py`: 收藏夹管理
- `album_history.py`: 浏览历史记录
- `album_viewer.py`: 图片查看和展示

### UI模块 (src/ui/)
- `ui_components.py`: 主要UI组件和界面
- `fallback_ui.py`: 备用简单界面

### 工具模块 (src/utils/)
- `image_utils.py`: 图像处理、缩略图生成、幻灯片等工具

### 主要文件
- `main.py`: 程序入口点
- `app_manager.py`: 应用程序主控制器

## 优化说明

1. **模块化设计**: 按功能将代码分类到不同目录
2. **清晰的依赖关系**: 核心逻辑与UI分离
3. **文档集中管理**: 所有文档放在docs目录
4. **简洁的根目录**: 只保留必要的配置和入口文件
