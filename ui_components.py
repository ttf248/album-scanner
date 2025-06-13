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
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建导航栏组件"""
        # 主容器
        self.main_container = tk.Frame(self.parent, bg='#F2F2F7')
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 创建启动页
        self.create_hero_section()
        self.create_quick_actions()
        self.create_path_input()
    
    def create_hero_section(self):
        """创建英雄区域"""
        hero_frame = tk.Frame(self.main_container, bg='#F2F2F7')
        hero_frame.pack(fill='x', pady=(0, 30))
        
        # 应用图标（使用Emoji）
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
    
    def create_quick_actions(self):
        """创建快速操作卡片"""
        actions_frame = tk.Frame(self.main_container, bg='#F2F2F7')
        actions_frame.pack(fill='x', pady=(0, 30))
        
        # 标题
        title = tk.Label(actions_frame, text="快速操作", 
                        font=get_safe_font('Arial', 20, 'bold'), 
                        bg='#F2F2F7', fg='#1D1D1F')
        title.pack(anchor='w', pady=(0, 20))
        
        # 网格容器 - 调整配置
        grid_frame = tk.Frame(actions_frame, bg='#F2F2F7')
        grid_frame.pack(fill='x')
        
        # 配置网格权重 - 让网格更均匀
        for i in range(2):
            grid_frame.grid_columnconfigure(i, weight=1, minsize=200)
        for i in range(2):
            grid_frame.grid_rowconfigure(i, weight=1, minsize=180)
        
        # 快速操作数据
        actions = [
            ("📚", "最近浏览", "查看最近打开的相册", self.recent_callback, "#007AFF"),
            ("⭐", "收藏夹", "管理您收藏的相册", self.favorites_callback, "#FF9500"),
            ("🔍", "智能扫描", "自动发现图片文件夹", self.scan_callback, "#34C759"),
            ("⚙️", "设置", "个性化您的体验", lambda: self._show_settings(), "#6D6D80")
        ]
        
        # 创建操作卡片
        for i, (icon, title, desc, command, color) in enumerate(actions):
            row, col = divmod(i, 2)
            self.create_action_card(grid_frame, icon, title, desc, command, color, row, col)
    
    def create_action_card(self, parent, icon, title, desc, command, color, row, col):
        """创建操作卡片"""
        # 卡片主框架 - 调整尺寸
        card_frame = tk.Frame(parent, bg=color, relief='flat', bd=0,
                             width=180, height=160)  # 设置固定尺寸
        card_frame.grid(row=row, column=col, padx=12, pady=12, sticky='nsew')
        card_frame.grid_propagate(False)  # 防止内容改变大小
        
        # 内容框架
        content_frame = tk.Frame(card_frame, bg=color)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')  # 居中放置
        
        # 图标 - 调整大小
        icon_label = tk.Label(content_frame, text=icon, 
                             font=get_safe_font('Arial', 32), bg=color, fg='white')
        icon_label.pack(pady=(0, 10))
        
        # 标题 - 调整字体大小
        title_label = tk.Label(content_frame, text=title,
                              font=get_safe_font('Arial', 14, 'bold'), 
                              bg=color, fg='white')
        title_label.pack(pady=(0, 6))
        
        # 描述 - 调整字体和换行
        desc_label = tk.Label(content_frame, text=desc,
                             font=get_safe_font('Arial', 10), 
                             bg=color, fg='#E5E5E7', 
                             wraplength=140, justify='center')
        desc_label.pack(pady=(0, 15))
        
        # 按钮 - 调整样式
        action_btn = tk.Button(content_frame, text="使用",
                              font=get_safe_font('Arial', 11, 'bold'), 
                              bg='white', fg=color,
                              relief='flat', bd=0, padx=18, pady=6,
                              cursor='hand2', command=command,
                              activebackground='#f0f0f0', activeforeground=color)
        action_btn.pack()
        
        # 悬停效果
        def on_enter(e):
            card_frame.configure(relief='raised', bd=1)
            card_frame.configure(bg=self._lighten_color(color))
            content_frame.configure(bg=self._lighten_color(color))
            for child in content_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg=self._lighten_color(color))
        
        def on_leave(e):
            card_frame.configure(relief='flat', bd=0)
            card_frame.configure(bg=color)
            content_frame.configure(bg=color)
            for child in content_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg=color)
        
        card_frame.bind('<Enter>', on_enter)
        card_frame.bind('<Leave>', on_leave)
        content_frame.bind('<Enter>', on_enter)
        content_frame.bind('<Leave>', on_leave)
        
        # 为所有子组件绑定悬停事件
        for child in content_frame.winfo_children():
            child.bind('<Enter>', on_enter)
            child.bind('<Leave>', on_leave)
    
    def _lighten_color(self, color):
        """让颜色变亮一点"""
        color_map = {
            "#007AFF": "#1A8AFF",
            "#FF9500": "#FFA520", 
            "#34C759": "#4DD169",
            "#6D6D80": "#8D8D90"
        }
        return color_map.get(color, color)

    def create_quick_actions(self):
        """创建快速操作卡片"""
        actions_frame = tk.Frame(self.main_container, bg='#F2F2F7')
        actions_frame.pack(fill='x', pady=(0, 30))
        
        # 标题
        title = tk.Label(actions_frame, text="快速操作", 
                        font=get_safe_font('Arial', 20, 'bold'), 
                        bg='#F2F2F7', fg='#1D1D1F')
        title.pack(anchor='w', pady=(0, 20))
        
        # 网格容器 - 调整配置
        grid_frame = tk.Frame(actions_frame, bg='#F2F2F7')
        grid_frame.pack(fill='x')
        
        # 配置网格权重 - 让网格更均匀
        for i in range(2):
            grid_frame.grid_columnconfigure(i, weight=1, minsize=200)
        for i in range(2):
            grid_frame.grid_rowconfigure(i, weight=1, minsize=180)
        
        # 快速操作数据
        actions = [
            ("📚", "最近浏览", "查看最近打开的相册", self.recent_callback, "#007AFF"),
            ("⭐", "收藏夹", "管理您收藏的相册", self.favorites_callback, "#FF9500"),
            ("🔍", "智能扫描", "自动发现图片文件夹", self.scan_callback, "#34C759"),
            ("⚙️", "设置", "个性化您的体验", lambda: self._show_settings(), "#6D6D80")
        ]
        
        # 创建操作卡片
        for i, (icon, title, desc, command, color) in enumerate(actions):
            row, col = divmod(i, 2)
            self.create_action_card(grid_frame, icon, title, desc, command, color, row, col)
    
    def _show_settings(self):
        """显示设置对话框"""
        messagebox.showinfo("设置", "设置功能即将推出，敬请期待！")

    def create_path_input(self):
        """创建路径输入区域"""
        path_frame = tk.Frame(self.main_container, bg='#FFFFFF', relief='flat', bd=0)
        path_frame.pack(fill='x', pady=(0, 20))
        
        # 添加圆角效果的模拟
        path_frame.configure(highlightbackground='#E5E5EA', highlightthickness=1)
        
        # 内容框架
        content_frame = tk.Frame(path_frame, bg='#FFFFFF')
        content_frame.pack(fill='x', padx=25, pady=25)
        
        # 标题
        title = tk.Label(content_frame, text="选择相册文件夹", 
                        font=get_safe_font('Arial', 18, 'bold'), 
                        bg='#FFFFFF', fg='#1D1D1F')
        title.pack(anchor='w', pady=(0, 18))
        
        # 路径输入框
        input_frame = tk.Frame(content_frame, bg='#FFFFFF')
        input_frame.pack(fill='x', pady=(0, 18))
        
        self.path_entry = tk.Entry(input_frame, textvariable=self.path_var,
                                  font=get_safe_font('Arial', 14), 
                                  bg='#F2F2F7', fg='#1D1D1F',
                                  relief='flat', bd=0, highlightthickness=0)
        self.path_entry.pack(side='left', fill='x', expand=True, ipady=12, padx=(0, 15))
        
        # 按钮框架
        button_frame = tk.Frame(content_frame, bg='#FFFFFF')
        button_frame.pack(fill='x')
        
        # 浏览按钮 - 调整样式
        browse_btn = tk.Button(button_frame, text="📁 选择文件夹",
                              font=get_safe_font('Arial', 14, 'bold'), 
                              bg='#007AFF', fg='white',
                              relief='flat', bd=0, padx=25, pady=12,
                              cursor='hand2', command=self.browse_callback,
                              activebackground='#0056CC', activeforeground='white')
        browse_btn.pack(side='left', padx=(0, 15))
        
        # 扫描按钮 - 调整样式
        scan_btn = tk.Button(button_frame, text="🔍 开始扫描",
                            font=get_safe_font('Arial', 14, 'bold'), 
                            bg='#34C759', fg='white',
                            relief='flat', bd=0, padx=25, pady=12,
                            cursor='hand2', command=self.scan_callback,
                            activebackground='#28A745', activeforeground='white')
        scan_btn.pack(side='left')

class AlbumGrid:
    """瀑布流相册网格"""
    
    def __init__(self, parent, open_callback, favorite_callback):
        self.parent = parent
        self.open_callback = open_callback
        self.favorite_callback = favorite_callback
        self.is_favorite = None  # 由外部设置
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建网格组件"""
        # 这里创建一个简单的网格容器，避免复杂的字体配置
        self.grid_frame = tk.Frame(self.parent, bg='#F2F2F7')
        self.grid_frame.pack(fill='both', expand=True)
        
    def display_albums(self, albums):
        """显示相册（简化版本）"""
        # 清除现有内容
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        if not albums:
            # 显示空状态
            empty_label = tk.Label(self.grid_frame, text="暂无相册", 
                                  font=get_safe_font('Arial', 16), 
                                  bg='#F2F2F7', fg='#6D6D80')
            empty_label.pack(expand=True)
            return
        
        # 创建简单的列表显示
        for i, album in enumerate(albums):
            album_frame = tk.Frame(self.grid_frame, bg='white', relief='solid', bd=1)
            album_frame.pack(fill='x', padx=10, pady=5)
            
            # 相册信息
            info_frame = tk.Frame(album_frame, bg='white')
            info_frame.pack(fill='x', padx=10, pady=10)
            
            # 名称
            name_label = tk.Label(info_frame, text=album['name'], 
                                 font=get_safe_font('Arial', 14, 'bold'), 
                                 bg='white', fg='black')
            name_label.pack(anchor='w')
            
            # 统计信息
            stats_text = f"{album['image_count']} 张图片"
            stats_label = tk.Label(info_frame, text=stats_text, 
                                  font=get_safe_font('Arial', 12), 
                                  bg='white', fg='gray')
            stats_label.pack(anchor='w')
            
            # 按钮框架
            btn_frame = tk.Frame(info_frame, bg='white')
            btn_frame.pack(anchor='w', pady=(5, 0))
            
            # 打开按钮
            open_btn = tk.Button(btn_frame, text="打开", 
                               font=get_safe_font('Arial', 10), 
                               command=lambda path=album['path']: self.open_callback(path))
            open_btn.pack(side='left', padx=(0, 5))
            
            # 收藏按钮
            is_fav = self.is_favorite(album['path']) if self.is_favorite else False
            fav_text = "⭐" if is_fav else "☆"
            fav_btn = tk.Button(btn_frame, text=fav_text, 
                              font=get_safe_font('Arial', 10), 
                              command=lambda path=album['path']: self.favorite_callback(path))
            fav_btn.pack(side='left')

class ImageViewer:
    """图片查看器"""
    
    def __init__(self, parent, image_files, config_manager):
        self.parent = parent
        self.image_files = image_files
        self.config_manager = config_manager
        self.current_index = 0
        
        self.create_widgets()
        self.load_current_image()
    
    def create_widgets(self):
        """创建查看器组件"""
        # 创建简单的图片查看器
        self.main_frame = tk.Frame(self.parent, bg='black')
        self.main_frame.pack(fill='both', expand=True)
        
        # 图片显示区域
        self.image_label = tk.Label(self.main_frame, bg='black')
        self.image_label.pack(fill='both', expand=True)
        
        # 控制栏
        control_frame = tk.Frame(self.parent, bg='white', height=50)
        control_frame.pack(side='bottom', fill='x')
        control_frame.pack_propagate(False)
        
        # 导航按钮
        prev_btn = tk.Button(control_frame, text="上一张", 
                           font=get_safe_font('Arial', 12), 
                           command=self.prev_image)
        prev_btn.pack(side='left', padx=10, pady=10)
        
        next_btn = tk.Button(control_frame, text="下一张", 
                           font=get_safe_font('Arial', 12), 
                           command=self.next_image)
        next_btn.pack(side='left', padx=5, pady=10)
        
        # 图片信息
        self.info_var = tk.StringVar()
        info_label = tk.Label(control_frame, textvariable=self.info_var, 
                             font=get_safe_font('Arial', 12), 
                             bg='white')
        info_label.pack(side='right', padx=10, pady=10)
        
        # 键盘绑定
        self.parent.bind('<Key>', self.on_key_press)
        self.parent.focus_set()
    
    def load_current_image(self):
        """加载当前图片"""
        if not self.image_files:
            return
        
        try:
            image_path = self.image_files[self.current_index]
            image = Image.open(image_path)
            
            # 调整图片大小适应窗口
            window_width = self.main_frame.winfo_width() or 800
            window_height = self.main_frame.winfo_height() or 600
            
            image.thumbnail((window_width, window_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # 保持引用
            
            # 更新信息
            filename = os.path.basename(image_path)
            info_text = f"{self.current_index + 1}/{len(self.image_files)} - {filename}"
            self.info_var.set(info_text)
            
        except Exception as e:
            print(f"加载图片失败: {e}")
    
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
    
    def on_key_press(self, event):
        """键盘事件处理"""
        if event.keysym == 'Left':
            self.prev_image()
        elif event.keysym == 'Right':
            self.next_image()
        elif event.keysym == 'Escape':
            self.parent.destroy()
    def display_albums(self, albums):
        """显示相册瀑布流"""
        self.clear_albums()
        
        if not albums:
            self._show_empty_state()
            return
        
        # 创建列框架
        self._create_columns()
        
        # 瀑布流布局
        for i, album in enumerate(albums):
            col = i % self.cols
            self.create_album_card(album, self.column_frames[col])
    
    def _create_columns(self):
        """创建瀑布流列"""
        container = tk.Frame(self.scrollable_frame, bg='#f2f2f7')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.column_frames = []
        for i in range(self.cols):
            col_frame = tk.Frame(container, bg='#f2f2f7')
            col_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8)
            self.column_frames.append(col_frame)
    
    def _show_empty_state(self):
        """显示空状态"""
        empty_frame = tk.Frame(self.scrollable_frame, bg='#f2f2f7')
        empty_frame.pack(fill=tk.BOTH, expand=True, pady=100)
        
        # 空状态图标
        empty_icon = tk.Label(empty_frame, text="📷", font=('SF Pro Display', 64), 
                            bg='#f2f2f7', fg='#c7c7cc')
        empty_icon.pack(pady=(0, 20))
        
        # 空状态标题
        empty_title = tk.Label(empty_frame, text="暂无相册",
                             font=('SF Pro Display', 24, 'bold'),
                             bg='#f2f2f7', fg='#8e8e93')
        empty_title.pack(pady=(0, 8))
        
        # 空状态描述
        empty_desc = tk.Label(empty_frame, text="选择文件夹并点击扫描来发现您的相册",
                            font=('SF Pro Display', 17),
                            bg='#f2f2f7', fg='#aeaeb2')
        empty_desc.pack()
    
    def create_album_card(self, album, parent_column):
        """创建iPhone风格相册卡片"""
        # 计算卡片高度（模拟瀑布流效果）
        base_height = 280
        random_height = hash(album['name']) % 100
        card_height = base_height + random_height
        
        # 卡片容器
        card_frame = tk.Frame(parent_column, bg='#ffffff', relief='flat', bd=0,
                            height=card_height)
        card_frame.pack(fill=tk.X, pady=12)
        card_frame.pack_propagate(False)
        
        # 卡片内容
        content_frame = tk.Frame(card_frame, bg='#ffffff')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # 封面图片
        if album['cover_image']:
            photo = ImageProcessor.create_thumbnail(album['cover_image'], size=(240, 180))
            if photo:
                cover_label = tk.Label(content_frame, image=photo, bg='#ffffff',
                                     cursor='hand2')
                cover_label.image = photo
                cover_label.pack(pady=(0, 12))
                cover_label.bind("<Button-1>", 
                               lambda e, path=album['path']: self.on_album_click(path))
        
        # 相册信息
        info_frame = tk.Frame(content_frame, bg='#ffffff')
        info_frame.pack(fill=tk.X)
        
        # 相册名称
        name_label = tk.Label(info_frame, text=album['name'],
                            font=('SF Pro Display', 17, 'medium'),
                            bg='#ffffff', fg='#000000')
        name_label.pack(anchor=tk.W, pady=(0, 4))
        
        # 统计信息
        stats_text = f"{album.get('image_count', len(album['image_files']))} 张照片"
        if 'folder_size' in album:
            stats_text += f" • {album['folder_size']}"
        
        stats_label = tk.Label(info_frame, text=stats_text,
                             font=('SF Pro Display', 13),
                             bg='#ffffff', fg='#8e8e93')
        stats_label.pack(anchor=tk.W, pady=(0, 12))
        
        # 操作按钮
        button_frame = tk.Frame(info_frame, bg='#ffffff')
        button_frame.pack(fill=tk.X)
        
        # 查看按钮
        view_btn = tk.Button(button_frame, text="打开",
                           command=lambda: self.on_album_click(album['path']),
                           font=('SF Pro Display', 15, 'medium'),
                           bg='#007aff', fg='white',
                           relief='flat', bd=0,
                           padx=20, pady=8,
                           cursor='hand2')
        view_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        # 收藏按钮
        fav_icon = "⭐" if self.is_favorite(album['path']) else "☆"
        fav_btn = tk.Button(button_frame, text=fav_icon,
                          command=lambda: self.on_favorite_toggle(album['path']),
                          font=('SF Pro Display', 18),
                          bg='#f2f2f7', fg='#ff9500',
                          relief='flat', bd=0,
                          width=3, pady=8,
                          cursor='hand2')
        fav_btn.pack(side=tk.RIGHT)
        
        # 添加悬停效果
        def on_enter(event):
            card_frame.configure(bg='#f8f8f8')
            content_frame.configure(bg='#f8f8f8')
        
        def on_leave(event):
            card_frame.configure(bg='#ffffff')
            content_frame.configure(bg='#ffffff')
        
        card_frame.bind('<Enter>', on_enter)
        card_frame.bind('<Leave>', on_leave)
        content_frame.bind('<Enter>', on_enter)
        content_frame.bind('<Leave>', on_leave)
    
    def is_favorite(self, album_path):
        """检查是否为收藏"""
        return False  # 默认实现

class ImageViewer:
    """iPhone风格图片查看器"""
    
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
        """设置iPhone风格窗口"""
        self.parent.configure(bg='#000000')
    
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
