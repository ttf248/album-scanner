"""
相册扫描器UI模块

提供所有用户界面组件的统一导入接口。
所有UI组件已模块化到独立文件中，通过此文件统一导出。
"""

# 导入所有UI组件
from .components.style_manager import StyleManager, get_safe_font
from .components.status_bar import StatusBar
from .components.album_grid import AlbumGrid
from .components.image_viewer import ImageViewer

# 工具模块导入
from ..utils.image_utils import ImageProcessor, SlideshowManager

# 导出所有公共接口
__all__ = [
    # 核心UI组件
    'AlbumGrid',
    'ImageViewer', 
    'StatusBar',
    'StyleManager',
    
    # 工具函数
    'get_safe_font',
    
    # 图片处理工具
    'ImageProcessor',
    'SlideshowManager'
]

# 版本信息
__version__ = '2.0.0'
__author__ = 'Album Scanner Team'
