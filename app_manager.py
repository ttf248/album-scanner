import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import os
from pathlib import Path
from src.core.config import ConfigManager
from src.utils.image_utils import ImageProcessor
from src.ui.components.style_manager import StyleManager
from src.ui.components.navigation_bar import NavigationBar
from src.ui.components.album_grid import AlbumGrid
from src.ui.components.image_viewer import ImageViewer
from src.ui.components.status_bar import StatusBar

class PhotoAlbumApp:
    """现代化漫画扫描器主应用程序"""
    
    def __init__(self, root):
        self.root = root
        
        # 首先初始化管理器
        self.config_manager = ConfigManager()
        
        # 然后设置窗口
        self.setup_window()
        
        # 初始化现代化样式管理器
        from tkinter import ttk
        style = ttk.Style()
        self.style_manager = StyleManager(self.root, style)
        
        # 配置TTK样式
        self.style_manager.configure_ttk_styles()
        
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
        self.root.title("漫画扫描器 - 现代化图片管理")
        
        # 窗口大小和位置 - 增大默认尺寸以适应新布局
        window_size = self.config_manager.config.get('window_size', '1400x900')
        self.root.geometry(window_size)
        self.root.minsize(1100, 700)  # 增大最小尺寸
        
        # 设置现代化主题
        try:
            # 尝试设置现代化主题
            available_themes = ['arc', 'equilux', 'adapta', 'yaru']
            theme_set = False
            
            for theme in available_themes:
                try:
                    self.root.set_theme(theme)
                    print(f"已应用 {theme} 主题")
                    theme_set = True
                    break
                except Exception as e:
                    print(f"设置 {theme} 主题失败: {e}")
                    continue
            
            if not theme_set:
                print("使用默认主题")
                try:
                    self.root.set_theme('default')
                except:
                    pass
                    
        except Exception as e:
            print(f"主题设置过程出错: {e}")
        
    def create_widgets(self):
        """创建现代化UI组件"""
        try:
            # 创建路径变量
            self.path_var = tk.StringVar()
            self.path_var.set(self.config_manager.get_last_path())
            
            # 创建现代化导航栏
            self.nav_bar = NavigationBar(
                self.root,
                browse_callback=self.browse_folder,
                scan_callback=self.scan_albums,
                path_var=self.path_var,
                recent_callback=self.show_recent_albums,
                favorites_callback=self.show_favorites,
                style_manager=self.style_manager
            )
            # NavigationBar已经在create_widgets中自动pack了
            
            # 创建现代化漫画网格
            self.album_grid = AlbumGrid(
                self.root,
                open_callback=self.open_album,
                favorite_callback=self.toggle_favorite,
                style_manager=self.style_manager
            )
            # 设置is_favorite回调
            self.album_grid.is_favorite = self.config_manager.is_favorite
            # AlbumGrid已经在create_widgets中自动pack了
            
            # 创建现代化状态栏
            self.status_bar = StatusBar(
                self.root,
                style_manager=self.style_manager
            )
            # StatusBar已经在create_widgets中自动pack了
            
            # 设置组件间的引用
            self.album_grid.nav_bar = self.nav_bar
            
            # 更新路径显示
            if self.folder_path:
                self.path_var.set(self.folder_path)
            
            # 初始状态 - 根据是否有上次路径显示不同消息
            if self.folder_path and os.path.exists(self.folder_path):
                folder_name = os.path.basename(self.folder_path)
                # 处理长路径名称
                if len(folder_name) > 30:
                    display_name = folder_name[:27] + "..."
                else:
                    display_name = folder_name
                self.status_bar.set_status(f"上次路径: {display_name}", "info")
            else:
                self.status_bar.set_status("欢迎使用漫画扫描器", "success")
            
            print("现代化UI组件创建成功")
            
        except Exception as e:
            print(f"创建UI组件时发生错误: {e}")
            import traceback
            traceback.print_exc()
            # 创建简化版本的UI
            try:
                from src.ui.fallback_ui import FallbackUIManager
                fallback_manager = FallbackUIManager(self)
                fallback_manager.create_fallback_ui()
            except Exception as fallback_error:
                print(f"创建回退UI也失败: {fallback_error}")

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
            title="选择漫画文件夹",
            initialdir=self.folder_path if self.folder_path else str(Path.home())
        )
        if folder_selected:
            # 确保路径正确处理Unicode字符
            folder_selected = str(Path(folder_selected))
            self.folder_path = folder_selected
            self.path_var.set(folder_selected)
            self.config_manager.set_last_path(folder_selected)
            
            # 路径已通过self.path_var.set()更新，NavigationBar会自动显示
            
            # 显示文件夹名称，处理长路径
            folder_name = Path(folder_selected).name
            if len(folder_name) > 30:
                display_name = folder_name[:27] + "..."
            else:
                display_name = folder_name
            self.status_bar.set_status(f"已选择: {display_name}", "success")
            
    def scan_albums(self):
        """扫描漫画"""
        from src.core.album_scanner import AlbumScannerService
        scanner = AlbumScannerService(self)
        scanner.scan_albums()
    
    def show_recent_albums(self):
        """显示最近浏览的漫画"""
        from src.core.album_history import AlbumHistoryManager
        history_manager = AlbumHistoryManager(self)
        history_manager.show_recent_albums()
    
    def show_favorites(self):
        """显示收藏的漫画"""
        from src.core.album_favorites import AlbumFavoritesManager
        favorites_manager = AlbumFavoritesManager(self)
        favorites_manager.show_favorites()
    
    def toggle_favorite(self, album_path):
        """切换收藏状态"""
        if self.config_manager.is_favorite(album_path):
            self.config_manager.remove_favorite(album_path)
            self.status_bar.set_status(f"已从收藏中移除: {os.path.basename(album_path)}", "warning")
        else:
            self.config_manager.add_favorite(album_path)
            self.status_bar.set_status(f"已添加到收藏: {os.path.basename(album_path)}", "success")
        
        # 刷新当前显示
        if self.albums:
            self.album_grid.update_albums(self.albums)
            
    def open_album(self, folder_path):
        """打开漫画查看"""
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
