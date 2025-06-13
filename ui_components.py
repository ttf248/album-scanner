import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Toplevel
import os
from image_utils import ImageProcessor, SlideshowManager

class StyleManager:
    """现代化样式管理器，基于Material Design 3.0"""
    
    def __init__(self, root, style):
        self.root = root
        self.style = style
        self.setup_colors()
        self.setup_styles()
    
    def setup_colors(self):
        """设置现代化配色方案"""
        # Material Design 3.0 配色
        self.surface = '#fef7ff'          # 主背景色
        self.surface_variant = '#f5f0f7'  # 次要背景色
        self.primary = '#6750a4'          # 主色调
        self.primary_variant = '#4f378b'  # 主色调变体
        self.secondary = '#625b71'        # 次要色调
        self.on_surface = '#1d1b20'       # 表面文字色
        self.on_surface_variant = '#49454f' # 次要文字色
        self.outline = '#79747e'          # 边框色
        self.outline_variant = '#cac4d0'  # 次要边框色
        self.surface_container = '#f3edf7' # 容器背景色
        self.surface_container_high = '#ede7f6' # 高对比容器背景
        self.error = '#ba1a1a'            # 错误色
        self.on_error = '#ffffff'         # 错误文字色
        self.success = '#006d3c'          # 成功色
        
        # 投影效果
        self.shadow_color = '#00000018'
    
    def setup_styles(self):
        """设置现代化样式"""
        self.root.configure(bg=self.surface)
        
        # 基础样式
        self.style.configure('TFrame', background=self.surface)
        self.style.configure('TLabel', 
                           background=self.surface, 
                           foreground=self.on_surface,
                           font=('SF Pro Display', 10))
        
        # 现代化按钮样式
        self.style.element_create("Modern.Button.button", "from", "default")
        self.style.layout("Modern.TButton",
                         [('Modern.Button.button', {'children': [
                             ('Button.focus', {'children': [
                                 ('Button.padding', {'children': [
                                     ('Button.label', {'sticky': 'nswe'})
                                 ], 'sticky': 'nswe'})
                             ], 'sticky': 'nswe'})
                         ], 'sticky': 'nswe'})])
        
        # 主按钮样式
        self.style.configure("Primary.TButton",
                           background=self.primary,
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(20, 12),
                           font=('SF Pro Display', 10, 'bold'),
                           relief='flat')
        
        self.style.map("Primary.TButton",
                      background=[('active', self.primary_variant), 
                                ('pressed', self.primary_variant)],
                      foreground=[('active', 'white'), ('pressed', 'white')],
                      relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        
        # 次要按钮样式
        self.style.configure("Secondary.TButton",
                           background=self.surface_container,
                           foreground=self.on_surface,
                           borderwidth=1,
                           focuscolor='none',
                           padding=(16, 10),
                           font=('SF Pro Display', 10),
                           relief='flat')
        
        self.style.map("Secondary.TButton",
                      background=[('active', self.surface_container_high), 
                                ('pressed', self.surface_container_high)],
                      bordercolor=[('active', self.primary), ('pressed', self.primary)],
                      relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        
        # 图标按钮样式
        self.style.configure("Icon.TButton",
                           background=self.surface,
                           foreground=self.on_surface_variant,
                           borderwidth=0,
                           focuscolor='none',
                           padding=(12, 12),
                           font=('SF Pro Display', 12),
                           relief='flat')
        
        self.style.map("Icon.TButton",
                      background=[('active', self.surface_container), 
                                ('pressed', self.surface_container)],
                      foreground=[('active', self.primary), ('pressed', self.primary)])

        # 现代化卡片样式
        self.style.configure('Card.TFrame',
                           background='white',
                           relief='flat',
                           borderwidth=0,
                           padding=20)
        
        self.style.configure('CardElevated.TFrame',
                           background='white',
                           relief='solid',
                           borderwidth=1,
                           bordercolor=self.outline_variant,
                           padding=20)
        
        # 输入框样式
        self.style.configure('Modern.TEntry',
                           fieldbackground='white',
                           borderwidth=2,
                           bordercolor=self.outline_variant,
                           focuscolor=self.primary,
                           padding=12,
                           font=('SF Pro Display', 11))
        
        self.style.map('Modern.TEntry',
                      bordercolor=[('focus', self.primary)])
        
        # 标签样式
        self.style.configure('Title.TLabel',
                           font=('SF Pro Display', 24, 'bold'),
                           foreground=self.on_surface)
        
        self.style.configure('Subtitle.TLabel',
                           font=('SF Pro Display', 14),
                           foreground=self.on_surface_variant)
        
        self.style.configure('Body.TLabel',
                           font=('SF Pro Display', 12),
                           foreground=self.on_surface)
        
        self.style.configure('Caption.TLabel',
                           font=('SF Pro Display', 10),
                           foreground=self.on_surface_variant)

class StatusBar:
    """现代化状态栏组件"""
    
    def __init__(self, parent):
        self.parent = parent
        self.create_widgets()
        
    def create_widgets(self):
        self.status_frame = ttk.Frame(self.parent, style='Card.TFrame', padding="16 12")
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=(0, 20))
        
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                                    style='Body.TLabel')
        self.status_label.pack(side=tk.LEFT)
        
        # 右侧信息
        self.info_var = tk.StringVar()
        self.info_label = ttk.Label(self.status_frame, textvariable=self.info_var, 
                                  style='Caption.TLabel')
        self.info_label.pack(side=tk.RIGHT)
    
    def set_status(self, message):
        """设置状态信息"""
        self.status_var.set(message)
    
    def set_info(self, info):
        """设置右侧信息"""
        self.info_var.set(info)

class NavigationBar:
    """现代化导航栏组件"""
    
    def __init__(self, parent, on_browse, on_scan, path_var, on_recent, on_favorites):
        self.parent = parent
        self.on_browse = on_browse
        self.on_scan = on_scan
        self.path_var = path_var
        self.on_recent = on_recent
        self.on_favorites = on_favorites
        self.create_widgets()
    
    def create_widgets(self):
        # 主容器
        main_container = ttk.Frame(self.parent, padding="20 20 20 0")
        main_container.pack(fill=tk.X)
        
        # 头部区域
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 应用标题
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        app_title = ttk.Label(title_frame, text="相册扫描器", style='Title.TLabel')
        app_title.pack(anchor=tk.W)
        
        subtitle = ttk.Label(title_frame, text="发现和管理您的图片收藏", style='Subtitle.TLabel')
        subtitle.pack(anchor=tk.W, pady=(4, 0))
        
        # 快捷操作按钮
        action_frame = ttk.Frame(header_frame)
        action_frame.pack(side=tk.RIGHT)
        
        recent_btn = ttk.Button(action_frame, text="📚 最近浏览", 
                               command=self.on_recent, 
                               style="Secondary.TButton")
        recent_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        fav_btn = ttk.Button(action_frame, text="⭐ 收藏夹", 
                           command=self.on_favorites, 
                           style="Secondary.TButton")
        fav_btn.pack(side=tk.LEFT)
        
        # 搜索和扫描区域
        search_container = ttk.Frame(main_container, style='CardElevated.TFrame')
        search_container.pack(fill=tk.X, pady=(0, 20))
        
        # 路径输入区域
        path_frame = ttk.Frame(search_container)
        path_frame.pack(fill=tk.X, pady=(0, 16))
        
        path_label = ttk.Label(path_frame, text="选择相册文件夹", style='Body.TLabel')
        path_label.pack(anchor=tk.W, pady=(0, 8))
        
        input_frame = ttk.Frame(path_frame)
        input_frame.pack(fill=tk.X)
        
        self.path_entry = ttk.Entry(input_frame, textvariable=self.path_var, 
                                   style='Modern.TEntry', font=('SF Pro Display', 11))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        
        browse_btn = ttk.Button(input_frame, text="📁 浏览", 
                               command=self.on_browse, 
                               style="Secondary.TButton")
        browse_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        scan_btn = ttk.Button(input_frame, text="🔍 开始扫描", 
                             command=self.on_scan, 
                             style="Primary.TButton")
        scan_btn.pack(side=tk.LEFT)

class AlbumGrid:
    """现代化相册网格显示组件"""
    
    def __init__(self, parent, on_album_click, on_favorite_toggle):
        self.parent = parent
        self.on_album_click = on_album_click
        self.on_favorite_toggle = on_favorite_toggle
        self.create_widgets()
    
    def create_widgets(self):
        # 主容器
        self.main_container = ttk.Frame(self.parent, padding="20 0 20 0")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建画布和滚动条
        canvas_frame = ttk.Frame(self.main_container)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0, bg='#fef7ff')
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # 响应式网格列数
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.cols = 3
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_canvas_configure(self, event):
        # 根据窗口宽度调整列数
        width = event.width
        if width < 800:
            self.cols = 1
        elif width < 1200:
            self.cols = 2
        elif width < 1600:
            self.cols = 3
        else:
            self.cols = 4
        
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=width)
    
    def clear_albums(self):
        """清空相册显示"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
    
    def display_albums(self, albums):
        """显示相册列表"""
        self.clear_albums()
        
        if not albums:
            self._show_empty_state()
            return
        
        # 创建网格布局
        for i, album in enumerate(albums):
            row = i // self.cols
            col = i % self.cols
            self.create_album_card(album, row, col)
    
    def _show_empty_state(self):
        """显示空状态"""
        empty_frame = ttk.Frame(self.scrollable_frame, padding="40")
        empty_frame.pack(fill=tk.BOTH, expand=True)
        
        empty_icon = ttk.Label(empty_frame, text="📷", font=('SF Pro Display', 48))
        empty_icon.pack(pady=(0, 16))
        
        empty_title = ttk.Label(empty_frame, text="暂无相册", style='Title.TLabel')
        empty_title.pack(pady=(0, 8))
        
        empty_desc = ttk.Label(empty_frame, text="选择文件夹并点击扫描来发现您的相册", 
                              style='Subtitle.TLabel')
        empty_desc.pack()
    
    def create_album_card(self, album, row, col):
        """创建现代化相册卡片"""
        # 卡片容器
        card_frame = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        card_frame.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        
        # 配置网格权重
        self.scrollable_frame.grid_columnconfigure(col, weight=1)
        
        # 卡片内容容器
        content_frame = ttk.Frame(card_frame, style='Card.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # 封面图片容器
        cover_container = ttk.Frame(content_frame, style='Card.TFrame')
        cover_container.pack(fill=tk.X, pady=(0, 16))
        
        # 创建封面
        if album['cover_image']:
            photo = ImageProcessor.create_thumbnail(album['cover_image'], size=(280, 200))
            if photo:
                cover_label = ttk.Label(cover_container, image=photo, 
                                      style='Card.TLabel', cursor='hand2')
                cover_label.image = photo
                cover_label.pack()
                cover_label.bind("<Button-1>", 
                               lambda e, path=album['path']: self.on_album_click(path))
                
                # 添加悬停效果
                cover_label.bind('<Enter>', lambda e: self._on_card_enter(card_frame))
                cover_label.bind('<Leave>', lambda e: self._on_card_leave(card_frame))
        
        # 相册信息
        info_frame = ttk.Frame(content_frame, style='Card.TFrame')
        info_frame.pack(fill=tk.X)
        
        # 相册名称
        name_label = ttk.Label(info_frame, text=album['name'], 
                              style='Body.TLabel', 
                              font=('SF Pro Display', 14, 'bold'))
        name_label.pack(anchor=tk.W, pady=(0, 4))
        
        # 相册统计
        stats_frame = ttk.Frame(info_frame, style='Card.TFrame')
        stats_frame.pack(fill=tk.X, pady=(0, 12))
        
        count_text = f"📸 {album.get('image_count', len(album['image_files']))} 张"
        count_label = ttk.Label(stats_frame, text=count_text, style='Caption.TLabel')
        count_label.pack(side=tk.LEFT)
        
        if 'folder_size' in album:
            size_label = ttk.Label(stats_frame, text=f"💾 {album['folder_size']}", 
                                 style='Caption.TLabel')
            size_label.pack(side=tk.RIGHT)
        
        # 操作按钮
        action_frame = ttk.Frame(info_frame, style='Card.TFrame')
        action_frame.pack(fill=tk.X)
        
        # 查看按钮
        view_btn = ttk.Button(action_frame, text="打开相册", 
                             command=lambda: self.on_album_click(album['path']),
                             style="Primary.TButton")
        view_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        # 收藏按钮
        fav_icon = "⭐" if self.is_favorite(album['path']) else "☆"
        fav_btn = ttk.Button(action_frame, text=fav_icon, 
                           command=lambda: self.on_favorite_toggle(album['path']),
                           style="Icon.TButton", width=3)
        fav_btn.pack(side=tk.RIGHT)
    
    def is_favorite(self, album_path):
        """检查是否为收藏"""
        return False  # 默认实现
    
    def _on_card_enter(self, card_frame):
        """卡片悬停效果"""
        card_frame.configure(style='CardElevated.TFrame')
        
    def _on_card_leave(self, card_frame):
        """卡片离开效果"""
        card_frame.configure(style='Card.TFrame')

class ImageViewer:
    """现代化图片查看器组件"""
    
    def __init__(self, parent, image_files, config_manager=None):
        self.parent = parent
        self.image_files = image_files
        self.current_index = 0
        self.config_manager = config_manager
        self.zoom_mode = tk.StringVar(value=config_manager.get_zoom_mode() if config_manager else "fit")
        self.status_var = tk.StringVar()
        self.rotation = 0
        self.slideshow = SlideshowManager(self)
        self.fullscreen = False
        
        self.setup_window()
        self.create_widgets()
        self.bind_events()
        self.load_image()
    
    def setup_window(self):
        """设置窗口样式"""
        self.parent.configure(bg='#1c1c1e')
        
    def create_widgets(self):
        # 主容器
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部工具栏
        toolbar = ttk.Frame(main_frame, style='Card.TFrame', padding="16 12")
        toolbar.pack(fill=tk.X, padx=20, pady=(20, 0))
        
        # 左侧导航
        nav_frame = ttk.Frame(toolbar)
        nav_frame.pack(side=tk.LEFT)
        
        ttk.Button(nav_frame, text="⬅️", command=self.prev_image, 
                  style="Icon.TButton", width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="➡️", command=self.next_image, 
                  style="Icon.TButton", width=4).pack(side=tk.LEFT, padx=2)
        
        # 中间工具
        tools_frame = ttk.Frame(toolbar)
        tools_frame.pack(side=tk.LEFT, padx=40)
        
        ttk.Button(tools_frame, text="↺", command=self.rotate_left, 
                  style="Icon.TButton", width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(tools_frame, text="↻", command=self.rotate_right, 
                  style="Icon.TButton", width=4).pack(side=tk.LEFT, padx=2)
        
        self.play_btn = ttk.Button(tools_frame, text="▶️", command=self.toggle_slideshow, 
                                  style="Icon.TButton", width=4)
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(tools_frame, text="ℹ️", command=self.show_exif, 
                  style="Icon.TButton", width=4).pack(side=tk.LEFT, padx=2)
        
        # 右侧状态
        status_frame = ttk.Frame(toolbar)
        status_frame.pack(side=tk.RIGHT)
        
        ttk.Label(status_frame, textvariable=self.status_var, 
                 style='Body.TLabel').pack()
        
        # 图片显示区域
        image_area = ttk.Frame(main_frame)
        image_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.image_container = ttk.Frame(image_area, style='Card.TFrame')
        self.image_container.pack(fill=tk.BOTH, expand=True)
        
        self.image_label = ttk.Label(self.image_container, style='Card.TLabel')
        self.image_label.pack(expand=True)
        
        # 底部信息栏
        info_bar = ttk.Frame(main_frame, style='Card.TFrame', padding="16 12")
        info_bar.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.image_info = ttk.Label(info_bar, text='', style='Caption.TLabel')
        self.image_info.pack(side=tk.LEFT)
        
        # 缩放模式选择
        zoom_frame = ttk.Frame(info_bar)
        zoom_frame.pack(side=tk.RIGHT)
        
        ttk.Label(zoom_frame, text="缩放:", style='Caption.TLabel').pack(side=tk.LEFT, padx=(0, 8))
        
        modes = [("适应", "fit"), ("原始", "original"), ("填充", "fill")]
        for text, value in modes:
            ttk.Radiobutton(zoom_frame, text=text, variable=self.zoom_mode, 
                           value=value, command=self.on_zoom_change).pack(side=tk.LEFT, padx=4)
    
    def bind_events(self):
        """绑定键盘事件"""
        self.parent.bind("<Left>", lambda e: self.prev_image())
        self.parent.bind("<Right>", lambda e: self.next_image())
        self.parent.bind("<Escape>", lambda e: self.exit_fullscreen() if self.fullscreen else self.parent.destroy())
        self.parent.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.parent.bind("<space>", lambda e: self.toggle_slideshow())
        self.parent.bind("f", lambda e: self.set_zoom_mode("fit"))
        self.parent.bind("o", lambda e: self.set_zoom_mode("original"))
        self.parent.bind("l", lambda e: self.set_zoom_mode("fill"))
        self.parent.bind("r", lambda e: self.rotate_right())
        self.parent.bind("i", lambda e: self.show_exif())
        self.parent.focus_set()
    
    def set_zoom_mode(self, mode):
        """设置缩放模式"""
        self.zoom_mode.set(mode)
        self.on_zoom_change()
    
    def on_zoom_change(self):
        """缩放模式改变时保存配置"""
        if self.config_manager:
            self.config_manager.set_zoom_mode(self.zoom_mode.get())
        self.load_image()
    
    def toggle_fullscreen(self):
        """切换全屏模式"""
        if self.fullscreen:
            self.exit_fullscreen()
        else:
            self.parent.attributes('-fullscreen', True)
            self.fullscreen = True
    
    def exit_fullscreen(self):
        """退出全屏"""
        self.parent.attributes('-fullscreen', False)
        self.fullscreen = False
    
    def rotate_left(self):
        """向左旋转90度"""
        self.rotation = (self.rotation - 90) % 360
        self.load_image()
    
    def rotate_right(self):
        """向右旋转90度"""
        self.rotation = (self.rotation + 90) % 360
        self.load_image()
    
    def toggle_slideshow(self):
        """切换幻灯片播放"""
        if self.slideshow.is_playing:
            self.slideshow.stop_slideshow()
            self.play_btn.config(text="▶️")
        else:
            self.slideshow.start_slideshow()
            self.play_btn.config(text="⏸️")
    
    def show_exif(self):
        """显示EXIF信息"""
        if not (0 <= self.current_index < len(self.image_files)):
            return
        
        image_path = self.image_files[self.current_index]
        exif_data = ImageProcessor.get_image_exif(image_path)
        
        # 创建现代化EXIF信息窗口
        exif_window = Toplevel(self.parent)
        exif_window.title("图片信息")
        exif_window.geometry("500x700")
        exif_window.configure(bg='#fef7ff')
        
        # 标题
        title_frame = ttk.Frame(exif_window, padding="20 20 20 10")
        title_frame.pack(fill=tk.X)
        
        ttk.Label(title_frame, text="图片信息", style='Title.TLabel').pack(anchor=tk.W)
        ttk.Label(title_frame, text=os.path.basename(image_path), 
                 style='Subtitle.TLabel').pack(anchor=tk.W, pady=(4, 0))
        
        # 内容区域
        content_frame = ttk.Frame(exif_window, padding="20 10 20 20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 滚动文本框
        text_widget = tk.Text(content_frame, wrap=tk.WORD, 
                             font=('SF Pro Display', 10),
                             bg='white', fg='#1d1b20',
                             borderwidth=0, padx=16, pady=16)
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 显示EXIF信息
        text_widget.insert(tk.END, f"📁 文件路径\n{image_path}\n\n")
        for key, value in exif_data.items():
            text_widget.insert(tk.END, f"📋 {key}\n{value}\n\n")
        
        text_widget.config(state=tk.DISABLED)

    def load_image(self):
        """加载当前图片"""
        if not (0 <= self.current_index < len(self.image_files)):
            return
            
        image_path = self.image_files[self.current_index]
        window_width = self.image_container.winfo_width()
        window_height = self.image_container.winfo_height()
        
        if window_width < 10: 
            window_width = 800
        if window_height < 10: 
            window_height = 500
        
        result = ImageProcessor.load_image_with_mode(
            image_path, window_width, window_height, self.zoom_mode.get(), self.rotation)
        
        if result[0]:
            photo, width, height, orig_width, orig_height = result
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo
            self.status_var.set(f"{self.current_index + 1} / {len(self.image_files)}")
            
            # 显示详细信息
            size_info = f"显示: {width}×{height}"
            if self.zoom_mode.get() != "original":
                size_info += f" (原始: {orig_width}×{orig_height})"
            if self.rotation != 0:
                size_info += f" 旋转: {self.rotation}°"
            
            self.image_info.config(text=f"{os.path.basename(image_path)} • {size_info}")
        else:
            self.image_label.config(text="❌ 无法加载图片", image="")
            self.image_label.image = None

    def prev_image(self):
        """上一张图片"""
        self.current_index = (self.current_index - 1) % len(self.image_files)
        self.load_image()
        
    def next_image(self):
        """下一张图片"""
        self.current_index = (self.current_index + 1) % len(self.image_files)
        self.load_image()
