import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Toplevel
import os
from ..utils.image_utils import ImageProcessor, SlideshowManager
from PIL import Image, ImageTk
import threading
from concurrent.futures import ThreadPoolExecutor
from .components.style_manager import StyleManager, get_safe_font
from .components.status_bar import StatusBar



class NavigationBar:
    """iPhone风格导航栏"""
    
    def __init__(self, parent, browse_callback, scan_callback, path_var, 
                 recent_callback, favorites_callback):
        self.parent = parent
        self.browse_callback = browse_callback
        self.scan_callback = scan_callback
        self.path_var = path_var
        self.recent_callback = recent_callback
        self.favorites_callback = favorites_callback
        self.is_showing_start_page = True
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建导航栏组件"""
        # 顶部工具栏 - 始终显示
        self.toolbar = tk.Frame(self.parent, bg='#F2F2F7', height=80)
        self.toolbar.pack(fill='x', side='top')
        self.toolbar.pack_propagate(False)
        
        # 工具栏内容
        toolbar_content = tk.Frame(self.toolbar, bg='#F2F2F7')
        toolbar_content.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 左侧快速操作按钮
        left_frame = tk.Frame(toolbar_content, bg='#F2F2F7')
        left_frame.pack(side='left')
        
        # 浏览按钮 - 添加快捷键提示
        browse_btn = tk.Button(left_frame, text="📁 选择 (Ctrl+O)",
                              font=get_safe_font('Arial', 12, 'bold'), 
                              bg='#007AFF', fg='white',
                              relief='flat', bd=0, padx=15, pady=8,
                              cursor='hand2', command=self.browse_callback)
        browse_btn.pack(side='left', padx=(0, 8))
        
        # 扫描按钮 - 添加快捷键提示
        scan_btn = tk.Button(left_frame, text="🔍 扫描 (Ctrl+S/F5)",
                            font=get_safe_font('Arial', 12, 'bold'), 
                            bg='#34C759', fg='white',
                            relief='flat', bd=0, padx=15, pady=8,
                            cursor='hand2', command=self.scan_callback)
        scan_btn.pack(side='left', padx=(0, 8))
        
        # 最近浏览按钮 - 添加快捷键提示
        recent_btn = tk.Button(left_frame, text="📚 最近 (Ctrl+R)",
                              font=get_safe_font('Arial', 12, 'bold'), 
                              bg='#FF9500', fg='white',
                              relief='flat', bd=0, padx=15, pady=8,
                              cursor='hand2', command=self.recent_callback)
        recent_btn.pack(side='left', padx=(0, 8))
        
        # 收藏按钮 - 添加快捷键提示
        fav_btn = tk.Button(left_frame, text="⭐ 收藏 (Ctrl+F)",
                           font=get_safe_font('Arial', 12, 'bold'), 
                           bg='#FF9500', fg='white',
                           relief='flat', bd=0, padx=15, pady=8,
                           cursor='hand2', command=self.favorites_callback)
        fav_btn.pack(side='left')
        
        # 中间路径显示
        center_frame = tk.Frame(toolbar_content, bg='#F2F2F7')
        center_frame.pack(side='left', fill='x', expand=True, padx=20)
        
        path_label = tk.Label(center_frame, text="当前路径:", 
                             font=get_safe_font('Arial', 10), 
                             bg='#F2F2F7', fg='#6D6D80')
        path_label.pack(anchor='w')
        
        self.path_entry = tk.Entry(center_frame, textvariable=self.path_var,
                                  font=get_safe_font('Arial', 11), 
                                  bg='#FFFFFF', fg='#1D1D1F',
                                  relief='flat', bd=1, state='readonly')
        self.path_entry.pack(fill='x', ipady=4)
        
        # 启动页容器 - 可以隐藏/显示
        self.start_page_container = tk.Frame(self.parent, bg='#F2F2F7')
        self.start_page_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 创建启动页内容
        self.create_start_page()
    
    def create_start_page(self):
        """创建启动页内容"""
        # 清除现有内容
        for widget in self.start_page_container.winfo_children():
            widget.destroy()
        
        # 英雄区域
        hero_frame = tk.Frame(self.start_page_container, bg='#F2F2F7')
        hero_frame.pack(fill='x', pady=(20, 40))
        
        # 应用图标
        icon_label = tk.Label(hero_frame, text="📱", 
                             font=get_safe_font('Arial', 48), bg='#F2F2F7')
        icon_label.pack(pady=(0, 15))
        
        # 标题
        title_label = tk.Label(hero_frame, text="相册扫描器", 
                              font=get_safe_font('Arial', 28, 'bold'), 
                              bg='#F2F2F7', fg='#1D1D1F')
        title_label.pack(pady=(0, 8))
        
        # 副标题
        subtitle_label = tk.Label(hero_frame, text="iPhone风格的现代化图片管理", 
                                 font=get_safe_font('Arial', 16), 
                                 bg='#F2F2F7', fg='#6D6D80')
        subtitle_label.pack()
        
        # 快速操作提示
        tip_frame = tk.Frame(self.start_page_container, bg='#FFFFFF', relief='flat', bd=0)
        tip_frame.pack(fill='x', pady=(20, 0))
        
        tip_content = tk.Frame(tip_frame, bg='#FFFFFF')
        tip_content.pack(fill='x', padx=30, pady=20)
        
        tip_title = tk.Label(tip_content, text="🚀 快速开始", 
                            font=get_safe_font('Arial', 18, 'bold'), 
                            bg='#FFFFFF', fg='#1D1D1F')
        tip_title.pack(anchor='w', pady=(0, 10))
        
        # 更新快速操作提示，添加快捷键信息
        tips = [
            "1. 点击「📁 选择」按钮或按 Ctrl+O 选择包含图片的文件夹",
            "2. 点击「🔍 扫描」按钮或按 Ctrl+S/F5 自动发现相册",
            "3. 使用 Ctrl+R 查看最近浏览，Ctrl+F 管理收藏夹",
            "4. 在瀑布流中浏览和管理您的相册"
        ]
        
        for tip in tips:
            tip_label = tk.Label(tip_content, text=tip,
                               font=get_safe_font('Arial', 14),
                               bg='#FFFFFF', fg='#6D6D80', anchor='w')
            tip_label.pack(fill='x', pady=2)
    
    def show_start_page(self):
        """显示启动页"""
        if not self.is_showing_start_page:
            self.start_page_container.pack(fill='both', expand=True, padx=20, pady=20)
            self.is_showing_start_page = True
    
    def hide_start_page(self):
        """隐藏启动页"""
        if self.is_showing_start_page:
            self.start_page_container.pack_forget()
            self.is_showing_start_page = False

class AlbumGrid:
    """瀑布流相册网格"""
    
    def __init__(self, parent, open_callback, favorite_callback):
        self.parent = parent
        self.open_callback = open_callback
        self.favorite_callback = favorite_callback
        self.is_favorite = None  # 由外部设置
        self.nav_bar = None  # 导航栏引用
        
        # 封面缓存
        self.cover_cache = {}  # 缓存封面图片
        self.large_cover_cache = {}  # 缓存大尺寸封面图片
        self.executor = ThreadPoolExecutor(max_workers=3)  # 线程池用于异步加载封面
        
        # 浮动预览框
        self.preview_window = None
        self.preview_timer = None
        
        # 确保初始化grid_frame
        self.grid_frame = None
        self.canvas = None
        self.scrollbar = None
        self.scrollable_frame = None
        self.create_widgets()
    
    def create_widgets(self):
        """创建带滚动功能的网格组件"""
        try:
            # 创建主容器
            self.grid_frame = tk.Frame(self.parent, bg='#F2F2F7')
            self.grid_frame.pack(fill='both', expand=True)
            
            # 创建Canvas和滚动条
            self.canvas = tk.Canvas(self.grid_frame, bg='#F2F2F7', highlightthickness=0)
            self.scrollbar = tk.Scrollbar(self.grid_frame, orient="vertical", command=self.canvas.yview)
            self.scrollable_frame = tk.Frame(self.canvas, bg='#F2F2F7')
            
            # 配置滚动
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            )
            
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            # 布局Canvas和滚动条
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")
            
            # 绑定鼠标滚轮事件
            self._bind_mousewheel()
            
            # 显示初始状态
            self._show_empty_state()
            
        except Exception as e:
            print(f"创建AlbumGrid组件时出错: {e}")
            # 创建一个基本的框架作为备用
            self.grid_frame = tk.Frame(self.parent, bg='white')
            self.grid_frame.pack(fill='both', expand=True)
            
            # 显示错误信息
            error_label = tk.Label(self.grid_frame, text="界面初始化失败，使用简化模式", 
                                 bg='white', fg='red')
            error_label.pack(expand=True)
    
    def _bind_mousewheel(self):
        """绑定鼠标滚轮事件"""
        def _on_mousewheel(event):
            if self.canvas:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            if self.canvas:
                self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            if self.canvas:
                self.canvas.unbind_all("<MouseWheel>")
        
        if self.canvas:
            self.canvas.bind('<Enter>', _bind_to_mousewheel)
            self.canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def _show_empty_state(self):
        """显示空状态"""
        try:
            if self.scrollable_frame:
                # 清除现有内容
                for widget in self.scrollable_frame.winfo_children():
                    widget.destroy()
                
                # 显示空状态提示
                empty_label = tk.Label(self.scrollable_frame, text="请选择文件夹并扫描相册", 
                                      font=get_safe_font('Arial', 16), 
                                      bg='#F2F2F7', fg='#6D6D80')
                empty_label.pack(expand=True, pady=100)
        except Exception as e:
            print(f"显示空状态时出错: {e}")
        
    def _load_cover_image(self, album_path, callback, size=(120, 120)):
        """异步加载封面图片"""
        def load_cover():
            try:
                # 查找相册中的第一张图片作为封面
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
                
                for file in os.listdir(album_path):
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        cover_path = os.path.join(album_path, file)
                        
                        # 根据尺寸选择缓存
                        cache_key = f"{cover_path}_{size[0]}x{size[1]}"
                        target_cache = self.large_cover_cache if size[0] > 120 else self.cover_cache
                        
                        # 检查缓存
                        if cache_key in target_cache:
                            callback(target_cache[cache_key])
                            return
                        
                        # 加载并调整图片大小
                        with Image.open(cover_path) as img:
                            # 创建缩略图
                            img.thumbnail(size, Image.Resampling.LANCZOS)
                            
                            # 创建背景
                            bg_color = (242, 242, 247, 255) if size[0] <= 120 else (255, 255, 255, 255)
                            bg = Image.new('RGBA', size, bg_color)
                            
                            # 计算居中位置
                            img_w, img_h = img.size
                            x = (size[0] - img_w) // 2
                            y = (size[1] - img_h) // 2
                            
                            # 确保图片有alpha通道
                            if img.mode != 'RGBA':
                                img = img.convert('RGBA')
                            
                            # 粘贴到背景上
                            bg.paste(img, (x, y), img if img.mode == 'RGBA' else None)
                            
                            # 转换为PhotoImage
                            photo = ImageTk.PhotoImage(bg)
                            
                            # 缓存图片
                            target_cache[cache_key] = photo
                            
                            # 回调显示
                            callback(photo)
                            return
                
                # 如果没有找到图片，返回默认图标
                callback(None)
                
            except Exception as e:
                print(f"加载封面失败 {album_path}: {e}")
                callback(None)
        
        # 在线程池中执行
        self.executor.submit(load_cover)
    
    def _show_preview_window(self, event, album_path, album_name):
        """显示预览浮动窗口"""
        try:
            # 清除之前的定时器
            if self.preview_timer:
                self.parent.after_cancel(self.preview_timer)
                self.preview_timer = None
            
            # 关闭之前的预览窗口
            self._hide_preview_window()
            
            # 延迟显示预览窗口（避免鼠标快速移动时频繁弹出）
            self.preview_timer = self.parent.after(500, 
                lambda: self._create_preview_window(event, album_path, album_name))
            
        except Exception as e:
            print(f"显示预览窗口时出错: {e}")
    
    def _create_preview_window(self, event, album_path, album_name):
        """创建预览浮动窗口"""
        try:
            # 创建顶层窗口
            self.preview_window = tk.Toplevel(self.parent)
            self.preview_window.withdraw()  # 先隐藏
            
            # 设置窗口属性
            self.preview_window.overrideredirect(True)  # 无边框
            self.preview_window.configure(bg='white', relief='solid', bd=2)
            
            # 设置窗口在最顶层
            self.preview_window.attributes('-topmost', True)
            
            # 创建内容框架
            content_frame = tk.Frame(self.preview_window, bg='white', padx=10, pady=10)
            content_frame.pack()
            
            # 标题
            title_label = tk.Label(content_frame, text=album_name,
                                 font=get_safe_font('Arial', 12, 'bold'),
                                 bg='white', fg='black')
            title_label.pack(pady=(0, 8))
            
            # 封面占位符 - 更大尺寸
            self.preview_cover_label = tk.Label(content_frame, text="🔄 加载中...",
                                              font=get_safe_font('Arial', 16),
                                              bg='#F2F2F7', fg='#8E8E93',
                                              width=200, height=200)
            self.preview_cover_label.pack()
            
            # 计算窗口位置（跟随鼠标，但避免超出屏幕）
            x = event.x_root + 15
            y = event.y_root + 15
            
            # 获取屏幕尺寸
            screen_width = self.preview_window.winfo_screenwidth()
            screen_height = self.preview_window.winfo_screenheight()
            
            # 预估窗口大小
            window_width = 240
            window_height = 280
            
            # 调整位置避免超出屏幕
            if x + window_width > screen_width:
                x = event.x_root - window_width - 15
            if y + window_height > screen_height:
                y = event.y_root - window_height - 15
            
            # 设置窗口位置
            self.preview_window.geometry(f"+{x}+{y}")
            
            # 显示窗口
            self.preview_window.deiconify()
            
            # 异步加载大尺寸封面
            self._load_cover_image(album_path, 
                                 lambda photo: self._update_preview_cover(photo),
                                 size=(200, 200))
            
            # 绑定鼠标离开事件
            self._bind_preview_events()
            
        except Exception as e:
            print(f"创建预览窗口时出错: {e}")
            self._hide_preview_window()
    
    def _update_preview_cover(self, photo):
        """更新预览窗口的封面"""
        try:
            if (photo and self.preview_window and 
                self.preview_window.winfo_exists() and 
                hasattr(self, 'preview_cover_label') and 
                self.preview_cover_label.winfo_exists()):
                
                self.preview_cover_label.configure(image=photo, text="")
                self.preview_cover_label.image = photo  # 保持引用
                
        except Exception as e:
            print(f"更新预览封面时出错: {e}")
    
    def _bind_preview_events(self):
        """绑定预览窗口事件"""
        try:
            if self.preview_window and self.preview_window.winfo_exists():
                # 鼠标进入预览窗口时保持显示
                self.preview_window.bind('<Enter>', self._on_preview_enter)
                # 鼠标离开预览窗口时隐藏
                self.preview_window.bind('<Leave>', self._on_preview_leave)
                
                # 为预览窗口内的所有组件绑定事件
                for widget in self.preview_window.winfo_children():
                    self._bind_widget_events(widget)
                    
        except Exception as e:
            print(f"绑定预览事件时出错: {e}")
    
    def _bind_widget_events(self, widget):
        """递归绑定组件事件"""
        try:
            widget.bind('<Enter>', self._on_preview_enter)
            widget.bind('<Leave>', self._on_preview_leave)
            
            # 递归绑定子组件
            for child in widget.winfo_children():
                self._bind_widget_events(child)
                
        except Exception as e:
            print(f"绑定组件事件时出错: {e}")
    
    def _on_preview_enter(self, event):
        """鼠标进入预览窗口"""
        # 取消隐藏定时器
        if self.preview_timer:
            self.parent.after_cancel(self.preview_timer)
            self.preview_timer = None
    
    def _on_preview_leave(self, event):
        """鼠标离开预览窗口"""
        # 延迟隐藏窗口（给用户时间移动鼠标回来）
        self.preview_timer = self.parent.after(300, self._hide_preview_window)
    
    def _hide_preview_window(self):
        """隐藏预览窗口"""
        try:
            if self.preview_timer:
                self.parent.after_cancel(self.preview_timer)
                self.preview_timer = None
                
            if self.preview_window and self.preview_window.winfo_exists():
                self.preview_window.destroy()
                self.preview_window = None
                
        except Exception as e:
            print(f"隐藏预览窗口时出错: {e}")

    def display_albums(self, albums):
        """显示相册（带滚动支持和封面）"""
        try:
            # 确保组件存在
            if not hasattr(self, 'scrollable_frame') or self.scrollable_frame is None:
                print("scrollable_frame不存在，重新创建")
                self.create_widgets()
                
            # 清除现有内容
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            if not albums or len(albums) == 0:
                # 显示空状态
                empty_label = tk.Label(self.scrollable_frame, text="暂无相册", 
                                      font=get_safe_font('Arial', 16), 
                                      bg='#F2F2F7', fg='#6D6D80')
                empty_label.pack(expand=True, pady=100)
                return
            
            # 隐藏导航栏的启动页（如果存在）
            if hasattr(self, 'nav_bar') and self.nav_bar and hasattr(self.nav_bar, 'hide_start_page'):
                self.nav_bar.hide_start_page()
            
            # 创建相册列表显示
            for i, album in enumerate(albums):
                try:
                    # 验证相册数据完整性
                    if not isinstance(album, dict):
                        continue
                        
                    album_name = album.get('name', '未知相册')
                    image_count = album.get('image_count', 0)
                    album_path = album.get('path', '')
                    
                    if not album_path:
                        continue
                    
                    # 创建相册卡片 - 增加高度以容纳封面
                    album_frame = tk.Frame(self.scrollable_frame, bg='white', relief='solid', bd=1)
                    album_frame.pack(fill='x', padx=15, pady=8)
                    
                    # 主要内容框架 - 使用水平布局
                    main_frame = tk.Frame(album_frame, bg='white')
                    main_frame.pack(fill='x', padx=15, pady=15)
                    
                    # 左侧封面区域
                    cover_frame = tk.Frame(main_frame, bg='white', width=120, height=120)
                    cover_frame.pack(side='left', padx=(0, 15))
                    cover_frame.pack_propagate(False)  # 保持固定大小
                    
                    # 封面占位符
                    cover_label = tk.Label(cover_frame, text="📁", 
                                         font=get_safe_font('Arial', 48),
                                         bg='#F2F2F7', fg='#8E8E93',
                                         width=120, height=120, cursor='hand2')
                    cover_label.pack(fill='both')
                    
                    # 封面点击事件 - 预览相册
                    cover_label.bind('<Button-1>', 
                                   lambda e, path=album_path: self.open_callback(path))
                    
                    # 封面悬停事件 - 显示预览
                    # cover_label.bind('<Enter>', 
                    #                lambda e, path=album_path, name=album_name: 
                    #                self._show_preview_window(e, path, name))
                    cover_label.bind('<Leave>', 
                                   lambda e: self._schedule_hide_preview())
                    
                    # 右侧信息区域
                    info_frame = tk.Frame(main_frame, bg='white')
                    info_frame.pack(side='left', fill='both', expand=True)
                    
                    # 名称
                    name_label = tk.Label(info_frame, text=album_name, 
                                         font=get_safe_font('Arial', 16, 'bold'), 
                                         bg='white', fg='black', anchor='w')
                    name_label.pack(fill='x', pady=(0, 5))
                    
                    # 统计信息
                    stats_text = f"📷 {image_count} 张图片"
                    if 'folder_size' in album and album['folder_size']:
                        stats_text += f"  💾 {album['folder_size']}"
                    stats_label = tk.Label(info_frame, text=stats_text, 
                                          font=get_safe_font('Arial', 12), 
                                          bg='white', fg='#6D6D80', anchor='w')
                    stats_label.pack(fill='x', pady=(0, 5))
                    
                    # 路径信息
                    path_text = f"📁 {album_path}"
                    if len(path_text) > 60:
                        path_text = path_text[:57] + "..."
                    path_label = tk.Label(info_frame, text=path_text, 
                                         font=get_safe_font('Arial', 10), 
                                         bg='white', fg='#8E8E93', anchor='w')
                    path_label.pack(fill='x', pady=(0, 10))
                    
                    # 按钮框架
                    btn_frame = tk.Frame(info_frame, bg='white')
                    btn_frame.pack(fill='x')
                    
                    # 打开按钮 - 增大尺寸
                    open_btn = tk.Button(btn_frame, text="🔍 打开相册", 
                                       font=get_safe_font('Arial', 11, 'bold'), 
                                       bg='#007AFF', fg='white',
                                       relief='flat', bd=0, padx=20, pady=8,
                                       cursor='hand2',
                                       command=lambda path=album_path: self.open_callback(path))
                    open_btn.pack(side='left', padx=(0, 10))
                    
                    # 收藏按钮 - 改进样式
                    is_fav = self.is_favorite(album_path) if self.is_favorite else False
                    fav_text = "⭐ 已收藏" if is_fav else "☆ 收藏"
                    fav_color = '#FF9500' if is_fav else '#8E8E93'
                    fav_btn = tk.Button(btn_frame, text=fav_text, 
                                      font=get_safe_font('Arial', 11), 
                                      bg=fav_color, fg='white',
                                      relief='flat', bd=0, padx=15, pady=8,
                                      cursor='hand2',
                                      command=lambda path=album_path: self.favorite_callback(path))
                    fav_btn.pack(side='left')
                    
                    # 异步加载封面图片
                    self._load_cover_image(album_path, 
                                         lambda photo, label=cover_label: self._update_cover(label, photo))
                    
                    # 添加悬停效果
                    self._add_hover_effects(album_frame, open_btn, fav_btn)
                        
                except Exception as e:
                    print(f"显示相册项时出错 {i}: {e}")
                    continue
            
            # 更新滚动区域
            self.scrollable_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
        except Exception as e:
            print(f"显示相册列表时出错: {e}")
            # 创建最基本的显示
            self._create_fallback_display(albums)
    
    def _add_hover_effects(self, album_frame, open_btn, fav_btn):
        """添加悬停效果"""
        try:
            # 相册卡片悬停效果
            def on_album_enter(event):
                album_frame.configure(relief='solid', bd=2)
                
            def on_album_leave(event):
                album_frame.configure(relief='solid', bd=1)
            
            album_frame.bind('<Enter>', on_album_enter)
            album_frame.bind('<Leave>', on_album_leave)
            
            # 按钮悬停效果
            def on_open_btn_enter(event):
                open_btn.configure(bg='#0056D6')
                
            def on_open_btn_leave(event):
                open_btn.configure(bg='#007AFF')
                
            open_btn.bind('<Enter>', on_open_btn_enter)
            open_btn.bind('<Leave>', on_open_btn_leave)
            
            # 收藏按钮悬停效果
            def on_fav_btn_enter(event):
                current_bg = fav_btn.cget('bg')
                if current_bg == '#FF9500':  # 已收藏
                    fav_btn.configure(bg='#E6830C')
                else:  # 未收藏
                    fav_btn.configure(bg='#6D6D80')
                    
            def on_fav_btn_leave(event):
                current_bg = fav_btn.cget('bg')
                if current_bg == '#E6830C':  # 已收藏悬停
                    fav_btn.configure(bg='#FF9500')
                else:  # 未收藏悬停
                    fav_btn.configure(bg='#8E8E93')
                    
            fav_btn.bind('<Enter>', on_fav_btn_enter)
            fav_btn.bind('<Leave>', on_fav_btn_leave)
            
        except Exception as e:
            print(f"添加悬停效果时出错: {e}")
    
    def _create_fallback_display(self, albums):
        """创建基本的显示方式作为备用"""
        try:
            # 清除现有内容
            if hasattr(self, 'scrollable_frame') and self.scrollable_frame:
                for widget in self.scrollable_frame.winfo_children():
                    widget.destroy()
                
                # 创建简单的列表显示
                error_label = tk.Label(self.scrollable_frame, 
                                     text="界面组件出错，使用简化显示", 
                                     font=get_safe_font('Arial', 14), 
                                     bg='#F2F2F7', fg='#FF3B30')
                error_label.pack(pady=10)
                
                # 简单显示相册
                for album in albums:
                    try:
                        album_name = album.get('name', '未知相册')
                        album_path = album.get('path', '')
                        image_count = album.get('image_count', 0)
                        
                        simple_frame = tk.Frame(self.scrollable_frame, bg='white', relief='solid', bd=1)
                        simple_frame.pack(fill='x', padx=10, pady=2)
                        
                        info_text = f"{album_name} ({image_count} 张图片)"
                        tk.Label(simple_frame, text=info_text, bg='white', anchor='w').pack(side='left', padx=10, pady=5)
                        
                        if album_path:
                            tk.Button(simple_frame, text="打开", 
                                    command=lambda p=album_path: self.open_callback(p)).pack(side='right', padx=10)
                    except Exception as e:
                        print(f"创建简化相册项时出错: {e}")
                        continue
                        
        except Exception as e:
            print(f"创建备用显示时出错: {e}")
    
    def _update_cover(self, label, photo):
        """更新封面图片"""
        try:
            if photo and label.winfo_exists():
                label.configure(image=photo, text="")
                label.image = photo  # 保持引用
        except Exception as e:
            print(f"更新封面时出错: {e}")
    
    def _schedule_hide_preview(self):
        """计划隐藏预览窗口"""
        # 延迟隐藏，给用户时间移动到预览窗口
        self.preview_timer = self.parent.after(200, self._hide_preview_window)

    def __del__(self):
        """清理资源"""
        try:
            # 清理预览窗口
            self._hide_preview_window()
            
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=False)
        except:
            pass

class ImageViewer:
    """图片查看器"""
    
    def __init__(self, parent, image_files, config_manager):
        self.parent = parent
        self.image_files = image_files
        self.config_manager = config_manager
        self.current_index = 0
        self.current_image = None
        self.zoom_factor = 1.0
        self.is_fullscreen = False
        self.rotation = 0  # 旋转角度
        
        # 设置窗口属性
        self.parent.configure(bg='#1D1D1F')
        
        self.create_widgets()
        self.bind_events()
        # 延迟加载图片，确保窗口已完全创建
        self.parent.after(100, self.load_current_image)
    
    def create_widgets(self):
        """创建查看器组件"""
        # 顶部工具栏
        self.toolbar = tk.Frame(self.parent, bg='#2C2C2E', height=60)
        self.toolbar.pack(side='top', fill='x')
        self.toolbar.pack_propagate(False)
        
        # 工具栏内容
        toolbar_content = tk.Frame(self.toolbar, bg='#2C2C2E')
        toolbar_content.pack(fill='both', expand=True, padx=15, pady=10)
        
        # 左侧文件信息
        left_frame = tk.Frame(toolbar_content, bg='#2C2C2E')
        left_frame.pack(side='left', fill='y')
        
        self.file_info_var = tk.StringVar()
        info_label = tk.Label(left_frame, textvariable=self.file_info_var,
                             font=get_safe_font('Arial', 12, 'bold'),
                             bg='#2C2C2E', fg='white')
        info_label.pack(anchor='w')
        
        # 更新快捷键提示，更详细的信息
        shortcut_label = tk.Label(left_frame, text="⌨️ 快捷键: ←→切换 +/-缩放 R旋转 F11全屏 I信息 H帮助 ESC退出",
                                 font=get_safe_font('Arial', 9),
                                 bg='#2C2C2E', fg='#8E8E93')
        shortcut_label.pack(anchor='w', pady=(2, 0))
        
        # 右侧控制按钮
        btn_frame = tk.Frame(toolbar_content, bg='#2C2C2E')
        btn_frame.pack(side='right')
        
        # 旋转按钮 - 添加快捷键提示
        rotate_left_btn = tk.Button(btn_frame, text="↺ (Shift+R)", 
                                   font=get_safe_font('Arial', 10),
                                   bg='#48484A', fg='white', relief='flat',
                                   padx=8, command=self.rotate_left)
        rotate_left_btn.pack(side='left', padx=2)
        
        rotate_right_btn = tk.Button(btn_frame, text="↻ (R)", 
                                    font=get_safe_font('Arial', 10),
                                    bg='#48484A', fg='white', relief='flat',
                                    padx=8, command=self.rotate_right)
        rotate_right_btn.pack(side='left', padx=2)
        
        # 分隔线
        separator = tk.Label(btn_frame, text="|", bg='#2C2C2E', fg='#48484A')
        separator.pack(side='left', padx=5)
        
        # 缩放按钮 - 添加快捷键提示
        zoom_out_btn = tk.Button(btn_frame, text="缩小 (-)", 
                               font=get_safe_font('Arial', 10),
                               bg='#48484A', fg='white', relief='flat',
                               padx=8, command=self.zoom_out)
        zoom_out_btn.pack(side='left', padx=2)
        
        zoom_in_btn = tk.Button(btn_frame, text="放大 (+)", 
                              font=get_safe_font('Arial', 10),
                              bg='#48484A', fg='white', relief='flat',
                              padx=8, command=self.zoom_in)
        zoom_in_btn.pack(side='left', padx=2)
        
        reset_btn = tk.Button(btn_frame, text="重置 (0)", 
                            font=get_safe_font('Arial', 10),
                            bg='#48484A', fg='white', relief='flat',
                            padx=8, command=self.reset_zoom)
        reset_btn.pack(side='left', padx=2)
        
        # 主图片显示区域
        self.image_frame = tk.Frame(self.parent, bg='#1D1D1F')
        self.image_frame.pack(fill='both', expand=True)
        
        # 图片标签
        self.image_label = tk.Label(self.image_frame, bg='#1D1D1F', cursor='hand2')
        self.image_label.pack(expand=True)
        
        # 底部控制栏
        self.control_frame = tk.Frame(self.parent, bg='#2C2C2E', height=70)
        self.control_frame.pack(side='bottom', fill='x')
        self.control_frame.pack_propagate(False)
        
        # 控制栏内容
        control_content = tk.Frame(self.control_frame, bg='#2C2C2E')
        control_content.pack(fill='both', expand=True, padx=20, pady=15)
        
        # 左侧导航按钮 - 添加快捷键提示
        nav_frame = tk.Frame(control_content, bg='#2C2C2E')
        nav_frame.pack(side='left')
        
        prev_btn = tk.Button(nav_frame, text="⬅ 上一张 (←)", 
                           font=get_safe_font('Arial', 12, 'bold'),
                           bg='#007AFF', fg='white', relief='flat',
                           padx=20, pady=8, command=self.prev_image)
        prev_btn.pack(side='left')
        
        next_btn = tk.Button(nav_frame, text="下一张 (→) ➡", 
                           font=get_safe_font('Arial', 12, 'bold'),
                           bg='#007AFF', fg='white', relief='flat',
                           padx=20, pady=8, command=self.next_image)
        next_btn.pack(side='left', padx=(10, 0))
        
        # 中间缩放信息
        zoom_info_frame = tk.Frame(control_content, bg='#2C2C2E')
        zoom_info_frame.pack(expand=True)
        
        self.zoom_var = tk.StringVar()
        zoom_label = tk.Label(zoom_info_frame, textvariable=self.zoom_var,
                             font=get_safe_font('Arial', 11),
                             bg='#2C2C2E', fg='#8E8E93')
        zoom_label.pack()
        
        # 右侧进度信息
        progress_frame = tk.Frame(control_content, bg='#2C2C2E')
        progress_frame.pack(side='right')
        
        self.progress_var = tk.StringVar()
        progress_label = tk.Label(progress_frame, textvariable=self.progress_var,
                                font=get_safe_font('Arial', 12, 'bold'),
                                bg='#2C2C2E', fg='white')
        progress_label.pack()
    
    def bind_events(self):
        """绑定键盘和鼠标事件"""
        # 键盘事件 - 绑定到窗口
        self.parent.bind('<KeyPress>', self.on_key_press)
        self.parent.focus_set()
        
        # 双击全屏
        self.image_label.bind('<Double-Button-1>', self.toggle_fullscreen)
        
        # 鼠标滚轮缩放
        self.image_label.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # 窗口大小变化时重新调整图片
        self.parent.bind('<Configure>', self.on_window_resize)
        
        # 为了确保键盘事件能被捕获，也绑定到图片标签
        self.image_label.bind('<Button-1>', lambda e: self.parent.focus_set())
    
    def on_key_press(self, event):
        """键盘事件处理 - 支持多种快捷键"""
        key = event.keysym.lower()
        
        # 图片导航
        if key in ['left', 'a']:
            self.prev_image()
        elif key in ['right', 'd']:
            self.next_image()
        elif key in ['up', 'w']:
            self.prev_image()
        elif key in ['down', 's']:
            self.next_image()
        elif key in ['home']:
            self.goto_first_image()
        elif key in ['end']:
            self.goto_last_image()
        
        # 缩放控制
        elif key in ['plus', 'equal', 'kp_add']:
            self.zoom_in()
        elif key in ['minus', 'kp_subtract']:
            self.zoom_out()
        elif key in ['0', 'kp_0']:
            self.reset_zoom()
        
        # 旋转控制
        elif key in ['r']:
            self.rotate_right()
        elif key in ['shift_r'] or (event.state & 0x1 and key == 'r'):  # Shift+R
            self.rotate_left()
        elif key in ['ctrl_r'] or (event.state & 0x4 and key == 'r'):  # Ctrl+R
            self.reset_rotation()
        
        # 全屏控制
        elif key in ['f11', 'f']:
            self.toggle_fullscreen()
        elif key in ['escape']:
            if self.is_fullscreen:
                self.toggle_fullscreen()
            else:
                self.parent.destroy()
        
        # 其他功能
        elif key in ['space']:
            self.start_slideshow()
        elif key in ['i']:
            self.show_image_info()
        elif key in ['h', 'f1']:
            self.show_help()
        
        # 防止事件传播
        return "break"
    
    def load_current_image(self):
        """加载当前图片"""
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        try:
            image_path = self.image_files[self.current_index]
            
            # 使用PIL加载图片
            with Image.open(image_path) as img:
                # 应用旋转
                if self.rotation != 0:
                    img = img.rotate(-self.rotation, expand=True)
                
                # 获取原始尺寸
                original_width, original_height = img.size
                
                # 获取显示区域尺寸
                self.image_frame.update_idletasks()
                display_width = self.image_frame.winfo_width() or 800
                display_height = self.image_frame.winfo_height() or 600
                
                # 计算缩放比例
                if display_width > 100 and display_height > 100:
                    scale_x = display_width / original_width
                    scale_y = display_height / original_height
                    scale = min(scale_x, scale_y) * 0.9  # 留一些边距
                    
                    # 应用用户缩放
                    scale *= self.zoom_factor
                    
                    # 计算新尺寸
                    new_width = max(1, int(original_width * scale))
                    new_height = max(1, int(original_height * scale))
                    
                    # 调整图片大小
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # 转换为PhotoImage
                    self.current_image = ImageTk.PhotoImage(resized_img)
                    
                    # 显示图片
                    self.image_label.configure(image=self.current_image, text="")
                    self.image_label.image = self.current_image  # 保持引用
            
            # 更新信息显示
            filename = os.path.basename(image_path)
            self.file_info_var.set(f"📸 {filename}")
            
            progress_text = f"{self.current_index + 1} / {len(self.image_files)}"
            self.progress_var.set(progress_text)
            
            # 更新缩放信息
            zoom_percent = int(self.zoom_factor * 100)
            zoom_text = f"缩放: {zoom_percent}%"
            if self.rotation != 0:
                zoom_text += f" | 旋转: {self.rotation}°"
            self.zoom_var.set(zoom_text)
            
        except Exception as e:
            print(f"加载图片失败 {image_path}: {e}")
            # 显示错误信息
            error_text = f"无法加载图片\n{os.path.basename(image_path) if image_path else '未知文件'}"
            self.image_label.configure(image='', text=error_text, 
                                     font=get_safe_font('Arial', 14),
                                     fg='#FF3B30')
    
    def prev_image(self):
        """上一张图片"""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()
    
    def next_image(self):
        """下一张图片"""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_current_image()
    
    def goto_first_image(self):
        """跳转到第一张图片"""
        if self.image_files:
            self.current_index = 0
            self.load_current_image()
    
    def goto_last_image(self):
        """跳转到最后一张图片"""
        if self.image_files:
            self.current_index = len(self.image_files) - 1
            self.load_current_image()
    
    def zoom_in(self):
        """放大"""
        self.zoom_factor *= 1.2
        if self.zoom_factor > 10:  # 限制最大缩放
            self.zoom_factor = 10
        self.load_current_image()
    
    def zoom_out(self):
        """缩小"""
        self.zoom_factor /= 1.2
        if self.zoom_factor < 0.1:  # 限制最小缩放
            self.zoom_factor = 0.1
        self.load_current_image()
    
    def reset_zoom(self):
        """重置缩放"""
        self.zoom_factor = 1.0
        self.load_current_image()
    
    def rotate_left(self):
        """向左旋转90度"""
        self.rotation = (self.rotation + 90) % 360
        self.load_current_image()
    
    def rotate_right(self):
        """向右旋转90度"""
        self.rotation = (self.rotation - 90) % 360
        self.load_current_image()
    
    def reset_rotation(self):
        """重置旋转"""
        self.rotation = 0
        self.load_current_image()
    
    def toggle_fullscreen(self, event=None):
        """切换全屏模式"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            # 进入全屏
            self.toolbar.pack_forget()
            self.control_frame.pack_forget()
            self.parent.attributes('-fullscreen', True)
        else:
            # 退出全屏
            self.parent.attributes('-fullscreen', False)
            self.toolbar.pack(side='top', fill='x')
            self.control_frame.pack(side='bottom', fill='x')
        
        # 重新加载图片以适应新尺寸
        self.parent.after(100, self.load_current_image)
    
    def start_slideshow(self):
        """开始/暂停幻灯片播放"""
        # 这里可以实现幻灯片功能
        messagebox.showinfo("幻灯片", "幻灯片功能开发中...")
    
    def show_image_info(self):
        """显示图片信息"""
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        try:
            image_path = self.image_files[self.current_index]
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode
            
            file_size = os.path.getsize(image_path)
            size_mb = file_size / (1024 * 1024)
            
            info_text = f"""图片信息：
文件名: {os.path.basename(image_path)}
尺寸: {width} × {height} 像素
格式: {format_name}
模式: {mode}
文件大小: {size_mb:.2f} MB
路径: {image_path}"""
            
            messagebox.showinfo("图片信息", info_text)
            
        except Exception as e:
            messagebox.showerror("错误", f"无法获取图片信息: {e}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """图片查看器快捷键：

📸 图片导航：
  ← / A / ↑ / W      上一张图片
  → / D / ↓ / S      下一张图片
  Home               第一张图片
  End                最后一张图片

🔍 缩放控制：
  + / =              放大图片
  -                  缩小图片
  0                  重置缩放 (100%)

🔄 旋转控制：
  R                  向右旋转90°
  Shift + R          向左旋转90°
  Ctrl + R           重置旋转 (0°)

🖥️ 显示控制：
  F11 / F            切换全屏模式
  ESC                退出全屏/关闭窗口
  空格                开始/暂停幻灯片

ℹ️ 其他功能：
  I                  显示图片详细信息
  H / F1             显示此快捷键帮助

💡 提示：
  • 双击图片也可切换全屏
  • 使用鼠标滚轮进行缩放
  • 点击图片获得键盘焦点"""
        
        messagebox.showinfo("快捷键帮助", help_text)
    
    def on_mouse_wheel(self, event):
        """鼠标滚轮事件"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def on_window_resize(self, event):
        """窗口大小变化事件"""
        # 只在主窗口大小变化时重新加载图片
        if event.widget == self.parent:
            self.parent.after(100, self.load_current_image)
        self.load_image()
