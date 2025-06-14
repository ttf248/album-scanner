import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import os
from pathlib import Path
from src.core.config import ConfigManager
from src.utils.image_utils import ImageProcessor
from src.ui.ui_components import StyleManager, NavigationBar, AlbumGrid, ImageViewer, StatusBar

class PhotoAlbumApp:
    """现代化相册扫描器主应用程序"""
    
    def __init__(self, root):
        self.root = root
        
        # 首先初始化管理器
        self.config_manager = ConfigManager()
        
        # 然后设置窗口
        self.setup_window()
        
        # 设置样式
        from tkinter import ttk
        self.style = ttk.Style()
        self.style_manager = StyleManager(self.root, self.style)
        
        # 初始化变量
        self.folder_path = self.config_manager.get_last_path()
        self.path_var = tk.StringVar(value=self.folder_path)
        self.albums = []
        
        # 创建UI组件
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
        
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("相册扫描器 - 现代化图片管理")
        
        # 窗口大小和位置
        window_size = self.config_manager.config.get('window_size', '1200x800')
        self.root.geometry(window_size)
        self.root.minsize(900, 600)
        
        # 设置主题
        try:
            self.root.set_theme("arc")
        except:
            pass  # 如果主题不可用，使用默认主题
        
    def create_widgets(self):
        """创建现代化UI组件"""
        try:
            # 导航栏
            self.nav_bar = NavigationBar(
                self.root, 
                self.browse_folder, 
                self.scan_albums, 
                self.path_var,
                self.show_recent_albums,
                self.show_favorites
            )
            
            # 相册网格
            self.album_grid = AlbumGrid(self.root, self.open_album, self.toggle_favorite)
            # 设置收藏检查函数
            self.album_grid.is_favorite = self.config_manager.is_favorite
            # 建立与导航栏的关联
            if hasattr(self, 'nav_bar'):
                self.album_grid.nav_bar = self.nav_bar
            
            # 状态栏
            self.status_bar = StatusBar(self.root)
            
            # 初始状态
            self.status_bar.set_status("欢迎使用相册扫描器")
            
        except Exception as e:
            print(f"创建UI组件时发生错误: {e}")
            import traceback
            traceback.print_exc()
            # 创建简化版本的UI
            from src.ui.fallback_ui import FallbackUIManager
            fallback_manager = FallbackUIManager(self)
            fallback_manager.create_fallback_ui()

    def bind_events(self):
        """绑定事件"""
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 键盘快捷键
        self.root.bind('<Control-o>', lambda e: self.browse_folder())
        self.root.bind('<Control-s>', lambda e: self.scan_albums())
        self.root.bind('<Control-r>', lambda e: self.show_recent_albums())
        self.root.bind('<Control-f>', lambda e: self.show_favorites())
        self.root.bind('<F5>', lambda e: self.scan_albums())
        
    def browse_folder(self):
        """浏览并选择文件夹"""
        folder_selected = filedialog.askdirectory(
            title="选择相册文件夹",
            initialdir=self.folder_path if self.folder_path else str(Path.home())
        )
        if folder_selected:
            # 确保路径正确处理Unicode字符
            folder_selected = str(Path(folder_selected))
            self.folder_path = folder_selected
            self.path_var.set(folder_selected)
            self.config_manager.set_last_path(folder_selected)
            
            # 显示文件夹名称，处理长路径
            folder_name = Path(folder_selected).name
            if len(folder_name) > 30:
                display_name = folder_name[:27] + "..."
            else:
                display_name = folder_name
            self.status_bar.set_status(f"已选择: {display_name}")
            
    def scan_albums(self):
        """扫描相册"""
        from src.core.album_scanner import AlbumScannerService
        scanner = AlbumScannerService(self)
        scanner.scan_albums()
    
    def show_recent_albums(self):
        """显示最近浏览的相册"""
        from src.core.album_history import AlbumHistoryManager
        history_manager = AlbumHistoryManager(self)
        history_manager.show_recent_albums()
    
    def show_favorites(self):
        """显示收藏的相册"""
        from src.core.album_favorites import AlbumFavoritesManager
        favorites_manager = AlbumFavoritesManager(self)
        favorites_manager.show_favorites()
    
    def toggle_favorite(self, album_path):
        """切换收藏状态"""
        if self.config_manager.is_favorite(album_path):
            self.config_manager.remove_favorite(album_path)
            self.status_bar.set_status(f"已从收藏中移除: {os.path.basename(album_path)}")
        else:
            self.config_manager.add_favorite(album_path)
            self.status_bar.set_status(f"已添加到收藏: {os.path.basename(album_path)}")
        
        # 刷新当前显示
        if self.albums:
            self.album_grid.display_albums(self.albums)
            
    def open_album(self, folder_path):
        """打开相册查看"""
        from src.core.album_viewer import AlbumViewerManager
        viewer_manager = AlbumViewerManager(self)
        viewer_manager.open_album(folder_path)

    def on_closing(self):
        """窗口关闭时保存配置"""
        try:
            # 保存窗口大小
            self.config_manager.config['window_size'] = self.root.geometry()
            self.config_manager.save_config()
        except Exception as e:
            print(f"保存配置时发生错误: {e}")
        finally:
            self.root.destroy()
