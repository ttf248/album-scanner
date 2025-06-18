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
        
        # 状态管理和缓存
        self.current_view_state = "home"  # "home", "recent", "favorites"
        self.cached_scan_results = None  # 缓存扫描结果
        self.cached_scan_path = None     # 缓存扫描路径
        
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
            
            # 设置返回首页回调
            self.nav_bar.home_callback = self.return_to_scan_results
            
            # 设置设置对话框回调
            self.nav_bar.settings_callback = self.show_settings
            
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
            
            # 设置筛选回调
            self.nav_bar.set_filter_callback(self.on_filter_changed)
            
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
        self.root.bind('<Control-comma>', lambda e: self.show_settings())  # Ctrl+, 设置快捷键
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
        
        # 保存当前扫描路径
        current_path = self.path_var.get().strip()
        
        scanner = AlbumScannerService(self)
        scanner.scan_albums()
        
        # 扫描成功后缓存结果
        if self.albums:  # 扫描成功
            self.cached_scan_results = self.albums.copy()
            self.cached_scan_path = current_path
            self.current_view_state = "scan"
            
            # 更新面包屑
            folder_name = os.path.basename(current_path) if current_path else "扫描结果"
            self.nav_bar.update_breadcrumb("scan", folder_name)
            
            # 启动智能预加载
            self._start_intelligent_preload()
    
    def _start_intelligent_preload(self):
        """启动智能预加载"""
        try:
            if not self.albums:
                return
            
            # 延迟启动预加载，确保UI已经稳定
            self.root.after(2000, self._do_intelligent_preload)
            
        except Exception as e:
            print(f"启动智能预加载失败: {e}")
    
    def _do_intelligent_preload(self):
        """执行智能预加载"""
        try:
            from src.utils.image_cache import get_image_cache
            cache = get_image_cache()
            
            # 获取缓存统计
            stats = cache.get_cache_stats()
            print(f"缓存统计: {stats}")
            
            # 预加载策略：
            # 1. 优先预加载前10个相册的封面
            # 2. 如果内存缓存较少，预加载更多
            # 3. 考虑用户的浏览历史
            
            priority_albums = self.albums[:10]  # 前10个优先
            remaining_albums = self.albums[10:20] if len(self.albums) > 10 else []  # 接下来10个
            
            # 优先预加载前10个
            if priority_albums:
                priority_paths = [album.get('path') for album in priority_albums if album.get('path')]
                cache.preload_album_covers(priority_paths, size=(320, 350), widget=self.root)
                print(f"优先预加载 {len(priority_paths)} 个封面")
            
            # 如果内存缓存较少，继续预加载
            if stats.get('memory_items', 0) < 20 and remaining_albums:
                self.root.after(5000, lambda: self._preload_remaining(remaining_albums))
            
            # 清理过期缓存（低优先级任务）
            self.root.after(10000, lambda: cache.cleanup_old_cache(max_age_days=7))
            
        except Exception as e:
            print(f"执行智能预加载失败: {e}")
    
    def _preload_remaining(self, albums):
        """预加载剩余相册"""
        try:
            from src.utils.image_cache import get_image_cache
            cache = get_image_cache()
            
            album_paths = [album.get('path') for album in albums if album.get('path')]
            if album_paths:
                cache.preload_album_covers(album_paths, size=(320, 350), widget=self.root)
                print(f"后台预加载 {len(album_paths)} 个封面")
                
        except Exception as e:
            print(f"预加载剩余相册失败: {e}")

    def show_recent_albums(self):
        """显示最近浏览的漫画"""
        from src.core.album_history import AlbumHistoryManager
        
        self.current_view_state = "recent"
        history_manager = AlbumHistoryManager(self)
        history_manager.show_recent_albums()
        
        # 更新面包屑
        self.nav_bar.update_breadcrumb("recent")
    
    def show_favorites(self):
        """显示收藏的漫画"""
        from src.core.album_favorites import AlbumFavoritesManager
        
        self.current_view_state = "favorites"
        favorites_manager = AlbumFavoritesManager(self)
        favorites_manager.show_favorites()
        
        # 更新面包屑
        self.nav_bar.update_breadcrumb("favorites")
    
    def return_to_scan_results(self):
        """返回扫描结果首页"""
        if self.cached_scan_results and self.cached_scan_path:
            # 恢复缓存的扫描结果
            self.albums = self.cached_scan_results.copy()
            self.current_view_state = "scan"
            
            # 更新显示
            self.album_grid.update_albums(self.albums)
            
            # 更新状态栏
            folder_name = os.path.basename(self.cached_scan_path)
            if len(folder_name) > 30:
                display_name = folder_name[:27] + "..."
            else:
                display_name = folder_name
            
            total_images = sum(len(album.get('image_files', [])) for album in self.albums)
            self.status_bar.set_status(f"扫描结果: {display_name} ({len(self.albums)} 个漫画)", "success")
            self.status_bar.set_info(f"共 {total_images} 张图片")
            
            # 更新面包屑
            self.nav_bar.update_breadcrumb("scan", folder_name)
        else:
            # 没有缓存，提示用户扫描
            self.status_bar.set_status("请先扫描漫画文件夹", "warning")
            self.album_grid.show_empty_state()
            self.nav_bar.update_breadcrumb("home")
    
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
            
            # 如果在收藏视图中，需要重新加载收藏列表
            if self.current_view_state == "favorites":
                self.show_favorites()
    
    def open_album(self, folder_path):
        """打开漫画查看"""
        from src.core.album_viewer import AlbumViewerManager
        viewer_manager = AlbumViewerManager(self)
        
        # 尝试获取当前相册列表和索引
        album_list = None
        current_album_index = None
        
        # 检查是否启用自动切换相册功能
        if self.config_manager.get_auto_switch_album() and self.cached_scan_results:
            album_list = [album['path'] for album in self.cached_scan_results]
            try:
                current_album_index = album_list.index(folder_path)
            except ValueError:
                # 如果当前路径不在列表中，不传递索引
                pass
        
        viewer_manager.open_album(folder_path, album_list=album_list, current_album_index=current_album_index)
    
    def show_settings(self):
        """显示设置对话框"""
        try:
            from src.ui.components.settings_dialog import SettingsDialog
            settings_dialog = SettingsDialog(self.root, self.config_manager, self.style_manager)
            settings_dialog.show()
        except Exception as e:
            print(f"打开设置对话框失败: {e}")
            messagebox.showerror("错误", f"无法打开设置对话框: {str(e)}")
    
    def on_filter_changed(self, filter_value):
        """处理筛选条件变化"""
        try:
            print(f"筛选条件变化: {filter_value}")
            
            # 应用筛选到相册网格
            if self.album_grid:
                self.album_grid.apply_filter(filter_value)
                
                # 更新状态栏显示筛选统计
                if self.status_bar:
                    stats = self.album_grid.get_filter_stats()
                    current_count = len(self.album_grid.albums) if self.album_grid.albums else 0
                    total_count = stats.get("全部", 0)
                    
                    if filter_value == "全部":
                        filter_text = f"显示全部 {total_count} 个相册"
                    else:
                        filter_text = f"筛选: {filter_value} ({current_count}/{total_count})"
                    
                    self.status_bar.set_status(filter_text)
                    
        except Exception as e:
            print(f"处理筛选条件变化时出错: {e}")
            import traceback
            traceback.print_exc()

    def on_closing(self):
        """窗口关闭时保存配置并清理资源"""
        try:
            # 保存窗口大小
            self.config_manager.config['window_size'] = self.root.geometry()
            self.config_manager.save_config()
            
            # 清理图片缓存
            try:
                from src.utils.image_cache import get_image_cache
                cache = get_image_cache()
                if cache and hasattr(cache, 'shutdown'):
                    # 显示缓存统计
                    stats = cache.get_cache_stats()
                    print(f"关闭时缓存统计: {stats}")
                    cache.shutdown()
            except Exception as e:
                print(f"清理图片缓存时出错: {e}")
            
        except Exception as e:
            print(f"保存配置时发生错误: {e}")
        finally:
            self.root.destroy()
