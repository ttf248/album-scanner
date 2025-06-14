# 此文件已废弃 - 所有UI组件已模块化
# 请使用: from ui.components import AlbumGrid, ImageViewer, StatusBar, StyleManager
import os
from ...utils.image_utils import ImageProcessor, SlideshowManager
from PIL import Image, ImageTk
import threading
from concurrent.futures import ThreadPoolExecutor
from .components.style_manager import StyleManager, get_safe_font
from .components.status_bar import StatusBar
from .components.album_grid import AlbumGrid
from .components.image_viewer import ImageViewer

# AlbumGrid类已移动到 components/album_grid.py
# ImageViewer类已移动到 components/image_viewer.py
