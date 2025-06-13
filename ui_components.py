import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from image_utils import ImageProcessor

class StyleManager:
    """样式管理器，负责应用程序的外观样式"""
    
    def __init__(self, root, style):
        self.root = root
        self.style = style
        self.setup_colors()
        self.setup_styles()
    
    def setup_colors(self):
        """设置颜色方案"""
        self.bg_color = '#f8f9fa'
        self.accent_color = '#3f51b5'
        self.text_color = '#2d3436'
        self.card_bg = '#ffffff'
        self.border_color = '#e9ecef'
        self.hover_color = '#e8f0fe'
    
    def setup_styles(self):
        """设置样式"""
        self.root.configure(bg=self.bg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        
        # 自定义按钮样式
        self.style.element_create("Custom.Button.button", "from", "default")
        self.style.layout("Custom.TButton",
                         [('Custom.Button.button', {'children': [
                             ('Button.focus', {'children': [
                                 ('Button.padding', {'children': [
                                     ('Button.label', {'sticky': 'nswe'})
                                 ], 'sticky': 'nswe'})
                             ], 'sticky': 'nswe'})
                         ], 'sticky': 'nswe'})])
        
        self.style.configure("Custom.TButton",
                            background=self.accent_color,
                            foreground='white',
                            borderwidth=0,
                            focuscolor='none',
                            padding=(10, 8),
                            font=('Microsoft YaHei', 10))
        
        self.style.map("Custom.TButton",
                      background=[('active', '#303f9f'), ('pressed', '#283593')],
                      foreground=[('active', 'white'), ('pressed', 'white'), ('!disabled', 'white')],
                      relief=[('pressed', 'flat'), ('!pressed', 'flat')])

        # 卡片样式
        self.style.configure('Card.TFrame',
                            background=self.card_bg,
                            relief='flat',
                            borderwidth=1,
                            bordercolor=self.border_color)
        self.style.configure('CardHover.TFrame',
                            background=self.card_bg,
                            relief='flat',
                            borderwidth=1,
                            bordercolor=self.accent_color)

        # 输入框样式
        self.style.configure('TEntry',
                            padding=8,
                            relief='flat',
                            fieldbackground=self.card_bg,
                            bordercolor=self.border_color,
                            font=('Microsoft YaHei', 10))
        self.style.map('TEntry',
                      bordercolor=[('focus', self.accent_color)])
        self.style.configure('TRadiobutton', background=self.bg_color, foreground=self.text_color)

class NavigationBar:
    """导航栏组件"""
    
    def __init__(self, parent, on_browse, on_scan, path_var):
        self.parent = parent
        self.on_browse = on_browse
        self.on_scan = on_scan
        self.path_var = path_var
        self.create_widgets()
    
    def create_widgets(self):
        # 顶部导航栏
        self.nav_frame = ttk.Frame(self.parent, padding="15 10 15 10")
        self.nav_frame.pack(fill=tk.X)

        # 标题
        title_label = ttk.Label(self.nav_frame, text="相册扫描器", 
                               font=('Microsoft YaHei', 16, 'bold'))
        title_label.pack(side=tk.LEFT, padx=10)

        # 路径选择区域
        path_frame = ttk.Frame(self.nav_frame)
        path_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)

        ttk.Label(path_frame, text="相册路径:", 
                 font=('Microsoft YaHei', 10)).pack(side=tk.LEFT, padx=5)

        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50, 
                              font=('Microsoft YaHei', 10))
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        browse_btn = ttk.Button(path_frame, text="浏览", command=self.on_browse, 
                               width=8, style="Custom.TButton")
        browse_btn.pack(side=tk.LEFT, padx=5)

        scan_btn = ttk.Button(path_frame, text="扫描相册", command=self.on_scan, 
                             width=10, style="Custom.TButton")
        scan_btn.pack(side=tk.LEFT, padx=5)

class AlbumGrid:
    """相册网格显示组件"""
    
    def __init__(self, parent, on_album_click):
        self.parent = parent
        self.on_album_click = on_album_click
        self.max_cols = 4
        self.create_widgets()
    
    def create_widgets(self):
        # 相册显示区域
        self.album_frame = ttk.Frame(self.parent, padding="10")
        self.album_frame.pack(fill=tk.BOTH, expand=True)
        self.album_frame.rowconfigure(0, weight=1)
        self.album_frame.columnconfigure(0, weight=1)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(self.album_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建画布
        self.canvas = tk.Canvas(self.album_frame, yscrollcommand=scrollbar.set, 
                               highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        # 创建内部框架
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        # 绑定事件
        self.inner_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
    
    def on_canvas_configure(self, event):
        """画布大小变化时调整"""
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    def on_frame_configure(self, event):
        """更新画布滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def clear_albums(self):
        """清空相册显示"""
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
    
    def display_albums(self, albums):
        """显示相册列表"""
        self.clear_albums()
        
        row = 0
        col = 0
        
        for album in albums:
            self.create_album_card(album, row, col)
            
            col += 1
            if col >= self.max_cols:
                col = 0
                row += 1
    
    def create_album_card(self, album, row, col):
        """创建相册卡片"""
        album_frame = ttk.Frame(self.inner_frame, padding="15", 
                               relief=tk.FLAT, style='Card.TFrame')
        album_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # 绑定悬停效果
        album_frame.bind('<Enter>', lambda e, f=album_frame: self.on_enter(e, f))
        album_frame.bind('<Leave>', lambda e, f=album_frame: self.on_leave(e, f))

        # 创建封面
        if album['cover_image']:
            photo = ImageProcessor.create_thumbnail(album['cover_image'])
            if photo:
                cover_label = ttk.Label(album_frame, image=photo)
                cover_label.image = photo
                cover_label.bind("<Button-1>", 
                               lambda e, path=album['path']: self.on_album_click(path))
                cover_label.pack(pady=5)

        # 文件夹名称
        name_label = ttk.Label(album_frame, text=album['name'], wraplength=200, 
                              font=('Microsoft YaHei', 10, 'bold'))
        name_label.pack(pady=10)

        # 图片数量
        count_label = ttk.Label(album_frame, text=f"{len(album['image_files'])}张图片", 
                               font=('Microsoft YaHei', 9), foreground='#666666')
        count_label.pack(pady=2)
    
    def on_enter(self, event, frame):
        """鼠标悬停效果"""
        frame.configure(style='CardHover.TFrame')

    def on_leave(self, event, frame):
        """鼠标离开效果"""
        frame.configure(style='Card.TFrame')

class ImageViewer:
    """图片查看器组件"""
    
    def __init__(self, parent, image_files):
        self.parent = parent
        self.image_files = image_files
        self.current_index = 0
        self.zoom_mode = tk.StringVar(value="fit")
        self.status_var = tk.StringVar()
        
        self.create_widgets()
        self.bind_events()
        self.load_image()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 导航按钮
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(nav_frame, text="上一张", command=self.prev_image, 
                  style="Custom.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="下一张", command=self.next_image, 
                  style="Custom.TButton").pack(side=tk.LEFT, padx=10)
        
        ttk.Label(nav_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=10)

        # 图片显示区域
        self.image_frame = ttk.Frame(main_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_container = ttk.Frame(self.image_frame, padding=15, style='Card.TFrame')
        self.image_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.image_label = ttk.Label(self.image_container)
        self.image_label.pack(expand=True)

        # 图片信息
        self.image_info = ttk.Label(self.image_frame, text='', font=('Microsoft YaHei', 10))
        self.image_info.pack(pady=5)
        
        # 缩放模式
        zoom_frame = ttk.Frame(self.parent)
        zoom_frame.pack(fill=tk.X, pady=2)
        ttk.Label(zoom_frame, text="缩放模式:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(zoom_frame, text="适应窗口", variable=self.zoom_mode, 
                       value="fit", command=self.load_image).pack(side=tk.LEFT)
        ttk.Radiobutton(zoom_frame, text="原始大小", variable=self.zoom_mode, 
                       value="original", command=self.load_image).pack(side=tk.LEFT)
        ttk.Radiobutton(zoom_frame, text="填充", variable=self.zoom_mode, 
                       value="fill", command=self.load_image).pack(side=tk.LEFT)
    
    def bind_events(self):
        """绑定键盘事件"""
        self.parent.bind("<Left>", lambda e: self.prev_image())
        self.parent.bind("<Right>", lambda e: self.next_image())
        self.parent.bind("<Escape>", lambda e: self.parent.destroy())
        self.parent.bind("f", lambda e: self.set_zoom_mode("fit"))
        self.parent.bind("o", lambda e: self.set_zoom_mode("original"))
        self.parent.bind("l", lambda e: self.set_zoom_mode("fill"))
        self.parent.focus_set()  # 确保窗口能接收键盘事件
    
    def set_zoom_mode(self, mode):
        """设置缩放模式"""
        self.zoom_mode.set(mode)
        self.load_image()

    def load_image(self):
        """加载当前图片"""
        if not (0 <= self.current_index < len(self.image_files)):
            return
            
        image_path = self.image_files[self.current_index]
        window_width = self.image_frame.winfo_width()
        window_height = self.image_frame.winfo_height()
        
        if window_width < 10: 
            window_width = 800
        if window_height < 10: 
            window_height = 500
        
        photo, width, height = ImageProcessor.load_image_with_mode(
            image_path, window_width, window_height, self.zoom_mode.get())
        
        if photo:
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo
            self.status_var.set(f"{self.current_index + 1}/{len(self.image_files)}")
            self.image_info.config(text=f"{os.path.basename(image_path)} ({width}×{height})")
        else:
            self.image_label.config(text="无法加载图片", image="")
            self.image_label.image = None

    def prev_image(self):
        """上一张图片"""
        self.current_index = (self.current_index - 1) % len(self.image_files)
        self.load_image()
        
    def next_image(self):
        """下一张图片"""
        self.current_index = (self.current_index + 1) % len(self.image_files)
        self.load_image()
