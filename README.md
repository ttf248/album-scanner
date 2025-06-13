# Album Scanner

一个用于扫描和管理相册的工具。

## 功能特点
- 扫描本地相册文件
- 组织和分类照片
- 提供相册管理功能

## 依赖说明
本项目使用以下第三方库：

- **Pillow (PIL)**：用于图片处理和显示，支持多种图片格式的读取和缩略图生成
- **tkinter**：Python标准GUI库，用于创建用户界面（通常Python已预装）

## 安装说明
1. 克隆仓库
2. 安装依赖：
```
pip install -r requirements.txt
```

## 使用方法
```
python main.py
```

## 配置
应用程序会自动保存您上次选择的相册路径，以便下次启动时快速访问。配置信息存储在以下位置：
- Windows: `C:\Users\<用户名>\.album_scanner_config.json`
- macOS/Linux: `~/.album_scanner_config.json`

该JSON文件包含以下字段：
- `last_path`: 上次选择的相册文件夹路径

无需手动编辑此文件，应用程序会在您浏览并选择新文件夹时自动更新配置。当您下次启动应用时，将自动加载上次使用的路径。

## 许可证
[MIT](LICENSE)