import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Toplevel
import os
from image_utils import ImageProcessor, SlideshowManager
from PIL import Image, ImageTk

def get_safe_font(font_family, size, style=None):
    """获取安全的字体配置"""
    try:
        if style:
            return (font_family, size, style)
        else:
            return (font_family, size)
    except:
        # 如果字体不可用，使用默认字体
        if style:
            return ('Arial', size, style)
        else:
            return ('Arial', size)

class StyleManager:
    """样式管理器"""
    
    def __init__(self, root, style):
        self.root = root
        self.style = style
        
        # 设置颜色主题
        self.colors = {
            'bg_primary': '#F2F2F7',      # iOS 浅灰背景
            'bg_secondary': '#FFFFFF',     # 白色背景
            'text_primary': '#000000',     # 主要文字
            'text_secondary': '#6D6D80',   # 次要文字
            'accent': '#007AFF',           # iOS 蓝色
            'success': '#34C759',          # 成功绿色
            'warning': '#FF9500',          # 警告橙色
            'error': '#FF3B30',            # 错误红色
            'card_bg': '#FFFFFF',          # 卡片背景
            'border': '#C6C6C8'            # 边框颜色
        }
        
        # 设置字体
        self.fonts = {
            'title': get_safe_font('SF Pro Display', 24, 'bold'),
            'heading': get_safe_font('SF Pro Display', 18, 'bold'),
            'body': get_safe_font('SF Pro Display', 14),
            'caption': get_safe_font('SF Pro Display', 12),
            'button': get_safe_font('SF Pro Display', 14, 'bold')
        }
        
        self.configure_styles()
    
    def configure_styles(self):
        """配置样式"""
        # 设置根窗口背景
        self.root.configure(bg=self.colors['bg_primary'])

class StatusBar:
    """状态栏组件"""
    
    def __init__(self, parent):
        self.parent = parent
        self.status_var = tk.StringVar()
        self.info_var = tk.StringVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建状态栏组件"""
        # 状态栏主框架
        self.status_frame = tk.Frame(self.parent, bg='#F2F2F7', height=40)
        self.status_frame.pack(side='bottom', fill='x')
        self.status_frame.pack_propagate(False)
        
        # 内容框架
        content_frame = tk.Frame(self.status_frame, bg='#F2F2F7')
        content_frame.pack(fill='both', expand=True, padx=20, pady=8)
        
        # 状态标签
        self.status_label = tk.Label(content_frame, textvariable=self.status_var,
                                   font=get_safe_font('Arial', 12), bg='#F2F2F7', fg='#1D1D1F')
        self.status_label.pack(side='left')
        
        # 信息标签
        self.info_label = tk.Label(content_frame, textvariable=self.info_var,
                                 font=get_safe_font('Arial', 12), bg='#F2F2F7', fg='#6D6D80')
        self.info_label.pack(side='right')
    
    def set_status(self, message):
        """设置状态消息"""
        self.status_var.set(message)
    
    def set_info(self, message):
        """设置信息消息"""
        self.info_var.set(message)

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
        
        # 浏览按钮
        browse_btn = tk.Button(left_frame, text="📁 选择",
                              font=get_safe_font('Arial', 12, 'bold'), 
                              bg='#007AFF', fg='white',
                              relief='flat', bd=0, padx=15, pady=8,
                              cursor='hand2', command=self.browse_callback)
        browse_btn.pack(side='left', padx=(0, 8))
        
        # 扫描按钮
        scan_btn = tk.Button(left_frame, text="🔍 扫描",
                            font=get_safe_font('Arial', 12, 'bold'), 
                            bg='#34C759', fg='white',
                            relief='flat', bd=0, padx=15, pady=8,
                            cursor='hand2', command=self.scan_callback)
        scan_btn.pack(side='left', padx=(0, 8))
        
        # 最近浏览按钮
        recent_btn = tk.Button(left_frame, text="📚 最近",
                              font=get_safe_font('Arial', 12, 'bold'), 
                              bg='#FF9500', fg='white',
                              relief='flat', bd=0, padx=15, pady=8,
                              cursor='hand2', command=self.recent_callback)
        recent_btn.pack(side='left', padx=(0, 8))
        
        # 收藏按钮
        fav_btn = tk.Button(left_frame, text="⭐ 收藏",
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
        
        tips = [
            "1. 点击「📁 选择」按钮选择包含图片的文件夹",
            "2. 点击「🔍 扫描」按钮自动发现相册",
            "3. 在瀑布流中浏览和管理您的相册"
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
    """iPhone风格瀑布流相册网格"""
    
    def __init__(self, parent, open_callback, favorite_callback):
        self.parent = parent
        self.open_callback = open_callback
        self.favorite_callback = favorite_callback
        self.is_favorite = None
        self.cols = 3
        self.column_frames = []
        self.nav_bar = None  # 将在主程序中设置
        
        self.create_widgets()
        self.setup_responsive_layout()
    
    def create_widgets(self):
        """创建瀑布流容器"""
        # 主滚动框架 - 初始隐藏
        self.main_frame = tk.Frame(self.parent, bg='#F2F2F7')
        # 初始不显示，等有相册时再显示
        
        # 创建Canvas和Scrollbar
        self.canvas = tk.Canvas(self.main_frame, bg='#F2F2F7', highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#F2F2F7')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def setup_responsive_layout(self):
        """设置响应式布局"""
        def on_window_resize(event):
            if event.widget == self.main_frame:
                width = event.width
                if width > 1200:
                    self.cols = 4
                elif width > 800:
                    self.cols = 3
                else:
                    self.cols = 2
        
        self.main_frame.bind('<Configure>', on_window_resize)
    
    def _on_mousewheel(self, event):
        """处理鼠标滚轮"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def clear_albums(self):
        """清除所有相册"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.column_frames = []
    
    def display_albums(self, albums):
        """显示相册瀑布流"""
        self.clear_albums()
        
        if not albums:
            # 没有相册时显示启动页
            self.main_frame.pack_forget()
            if self.nav_bar:
                self.nav_bar.show_start_page()
            return
        
        # 有相册时隐藏启动页，显示相册
        if self.nav_bar:
            self.nav_bar.hide_start_page()
        
        # 显示相册网格
        self.main_frame.pack(fill='both', expand=True)
        
        # 创建列框架
        self._create_columns()
        
        # 瀑布流布局
        for i, album in enumerate(albums):
            col = i % self.cols
            self.create_album_card(album, self.column_frames[col])

    def _create_columns(self):
        """创建瀑布流列"""
        container = tk.Frame(self.scrollable_frame, bg='#F2F2F7')
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.column_frames = []
        for i in range(self.cols):
            col_frame = tk.Frame(container, bg='#F2F2F7')
            col_frame.pack(side='left', fill='y', padx=8, expand=True)
            self.column_frames.append(col_frame)
    
    def _show_empty_state(self):
        """显示空状态"""
        empty_frame = tk.Frame(self.scrollable_frame, bg='#F2F2F7')
        empty_frame.pack(fill='both', expand=True, pady=100)
        
        # 空状态图标
        empty_icon = tk.Label(empty_frame, text="📷", font=get_safe_font('Arial', 64), 
                            bg='#F2F2F7', fg='#C7C7CC')
        empty_icon.pack(pady=(0, 20))
        
        # 空状态标题
        empty_title = tk.Label(empty_frame, text="暂无相册",
                             font=get_safe_font('Arial', 24, 'bold'),
                             bg='#F2F2F7', fg='#8E8E93')
        empty_title.pack(pady=(0, 8))
        
        # 空状态描述
        empty_desc = tk.Label(empty_frame, text="选择文件夹并点击扫描来发现您的相册",
                            font=get_safe_font('Arial', 17),
                            bg='#F2F2F7', fg='#AEAEB2')
        empty_desc.pack()
    
    def create_album_card(self, album, parent_column):
        """创建iPhone风格相册卡片"""
        # 计算卡片高度（模拟瀑布流效果）
        base_height = 280
        random_height = hash(album['name']) % 80
        card_height = base_height + random_height
        
        # 卡片容器 - iPhone风格圆角
        card_frame = tk.Frame(parent_column, bg='#FFFFFF', relief='flat', bd=0,
                            height=card_height)
        card_frame.pack(fill='x', pady=12)
        card_frame.pack_propagate(False)
        
        # 添加阴影效果模拟
        shadow_frame = tk.Frame(parent_column, bg='#E5E5EA', height=2)
        shadow_frame.pack(fill='x', pady=(0, 1))
        
        # 卡片内容
        content_frame = tk.Frame(card_frame, bg='#FFFFFF')
        content_frame.pack(fill='both', expand=True, padx=16, pady=16)
        
        # 封面图片区域
        cover_frame = tk.Frame(content_frame, bg='#F2F2F7', height=180)
        cover_frame.pack(fill='x', pady=(0, 12))
        cover_frame.pack_propagate(False)
        
        # 加载封面图片
        if album.get('cover_image'):
            self._load_cover_image(cover_frame, album['cover_image'], album['path'])
        else:
            # 默认封面
            default_label = tk.Label(cover_frame, text="📷", 
                                   font=get_safe_font('Arial', 48),
                                   bg='#F2F2F7', fg='#C7C7CC')
            default_label.pack(expand=True)
        
        # 相册信息区域
        info_frame = tk.Frame(content_frame, bg='#FFFFFF')
        info_frame.pack(fill='x')
        
        # 相册名称
        name_label = tk.Label(info_frame, text=album['name'],
                            font=get_safe_font('Arial', 17, 'bold'),
                            bg='#FFFFFF', fg='#000000', anchor='w')
        name_label.pack(fill='x', pady=(0, 4))
        
        # 统计信息
        stats_text = f"{album.get('image_count', len(album['image_files']))} 张照片"
        if 'folder_size' in album:
            stats_text += f" • {album['folder_size']}"
        
        stats_label = tk.Label(info_frame, text=stats_text,
                             font=get_safe_font('Arial', 13),
                             bg='#FFFFFF', fg='#8E8E93', anchor='w')
        stats_label.pack(fill='x', pady=(0, 12))
        
        # 操作按钮区域
        button_frame = tk.Frame(info_frame, bg='#FFFFFF')
        button_frame.pack(fill='x')
        
        # 查看按钮 - iPhone风格
        view_btn = tk.Button(button_frame, text="打开相册",
                           command=lambda: self.open_callback(album['path']),
                           font=get_safe_font('Arial', 15, 'bold'),
                           bg='#007AFF', fg='white',
                           relief='flat', bd=0,
                           padx=20, pady=10,
                           cursor='hand2',
                           activebackground='#0056CC',
                           activeforeground='white')
        view_btn.pack(side='left', fill='x', expand=True, padx=(0, 8))
        
        # 收藏按钮 - iPhone风格
        is_fav = self.is_favorite(album['path']) if self.is_favorite else False
        fav_icon = "⭐" if is_fav else "☆"
        fav_color = "#FF9500" if is_fav else "#C7C7CC"
        
        fav_btn = tk.Button(button_frame, text=fav_icon,
                          command=lambda: self.favorite_callback(album['path']),
                          font=get_safe_font('Arial', 18),
                          bg='#F2F2F7', fg=fav_color,
                          relief='flat', bd=0,
                          width=3, pady=10,
                          cursor='hand2',
                          activebackground='#E5E5EA')
        fav_btn.pack(side='right')
        
        # 添加悬停效果
        self._add_hover_effects(card_frame, content_frame, info_frame)
    
    def _load_cover_image(self, parent, image_path, album_path):
        """加载封面图片"""
        try:
            # 创建缩略图
            thumbnail = ImageProcessor.create_thumbnail(image_path, size=(240, 160))
            if thumbnail:
                photo = ImageTk.PhotoImage(thumbnail)
                cover_label = tk.Label(parent, image=photo, bg='#F2F2F7',
                                     cursor='hand2')
                cover_label.image = photo  # 保持引用
                cover_label.pack(expand=True)
                
                # 点击封面打开相册
                cover_label.bind("<Button-1>", 
                               lambda e: self.open_callback(album_path))
            else:
                # 加载失败时显示默认图标
                default_label = tk.Label(parent, text="🖼️", 
                                       font=get_safe_font('Arial', 48),
                                       bg='#F2F2F7', fg='#C7C7CC')
                default_label.pack(expand=True)
        except Exception as e:
            print(f"加载封面图片失败: {e}")
            # 显示错误图标
            error_label = tk.Label(parent, text="❌", 
                                 font=get_safe_font('Arial', 48),
                                 bg='#F2F2F7', fg='#FF3B30')
            error_label.pack(expand=True)
    
    def _add_hover_effects(self, card_frame, content_frame, info_frame):
        """添加iPhone风格悬停效果"""
        def on_enter(event):
            card_frame.configure(bg='#F8F8F8')
            content_frame.configure(bg='#F8F8F8')
            info_frame.configure(bg='#F8F8F8')
            # 添加轻微的缩放效果模拟
            card_frame.configure(relief='raised', bd=1)
        
        def on_leave(event):
            card_frame.configure(bg='#FFFFFF')
            content_frame.configure(bg='#FFFFFF')
            info_frame.configure(bg='#FFFFFF')
            card_frame.configure(relief='flat', bd=0)
        
        # 绑定悬停事件到所有相关组件
        for widget in [card_frame, content_frame, info_frame]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            
            # 绑定子组件
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    child.bind('<Enter>', on_enter)
                    child.bind('<Leave>', on_leave)

class ImageViewer:
    """iPhone风格图片查看器"""
    
    def __init__(self, parent, image_files, config_manager):
        self.parent = parent
        self.image_files = image_files
        self.config_manager = config_manager
        self.current_index = 0
        self.zoom_level = 1.0
        self.is_fullscreen = False
        
        self.setup_window()
        self.create_widgets()
        self.bind_events()
        self.load_current_image()
    
    def setup_window(self):
        """设置iPhone风格窗口"""
        self.parent.configure(bg='#000000')
        
        # 设置窗口标题
        if self.image_files:
            filename = os.path.basename(self.image_files[0])
            folder_name = os.path.basename(os.path.dirname(self.image_files[0]))
            self.parent.title(f"📷 {folder_name} - {filename}")
    
    def create_widgets(self):
        """创建iPhone风格查看器组件"""
        # 顶部工具栏 - iPhone风格
        toolbar = tk.Frame(self.parent, bg='#F2F2F7', height=60)
        toolbar.pack(fill='x', side='top')
        toolbar.pack_propagate(False)
        
        # 工具栏内容
        toolbar_content = tk.Frame(toolbar, bg='#F2F2F7')
        toolbar_content.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 左侧导航按钮
        nav_frame = tk.Frame(toolbar_content, bg='#F2F2F7')
        nav_frame.pack(side='left')
        
        prev_btn = tk.Button(nav_frame, text="◀", command=self.prev_image,
                           font=get_safe_font('Arial', 16, 'bold'),
                           bg='#007AFF', fg='white', relief='flat', bd=0,
                           width=4, height=1, cursor='hand2')
        prev_btn.pack(side='left', padx=2)
        
        next_btn = tk.Button(nav_frame, text="▶", command=self.next_image,
                           font=get_safe_font('Arial', 16, 'bold'),
                           bg='#007AFF', fg='white', relief='flat', bd=0,
                           width=4, height=1, cursor='hand2')
        next_btn.pack(side='left', padx=2)
        
        # 中间信息显示
        self.info_var = tk.StringVar()
        info_label = tk.Label(toolbar_content, textvariable=self.info_var,
                            font=get_safe_font('Arial', 14, 'bold'),
                            bg='#F2F2F7', fg='#1D1D1F')
        info_label.pack(expand=True)
        
        # 右侧功能按钮
        tools_frame = tk.Frame(toolbar_content, bg='#F2F2F7')
        tools_frame.pack(side='right')
        
        fullscreen_btn = tk.Button(tools_frame, text="⛶", command=self.toggle_fullscreen,
                                 font=get_safe_font('Arial', 16, 'bold'),
                                 bg='#34C759', fg='white', relief='flat', bd=0,
                                 width=4, height=1, cursor='hand2')
        fullscreen_btn.pack(side='left', padx=2)
        
        # 图片显示区域
        self.image_container = tk.Frame(self.parent, bg='#000000')
        self.image_container.pack(fill='both', expand=True)
        
        # 图片标签
        self.image_label = tk.Label(self.image_container, bg='#000000')
        self.image_label.pack(expand=True)
        
        # 底部状态栏
        status_bar = tk.Frame(self.parent, bg='#F2F2F7', height=40)
        status_bar.pack(fill='x', side='bottom')
        status_bar.pack_propagate(False)
        
        # 状态信息
        self.status_var = tk.StringVar()
        status_label = tk.Label(status_bar, textvariable=self.status_var,
                              font=get_safe_font('Arial', 12),
                              bg='#F2F2F7', fg='#6D6D80')
        status_label.pack(side='left', padx=20, pady=10)
    
    def bind_events(self):
        """绑定键盘和鼠标事件"""
        self.parent.bind('<Left>', lambda e: self.prev_image())
        self.parent.bind('<Right>', lambda e: self.next_image())
        self.parent.bind('<Escape>', lambda e: self.exit_fullscreen() if self.is_fullscreen else self.parent.destroy())
        self.parent.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.parent.bind('<space>', lambda e: self.next_image())
        self.parent.focus_set()
        
        # 图片双击全屏
        self.image_label.bind('<Double-Button-1>', lambda e: self.toggle_fullscreen())
    
    def load_current_image(self):
        """加载当前图片"""
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        try:
            image_path = self.image_files[self.current_index]
            
            # 获取窗口尺寸
            window_width = self.image_container.winfo_width() or 800
            window_height = self.image_container.winfo_height() or 600
            
            # 加载图片
            result = ImageProcessor.load_image_with_mode(
                image_path, window_width, window_height, "fit", 0)
            
            if result and result[0]:
                photo, width, height, orig_width, orig_height = result
                self.image_label.configure(image=photo)
                self.image_label.image = photo  # 保持引用
                
                # 更新信息显示
                filename = os.path.basename(image_path)
                self.info_var.set(f"{self.current_index + 1} / {len(self.image_files)}")
                self.status_var.set(f"{filename} • {orig_width}×{orig_height}")
                
                # 更新窗口标题
                folder_name = os.path.basename(os.path.dirname(image_path))
                self.parent.title(f"📷 {folder_name} - {filename}")
            else:
                self.image_label.configure(image="", text="❌ 无法加载图片",
                                         font=get_safe_font('Arial', 16),
                                         fg='white')
                self.image_label.image = None
                
        except Exception as e:
            print(f"加载图片失败: {e}")
            self.image_label.configure(image="", text="❌ 加载失败",
                                     font=get_safe_font('Arial', 16),
                                     fg='white')
            self.image_label.image = None
    
    def prev_image(self):
        """上一张图片"""
        if self.image_files:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.load_current_image()
    
    def next_image(self):
        """下一张图片"""
        if self.image_files:
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.load_current_image()
    
    def toggle_fullscreen(self):
        """切换全屏模式"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.parent.attributes('-fullscreen', True)
            self.is_fullscreen = True
    
    def exit_fullscreen(self):
        """退出全屏"""
        self.parent.attributes('-fullscreen', False)
        self.is_fullscreen = False
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
