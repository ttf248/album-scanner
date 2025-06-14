import tkinter as tk
from ..utils.image_utils import ImageProcessor

class FallbackUIManager:
    """备用UI管理器"""
    
    def __init__(self, app):
        self.app = app
    
    def create_fallback_ui(self):
        """创建备用简化UI"""
        print("使用简化界面模式")
        
        # 简单的顶部框架
        top_frame = tk.Frame(self.app.root, bg='lightgray')
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # 路径输入
        tk.Label(top_frame, text="相册路径:", bg='lightgray').pack(side='left')
        path_entry = tk.Entry(top_frame, textvariable=self.app.path_var, width=50)
        path_entry.pack(side='left', padx=5)
        
        # 按钮 - 添加快捷键提示
        tk.Button(top_frame, text="浏览 (Ctrl+O)", command=self.app.browse_folder).pack(side='left', padx=2)
        tk.Button(top_frame, text="扫描 (Ctrl+S)", command=self.app.scan_albums).pack(side='left', padx=2)
        tk.Button(top_frame, text="最近 (Ctrl+R)", command=self.app.show_recent_albums).pack(side='left', padx=2)
        tk.Button(top_frame, text="收藏 (Ctrl+F)", command=self.app.show_favorites).pack(side='left', padx=2)
        
        # 主内容区域
        main_frame = tk.Frame(self.app.root, bg='white')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 创建简单的相册网格
        try:
            from .components.album_grid import AlbumGrid  # 从components导入
            self.app.album_grid = AlbumGrid(main_frame, self.app.open_album, self.app.toggle_favorite)
            self.app.album_grid.is_favorite = self.app.config_manager.is_favorite
        except Exception as e:
            print(f"创建简化相册网格时出错: {e}")
            import traceback
            traceback.print_exc()
            # 创建最基本的显示
            self.app.album_grid = self._create_basic_album_display(main_frame)
        
        # 简单的状态显示
        self._create_simple_status_bar()
    
    def _create_basic_album_display(self, parent):
        """创建最基本的相册显示"""
        app_instance = self.app  # 保存对主应用的引用
        
        class BasicAlbumDisplay:
            def __init__(self, parent):
                self.parent = parent
                self.display_frame = tk.Frame(parent, bg='white')
                self.display_frame.pack(fill='both', expand=True)
                # 确保有grid_frame属性以保持兼容性
                self.grid_frame = self.display_frame
                
            def display_albums(self, albums):
                try:
                    # 清除现有内容
                    for widget in self.display_frame.winfo_children():
                        widget.destroy()
                    
                    if not albums or len(albums) == 0:
                        tk.Label(self.display_frame, text="暂无相册", 
                               bg='white', fg='gray').pack(expand=True)
                        return
                    
                    # 简单列表显示
                    for album in albums:
                        try:
                            frame = tk.Frame(self.display_frame, bg='lightblue', relief='raised', bd=1)
                            frame.pack(fill='x', padx=5, pady=2)
                            
                            # 确保相册信息完整
                            album_name = album.get('name', '未知相册')
                            image_count = album.get('image_count', 0)
                            album_path = album.get('path', '')
                            
                            tk.Label(frame, text=f"{album_name} ({image_count} 张图片)", 
                                   bg='lightblue').pack(side='left', padx=10, pady=5)
                            
                            if album_path:
                                tk.Button(frame, text="打开", 
                                        command=lambda p=album_path: app_instance.open_album(p)).pack(side='right', padx=5)
                        except Exception as e:
                            print(f"显示相册时出错: {e}")
                            continue
                except Exception as e:
                    print(f"BasicAlbumDisplay.display_albums出错: {e}")
        
        return BasicAlbumDisplay(parent)
    
    def _create_simple_status_bar(self):
        """创建简单的状态栏"""
        status_frame = tk.Frame(self.app.root, bg='lightgray', height=30)
        status_frame.pack(side='bottom', fill='x')
        status_frame.pack_propagate(False)
        
        self.app.status_var = tk.StringVar(value="使用简化界面模式")
        status_label = tk.Label(status_frame, textvariable=self.app.status_var, bg='lightgray')
        status_label.pack(side='left', padx=10, pady=5)
        
        # 创建一个简单的状态栏对象
        class SimpleStatusBar:
            def __init__(self, status_var):
                self.status_var = status_var
            def set_status(self, message):
                self.status_var.set(message)
            def set_info(self, message):
                pass  # 简化版本不显示额外信息
        
        self.app.status_bar = SimpleStatusBar(self.app.status_var)
