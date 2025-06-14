import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Toplevel
import os
from ...utils.image_utils import ImageProcessor, SlideshowManager
from PIL import Image, ImageTk
import threading
from concurrent.futures import ThreadPoolExecutor
from .style_manager import StyleManager, get_safe_font
from .status_bar import StatusBar


class AlbumGrid:
    """现代化相册网格组件 - 卡片式瀑布流布局"""
    
    def __init__(self, parent, open_callback, favorite_callback, style_manager=None):
        self.parent = parent
        self.open_callback = open_callback
        self.favorite_callback = favorite_callback
        self.is_favorite = None  # 由外部设置
        self.nav_bar = None  # 导航栏引用
        
        # 使用传入的样式管理器或创建新实例
        if style_manager:
            self.style_manager = style_manager
        else:
            from tkinter import ttk
            style = ttk.Style()
            self.style_manager = StyleManager(parent, style)
        
        # 封面缓存
        self.cover_cache = {}  # 缓存封面图片
        self.large_cover_cache = {}  # 缓存大尺寸封面图片
        self.executor = ThreadPoolExecutor(max_workers=3)  # 线程池用于异步加载封面
        
        # 浮动预览框
        self.preview_window = None
        self.preview_timer = None
        
        # 现代化布局参数 - 优化为更大的卡片和瀑布流
        self.columns = 2  # 默认列数，会根据窗口大小动态调整
        self.card_width = 400  # 增大卡片宽度
        self.card_spacing = 20  # 增大间距
        self.card_padding = 20  # 增大内边距
        self.min_columns = 1   # 最小列数
        self.max_columns = 6   # 最大列数
        
        # 确保初始化grid_frame
        self.grid_frame = None
        self.canvas = None
        self.scrollbar = None
        self.scrollable_frame = None
        self.create_widgets()
        self.create_empty_state()
    
    def create_widgets(self):
        """创建现代化网格组件"""
        try:
            # 主容器 - 使用现代化背景
            self.grid_frame = tk.Frame(self.parent, bg=self.style_manager.colors['bg_primary'])
            self.grid_frame.pack(fill='both', expand=True, padx=16, pady=(8, 16))
            
            # 创建Canvas和现代化滚动条
            self.canvas = tk.Canvas(self.grid_frame, 
                                  bg=self.style_manager.colors['bg_primary'], 
                                  highlightthickness=0,
                                  relief='flat')
            
            # 现代化滚动条样式
            style = ttk.Style()
            style.configure('Modern.Vertical.TScrollbar',
                           background=self.style_manager.colors['scrollbar_bg'],
                           troughcolor=self.style_manager.colors['scrollbar_bg'],
                           borderwidth=0,
                           arrowcolor=self.style_manager.colors['scrollbar_thumb'],
                           darkcolor=self.style_manager.colors['scrollbar_thumb'],
                           lightcolor=self.style_manager.colors['scrollbar_thumb'])
            
            self.scrollbar = ttk.Scrollbar(self.grid_frame, 
                                         orient='vertical', 
                                         command=self.canvas.yview,
                                         style='Modern.Vertical.TScrollbar')
            
            self.scrollable_frame = tk.Frame(self.canvas, bg=self.style_manager.colors['bg_primary'])
            
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
            
            # 绑定鼠标滚轮事件 - 改进滚动体验
            self._bind_mousewheel()
            
            # 绑定窗口大小变化事件 - 实现响应式瀑布流
            self._bind_resize_events()
            
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
    
    def _bind_resize_events(self):
        """绑定窗口大小变化事件"""
        def _on_canvas_resize(event):
            # 延迟重新布局，避免频繁调用
            if hasattr(self, '_resize_timer'):
                self.parent.after_cancel(self._resize_timer)
            self._resize_timer = self.parent.after(200, self._relayout_albums)
        
        if self.canvas:
            self.canvas.bind('<Configure>', _on_canvas_resize)
    
    def _relayout_albums(self):
        """重新布局相册卡片"""
        try:
            if hasattr(self, 'albums') and self.albums:
                self._create_modern_album_cards(self.albums)
        except Exception as e:
            print(f"重新布局相册时出错: {e}")
    
    def create_empty_state(self):
        """创建空状态引导页面"""
        self.empty_frame = tk.Frame(self.scrollable_frame, bg=self.style_manager.colors['bg_primary'])
        
        # 空状态容器
        empty_container = tk.Frame(self.empty_frame, 
                                 bg=self.style_manager.colors['card_bg'],
                                 relief='flat',
                                 bd=1)
        empty_container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # 内容区域
        content_area = tk.Frame(empty_container, bg=self.style_manager.colors['card_bg'])
        content_area.pack(fill='both', expand=True, padx=60, pady=60)
        
        # 图标
        icon_label = tk.Label(content_area, 
                            text="📸",
                            font=self.style_manager.fonts['title'],
                            bg=self.style_manager.colors['card_bg'],
                            fg=self.style_manager.colors['accent'])
        icon_label.pack(pady=(0, 20))
        
        # 主标题
        title_label = tk.Label(content_area,
                             text="欢迎使用相册扫描器",
                             font=self.style_manager.fonts['heading'],
                             bg=self.style_manager.colors['card_bg'],
                             fg=self.style_manager.colors['text_primary'])
        title_label.pack(pady=(0, 12))
        
        # 副标题
        subtitle_label = tk.Label(content_area,
                                text="现代化的图片管理工具，让您的相册井然有序",
                                font=self.style_manager.fonts['body'],
                                bg=self.style_manager.colors['card_bg'],
                                fg=self.style_manager.colors['text_secondary'])
        subtitle_label.pack(pady=(0, 30))
        
        # 操作步骤
        steps_frame = tk.Frame(content_area, bg=self.style_manager.colors['card_bg'])
        steps_frame.pack(fill='x', pady=(0, 30))
        
        steps = [
            ("1️⃣", "选择文件夹", "点击\"选择文件夹\"按钮或按 Ctrl+O"),
            ("2️⃣", "扫描相册", "点击\"扫描相册\"按钮或按 Ctrl+S 开始扫描"),
            ("3️⃣", "浏览管理", "在卡片视图中浏览和管理您的相册")
        ]
        
        for icon, title, desc in steps:
            step_frame = tk.Frame(steps_frame, bg=self.style_manager.colors['card_bg'])
            step_frame.pack(fill='x', pady=8)
            
            # 步骤图标
            step_icon = tk.Label(step_frame,
                               text=icon,
                               font=self.style_manager.fonts['subheading'],
                               bg=self.style_manager.colors['card_bg'])
            step_icon.pack(side='left', padx=(0, 12))
            
            # 步骤内容
            step_content = tk.Frame(step_frame, bg=self.style_manager.colors['card_bg'])
            step_content.pack(side='left', fill='x', expand=True)
            
            step_title = tk.Label(step_content,
                                text=title,
                                font=self.style_manager.fonts['body_medium'],
                                bg=self.style_manager.colors['card_bg'],
                                fg=self.style_manager.colors['text_primary'],
                                anchor='w')
            step_title.pack(fill='x')
            
            step_desc = tk.Label(step_content,
                               text=desc,
                               font=self.style_manager.fonts['caption'],
                               bg=self.style_manager.colors['card_bg'],
                               fg=self.style_manager.colors['text_secondary'],
                               anchor='w')
            step_desc.pack(fill='x')
        
        # 快速开始按钮
        quick_start_frame = tk.Frame(content_area, bg=self.style_manager.colors['card_bg'])
        quick_start_frame.pack(pady=(20, 0))
        
        start_btn_style = self.style_manager.get_button_style('primary')
        start_btn = tk.Button(quick_start_frame,
                            text="🚀 快速开始",
                            command=self.quick_start,
                            **start_btn_style,
                            padx=24,
                            pady=12)
        start_btn.pack()
        
        self.style_manager.create_hover_effect(
            start_btn,
            self.style_manager.colors['button_primary_hover'],
            self.style_manager.colors['button_primary']
        )
        
        self.style_manager.add_tooltip(start_btn, "开始选择文件夹并扫描相册")
        
        # 默认显示空状态
        self.show_empty_state()
    
    def quick_start(self):
        """快速开始 - 触发选择文件夹"""
        if hasattr(self.parent, 'browse_folder'):
            self.parent.browse_folder()
        elif self.nav_bar and hasattr(self.nav_bar, 'browse_callback'):
            self.nav_bar.browse_callback()
    
    def show_empty_state(self):
        """显示空状态"""
        # 显示空状态
        self.empty_frame.pack(fill='both', expand=True)
    
    def hide_empty_state(self):
        """隐藏空状态"""
        self.empty_frame.pack_forget()
    
    def _show_empty_state(self):
        """显示空状态（兼容旧方法）"""
        self.show_empty_state()
    
    def update_albums(self, albums):
        """更新相册显示"""
        try:
            self.albums = albums
            
            # 清除现有显示
            if self.scrollable_frame:
                for widget in self.scrollable_frame.winfo_children():
                    widget.destroy()
            
            if not albums:
                self.show_empty_state()
                return
            
            # 隐藏空状态
            self.hide_empty_state()
            
            # 创建现代化相册卡片
            self._create_modern_album_cards(albums)
            
        except Exception as e:
            print(f"更新相册显示时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_cover_async(self, album_path, cover_label):
        """异步加载封面图片"""
        try:
            # 检查缓存
            if album_path in self.cover_cache:
                photo = self.cover_cache[album_path]
                self._update_cover_image(cover_label, photo)
                return
            
            # 在后台线程中加载封面
            def load_cover():
                try:
                    # 获取相册中的第一张图片
                    import glob
                    image_files = []
                    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                        pattern = os.path.join(album_path, f'*{ext}')
                        image_files.extend(glob.glob(pattern))
                        pattern = os.path.join(album_path, f'*{ext.upper()}')
                        image_files.extend(glob.glob(pattern))
                    
                    if image_files:
                        # 按文件名排序，取第一张
                        image_files.sort()
                        first_image = image_files[0]
                        
                        # 加载并调整图片大小
                        from PIL import Image, ImageTk
                        
                        # 安全地打开图片，防止解压缩炸弹攻击
                        try:
                            # 首先检查图片基本信息而不完全加载
                            with Image.open(first_image) as img:
                                # 检查图片尺寸是否合理（限制为50MP）
                                width, height = img.size
                                max_pixels = 50 * 1024 * 1024  # 50兆像素
                                if width * height > max_pixels:
                                    print(f"图片尺寸过大 ({width}x{height}={width*height} pixels)，跳过: {first_image}")
                                    raise ValueError(f"图片尺寸超出限制: {width*height} > {max_pixels}")
                                
                                # 安全加载图片
                                img.load()
                                image = img.copy()
                        except Exception as img_error:
                            print(f"无法安全加载图片 {first_image}: {img_error}")
                            # 尝试下一张图片
                            return  # 修复: 将 continue 改为 return，因为这里不在循环中
                        
                        # 计算缩放比例，保持宽高比 - 使用竖屏比例
                        target_size = (210, 280)  # 3:4 竖屏比例
                        image.thumbnail(target_size, Image.Resampling.LANCZOS)
                        
                        # 转换为PhotoImage
                        photo = ImageTk.PhotoImage(image)
                        
                        # 缓存图片
                        self.cover_cache[album_path] = photo
                        
                        # 在主线程中更新UI
                        cover_label.after(0, lambda: self._update_cover_image(cover_label, photo))
                    else:
                        # 没有图片时显示文件夹图标
                        cover_label.after(0, lambda: cover_label.configure(
                            text='📁\n空相册', 
                            font=self.style_manager.fonts['body'],
                            fg=self.style_manager.colors['text_tertiary']
                        ))
                        
                except Exception as e:
                    print(f"加载封面图片失败: {e}")
                    # 显示错误状态
                    cover_label.after(0, lambda: cover_label.configure(
                        text='❌\n加载失败', 
                        font=self.style_manager.fonts['body'],
                        fg=self.style_manager.colors['error']
                    ))
            
            # 在线程池中执行
            import threading
            thread = threading.Thread(target=load_cover, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"启动封面加载线程失败: {e}")
    
    def _update_cover_image(self, label, photo):
        """更新封面图片"""
        try:
            label.configure(image=photo, text='')
            label.image = photo  # 保持引用
        except Exception as e:
            print(f"更新封面图片失败: {e}")
        
    def _load_cover_image(self, album_path, callback, size=(210, 280)):
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
                        target_cache = self.large_cover_cache if size[0] > 210 else self.cover_cache
                        
                        # 检查缓存
                        if cache_key in target_cache:
                            callback(target_cache[cache_key])
                            return
                        
                        # 安全地加载并调整图片大小
                        try:
                            with Image.open(cover_path) as img:
                                # 检查图片尺寸是否合理（限制为50MP）
                                width, height = img.size
                                max_pixels = 50 * 1024 * 1024  # 50兆像素
                                if width * height > max_pixels:
                                    print(f"图片尺寸过大 ({width}x{height}={width*height} pixels)，跳过: {cover_path}")
                                    return
                                
                                # 安全加载图片
                                img.load()
                                
                                # 直接使用传入的尺寸参数创建缩略图
                                img.thumbnail(size, Image.Resampling.LANCZOS)
                                
                                # 创建背景
                                bg_color = (255, 255, 255, 255)
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
                        except Exception as img_error:
                            print(f"无法安全加载图片 {cover_path}: {img_error}")
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
            # 立即清理之前的预览窗口和所有定时器
            self._hide_preview_window()
            
            # 延迟显示预览窗口（避免鼠标快速移动时频繁弹出）
            self.preview_timer = self.parent.after(500, 
                lambda: self._create_preview_window(event, album_path, album_name))
            
        except Exception as e:
            print(f"显示预览窗口时出错: {e}")
    
    def _create_preview_window(self, event, album_path, album_name):
        """创建预览浮动窗口"""
        try:
            # 再次确保没有现有窗口
            if self.preview_window and self.preview_window.winfo_exists():
                self.preview_window.destroy()
                self.preview_window = None
            
            # 创建顶层窗口
            self.preview_window = tk.Toplevel(self.parent)
            self.preview_window.withdraw()  # 先隐藏
            
            # 设置窗口属性
            self.preview_window.overrideredirect(True)  # 无边框
            self.preview_window.configure(bg='white', relief='solid', bd=2)
            
            # 设置窗口在最顶层
            self.preview_window.attributes('-topmost', True)
            
            # 创建内容框架
            content_frame = tk.Frame(self.preview_window, bg='white', padx=12, pady=12)
            content_frame.pack()
            
            # 标题
            title_label = tk.Label(content_frame, text=album_name,
                                 font=get_safe_font('Arial', 12, 'bold'),
                                 bg='white', fg='black')
            title_label.pack(pady=(0, 8))
            
            # 封面占位符 - 更大的竖屏尺寸 (270x360)
            self.preview_cover_label = tk.Label(content_frame, text="🔄 加载中...",
                                              font=get_safe_font('Arial', 16),
                                              bg='#F2F2F7', fg='#8E8E93',
                                              width=270, height=360)
            self.preview_cover_label.pack()
            
            # 计算窗口位置（跟随鼠标，但避免超出屏幕）
            x = event.x_root + 15
            y = event.y_root + 15
            
            # 获取屏幕尺寸
            screen_width = self.preview_window.winfo_screenwidth()
            screen_height = self.preview_window.winfo_screenheight()
            
            # 预估窗口大小 - 适应更大的封面尺寸
            window_width = 310
            window_height = 420
            
            # 调整位置避免超出屏幕
            if x + window_width > screen_width:
                x = event.x_root - window_width - 15
            if y + window_height > screen_height:
                y = event.y_root - window_height - 15
            
            # 设置窗口位置
            self.preview_window.geometry(f"+{x}+{y}")
            
            # 显示窗口
            self.preview_window.deiconify()
            
            # 异步加载竖屏尺寸封面 - 更大尺寸
            self._load_cover_image(album_path, 
                                 lambda photo: self._update_preview_cover(photo),
                                 size=(270, 360))
            
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
            # 取消所有相关定时器
            if self.preview_timer:
                self.parent.after_cancel(self.preview_timer)
                self.preview_timer = None
                
            # 销毁预览窗口
            if self.preview_window:
                try:
                    if self.preview_window.winfo_exists():
                        self.preview_window.destroy()
                except tk.TclError:
                    # 窗口已经被销毁
                    pass
                finally:
                    self.preview_window = None
                    
            # 清理预览封面标签引用
            if hasattr(self, 'preview_cover_label'):
                self.preview_cover_label = None
                
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
                self.show_empty_state()
                return
            
            # 隐藏空状态
            self.hide_empty_state()
            
            # 隐藏导航栏的启动页（如果存在）
            if hasattr(self, 'nav_bar') and self.nav_bar and hasattr(self.nav_bar, 'hide_start_page'):
                self.nav_bar.hide_start_page()
            
            # 创建现代化相册卡片
            self._create_modern_album_cards(albums)
                
        except Exception as e:
            print(f"显示相册列表时出错: {e}")
            # 创建最基本的显示
            self._create_fallback_display(albums)
    
    def _create_modern_album_cards(self, albums):
        """创建现代化相册卡片"""
        try:
            if not self.scrollable_frame:
                return
            
            # 计算响应式列数 - 优化瀑布流布局
            canvas_width = self.canvas.winfo_width()
            if canvas_width > 1:
                # 根据卡片宽度和间距计算最佳列数
                available_width = canvas_width - (self.card_spacing * 2)  # 减去左右边距
                card_total_width = self.card_width + self.card_spacing
                calculated_columns = max(self.min_columns, available_width // card_total_width)
                self.columns = min(self.max_columns, calculated_columns)
            else:
                # 窗口尚未完全初始化时使用默认值
                self.columns = 2
            
            # 创建网格容器
            grid_container = tk.Frame(self.scrollable_frame, bg=self.style_manager.colors['bg_primary'])
            grid_container.pack(fill='both', expand=True, padx=self.card_spacing, pady=self.card_spacing)
            
            # 创建相册卡片
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
                    
                    row = i // self.columns
                    col = i % self.columns
                    
                    card = self._create_modern_album_card(grid_container, album)
                    card.grid(row=row, column=col, 
                             padx=self.card_spacing//2, 
                             pady=self.card_spacing//2, 
                             sticky='nsew')
                        
                except Exception as e:
                    print(f"显示相册项时出错 {i}: {e}")
                    continue
            
            # 配置网格权重
            for i in range(self.columns):
                grid_container.grid_columnconfigure(i, weight=1)
            
            # 更新滚动区域
            self.scrollable_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
        except Exception as e:
            print(f"创建相册卡片时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_modern_album_card(self, parent, album):
        """创建现代化单个相册卡片"""
        try:
            album_path = album['path']
            album_name = album['name']
            image_count = album.get('image_count', 0)
            
            # 卡片主容器 - 现代化样式
            card = tk.Frame(parent, 
                          bg=self.style_manager.colors['card_bg'],
                          relief='flat',
                          bd=1,
                          highlightthickness=0)
            
            # 添加卡片悬浮效果
            self.style_manager.create_hover_effect(
                card,
                self.style_manager.colors['card_hover'],
                self.style_manager.colors['card_bg']
            )
            
            # 封面区域 - 调整为竖屏比例 (3:4)
            cover_frame = tk.Frame(card, 
                                 bg=self.style_manager.colors['card_bg'], 
                                 height=280)  # 增加高度以适应竖屏比例
            cover_frame.pack(fill='x', padx=self.card_padding, pady=(self.card_padding, 8))
            cover_frame.pack_propagate(False)
            
            # 封面图片容器
            cover_container = tk.Frame(cover_frame, 
                                     bg=self.style_manager.colors['bg_tertiary'],
                                     relief='flat')
            cover_container.pack(fill='both', expand=True)
            
            # 封面图片标签
            cover_label = tk.Label(cover_container, 
                                 bg=self.style_manager.colors['bg_tertiary'], 
                                 text='📷\n加载中...',
                                 font=self.style_manager.fonts['body'], 
                                 fg=self.style_manager.colors['text_tertiary'])
            cover_label.pack(fill='both', expand=True)
            
            # 绑定封面预览事件
            def on_cover_enter(event):
                self._show_preview_window(event, album_path, album_name)
            
            def on_cover_leave(event):
                self._schedule_hide_preview()
            
            # 为封面相关组件绑定事件
            cover_frame.bind('<Enter>', on_cover_enter)
            cover_frame.bind('<Leave>', on_cover_leave)
            cover_container.bind('<Enter>', on_cover_enter)
            cover_container.bind('<Leave>', on_cover_leave)
            cover_label.bind('<Enter>', on_cover_enter)
            cover_label.bind('<Leave>', on_cover_leave)
            
            # 异步加载封面 - 使用竖屏比例 (3:4)
            self._load_cover_image(album_path, 
                                 lambda photo, label=cover_label: self._update_cover(label, photo),
                                 size=(210, 280))  # 竖屏比例尺寸
            
            # 信息区域
            info_frame = tk.Frame(card, bg=self.style_manager.colors['card_bg'])
            info_frame.pack(fill='x', padx=self.card_padding, pady=(0, 8))
            
            # 相册名称
            name_label = tk.Label(info_frame, 
                                text=album_name,
                                font=self.style_manager.fonts['subheading'],
                                bg=self.style_manager.colors['card_bg'], 
                                fg=self.style_manager.colors['text_primary'], 
                                anchor='w')
            name_label.pack(fill='x')
            
            # 统计信息容器
            stats_frame = tk.Frame(info_frame, bg=self.style_manager.colors['card_bg'])
            stats_frame.pack(fill='x', pady=(4, 0))
            
            # 图片数量
            count_icon = tk.Label(stats_frame, 
                                text="🖼️",
                                font=self.style_manager.fonts['caption'],
                                bg=self.style_manager.colors['card_bg'])
            count_icon.pack(side='left')
            
            count_label = tk.Label(stats_frame, 
                                 text=f'{image_count} 张图片',
                                 font=self.style_manager.fonts['caption'],
                                 bg=self.style_manager.colors['card_bg'], 
                                 fg=self.style_manager.colors['text_secondary'])
            count_label.pack(side='left', padx=(4, 0))
            
            # 路径显示（可选）
            if len(album_path) > 50:
                display_path = "..." + album_path[-47:]
            else:
                display_path = album_path
                
            path_label = tk.Label(info_frame, 
                                text=display_path,
                                font=self.style_manager.fonts['small'],
                                bg=self.style_manager.colors['card_bg'], 
                                fg=self.style_manager.colors['text_tertiary'], 
                                anchor='w')
            path_label.pack(fill='x', pady=(2, 0))
            
            # 为路径添加完整路径的工具提示
            self.style_manager.add_tooltip(path_label, album_path)
            
            # 按钮区域
            button_frame = tk.Frame(card, bg=self.style_manager.colors['card_bg'])
            button_frame.pack(fill='x', padx=self.card_padding, pady=(0, self.card_padding))
            
            # 打开按钮
            open_btn_style = self.style_manager.get_button_style('primary')
            open_btn = tk.Button(button_frame, 
                               text='📂 打开相册',
                               command=lambda: self.open_callback(album_path),
                               **open_btn_style,
                               padx=12, 
                               pady=6)
            open_btn.pack(side='left')
            
            self.style_manager.create_hover_effect(
                open_btn,
                self.style_manager.colors['button_primary_hover'],
                self.style_manager.colors['button_primary']
            )
            
            self.style_manager.add_tooltip(open_btn, f"打开相册：{album_name}")
            
            # 收藏按钮
            is_fav = self.is_favorite(album_path) if self.is_favorite else False
            fav_text = '⭐ 已收藏' if is_fav else '☆ 收藏'
            fav_style = self.style_manager.get_button_style('secondary')
            
            if is_fav:
                fav_style['fg'] = self.style_manager.colors['warning']
            
            fav_btn = tk.Button(button_frame, 
                              text=fav_text,
                              command=lambda: self._toggle_favorite(album_path, fav_btn),
                              **fav_style,
                              padx=12, 
                              pady=6)
            fav_btn.pack(side='right')
            
            self.style_manager.create_hover_effect(
                fav_btn,
                self.style_manager.colors['button_secondary_hover'],
                fav_style['bg']
            )
            
            tooltip_text = "取消收藏" if is_fav else "添加到收藏"
            self.style_manager.add_tooltip(fav_btn, tooltip_text)
            
            return card
            
        except Exception as e:
            print(f"创建相册卡片时出错: {e}")
            # 返回一个现代化的错误卡片
            error_card = tk.Frame(parent, 
                                bg=self.style_manager.colors['error_light'],
                                relief='flat', 
                                bd=1)
            error_label = tk.Label(error_card, 
                                 text='❌ 加载失败',
                                 font=self.style_manager.fonts['body'],
                                 bg=self.style_manager.colors['error_light'], 
                                 fg=self.style_manager.colors['error'])
            error_label.pack(pady=20)
            return error_card
    
    def _toggle_favorite(self, album_path, button):
        """切换收藏状态并更新按钮"""
        try:
            # 调用收藏回调
            self.favorite_callback(album_path)
            
            # 更新按钮显示
            is_fav = self.is_favorite(album_path) if self.is_favorite else False
            fav_text = '⭐ 已收藏' if is_fav else '☆ 收藏'
            button.configure(text=fav_text)
            
            if is_fav:
                button.configure(fg=self.style_manager.colors['warning'])
            else:
                button.configure(fg=self.style_manager.colors['text_primary'])
                
        except Exception as e:
            print(f"切换收藏状态时出错: {e}")
    
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
        # 取消之前的隐藏定时器
        if self.preview_timer:
            self.parent.after_cancel(self.preview_timer)
            
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