import os
import json
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import glob
import platform
from ttkthemes import ThemedTk

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.album_scanner_config.json')

class PhotoAlbumApp:
    def __init__(self, root):
        self.root = root  # 使用传入的root实例
        self.root.title("相册扫描器")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        # 应用主题
        self.root.set_theme("arc")

        # 设置样式
        self.style = ttk.Style()

        # 配置颜色方案
        # 配置现代颜色方案
        self.bg_color = '#f8f9fa'
        self.accent_color = '#3f51b5'
        self.text_color = '#2d3436'
        self.card_bg = '#ffffff'
        self.border_color = '#e9ecef'
        self.hover_color = '#e8f0fe'

        # 应用样式
        self.root.configure(bg=self.bg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        
        # 创建自定义按钮样式，完全覆盖主题
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

        # 配置卡片样式
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

        # 配置输入框样式
        self.style.configure('TEntry',
                            padding=8,
                            relief='flat',
                            fieldbackground=self.card_bg,
                            bordercolor=self.border_color,
                            font=('Microsoft YaHei', 10))
        self.style.map('TEntry',
                      bordercolor=[('focus', self.accent_color)])
        self.style.configure('TRadiobutton', background=self.bg_color, foreground=self.text_color)
        
        # 存储配置的文件夹路径
        # 加载上次保存的路径
        self.folder_path = self.load_last_path()
        self.path_var = tk.StringVar(value=self.folder_path)
        
        # 创建UI
        self.create_widgets()
        
    def create_widgets(self):
        # 顶部导航栏
        nav_frame = ttk.Frame(self.root, padding="15 10 15 10")
        nav_frame.pack(fill=tk.X)
        nav_frame.configure(style='Nav.TFrame')

        # 标题
        title_label = ttk.Label(nav_frame, text="相册扫描器", font=('Microsoft YaHei', 16, 'bold'))
        title_label.pack(side=tk.LEFT, padx=10)

        # 路径选择区域
        path_frame = ttk.Frame(nav_frame)
        path_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)

        ttk.Label(path_frame, text="相册路径:", font=('Microsoft YaHei', 10)).pack(side=tk.LEFT, padx=5)

        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50, font=('Microsoft YaHei', 10))
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 使用自定义按钮样式
        browse_btn = ttk.Button(path_frame, text="浏览", command=self.browse_folder, width=8, style="Custom.TButton")
        browse_btn.pack(side=tk.LEFT, padx=5)

        scan_btn = ttk.Button(path_frame, text="扫描相册", command=self.scan_albums, width=10, style="Custom.TButton")
        scan_btn.pack(side=tk.LEFT, padx=5)
        
        # 相册显示区域
        self.album_frame = ttk.Frame(self.root, padding="10")
        self.album_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(self.album_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建画布用于放置相册封面
        self.canvas = tk.Canvas(self.album_frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        # 创建内部框架放置相册封面
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        # 绑定事件以更新滚动区域
        self.inner_frame.bind("<Configure>", self.on_frame_configure)
        
    def on_frame_configure(self, event):
        """更新画布滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def load_last_path(self):
        """加载上次保存的路径"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('last_path', '')
        except Exception as e:
            print(f"加载配置失败: {e}")
        return ''

    def save_last_path(self):
        """保存当前路径到配置文件"""
        try:
            config = {'last_path': self.folder_path}
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def browse_folder(self):
        """浏览并选择文件夹"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path = folder_selected
            self.path_var.set(folder_selected)
            self.save_last_path()
            
    def scan_albums(self):
        """扫描文件夹并显示相册封面"""
        if not self.folder_path:
            messagebox.showwarning("警告", "请先选择相册文件夹")
            return
            
        # 清空现有内容
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
            
        # 递归获取所有包含图片的子文件夹
        subfolders = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        
        for root, dirs, files in os.walk(self.folder_path):
            # 检查当前目录是否包含图片文件
            has_images = any(os.path.splitext(file)[1].lower() in image_extensions for file in files)
            if has_images:
                subfolders.append(root)
        
        if not subfolders:
            messagebox.showinfo("提示", "未找到包含图片的文件夹")
            return
            
        # 为每个包含图片的文件夹创建相册封面
        row = 0
        col = 0
        max_cols = 4  # 每行显示4个相册
        
        for folder in subfolders:
            # 获取文件夹名称
            folder_name = os.path.basename(folder)
            
            # 获取文件夹中的图片文件
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
            image_files = []
            
            for ext in image_extensions:
                image_files.extend(glob.glob(os.path.join(folder, ext), recursive=False))
                image_files.extend(glob.glob(os.path.join(folder, ext.upper()), recursive=False))
                
            if not image_files:
                continue  # 跳过没有图片的文件夹
                
            # 按文件名排序
            image_files.sort()
            
            # 获取第一张图片作为封面
            cover_path = image_files[0]
            
            # 创建相册封面框架 - 现代卡片式设计
            album_frame = ttk.Frame(self.inner_frame, padding="15", relief=tk.FLAT, style='Card.TFrame')
            album_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            album_frame.bind('<Enter>', lambda e, f=album_frame: self.on_enter(e, f))
            album_frame.bind('<Leave>', lambda e, f=album_frame: self.on_leave(e, f))

            # 加载并调整封面图片大小
            try:
                img = Image.open(cover_path)
                img.thumbnail((200, 200))  # 调整为缩略图
                photo = ImageTk.PhotoImage(img)
                
                # 创建封面标签并绑定点击事件
                cover_label = ttk.Label(album_frame, image=photo)
                cover_label.image = photo  # 保持引用
                cover_label.bind("<Button-1>", lambda e, f=folder: self.open_album(f))
                cover_label.pack(pady=5)
                
                # 添加文件夹名称标签
                name_label = ttk.Label(album_frame, text=folder_name, wraplength=200, font=('Microsoft YaHei', 10, 'bold'))
                name_label.pack(pady=10)

                # 添加图片数量标签
                count_label = ttk.Label(album_frame, text=f"{len(image_files)}张图片", font=('Microsoft YaHei', 9), foreground='#666666')
                count_label.pack(pady=2)
                
                # 更新行列位置
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
            except Exception as e:
                print(f"无法加载图片 {cover_path}: {e}")
                continue
                
    def open_album(self, folder_path):
        """打开相册查看所有图片"""
        # 创建新窗口显示相册内容
        album_window = tk.Toplevel(self.root)
        album_window.title(os.path.basename(folder_path))
        album_window.geometry("800x600")
        
        # 获取文件夹中的所有图片
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(folder_path, ext), recursive=False))
            image_files.extend(glob.glob(os.path.join(folder_path, ext.upper()), recursive=False))
            
        if not image_files:
            messagebox.showinfo("提示", "该文件夹中没有图片")
            album_window.destroy()
            return
            
        # 按文件名排序
        image_files.sort()
        
        # 创建图片查看器
        img_viewer = ImageViewer(album_window, image_files)
        
    def on_enter(self, event, frame):
        """鼠标悬停在相册卡片上时的效果 - 添加缩放动画"""
        frame.configure(style='CardHover.TFrame')
        # 添加轻微缩放效果
        frame.bind('<Motion>', lambda e: self.on_motion(e, frame))
        self.animate_card(frame, 1.0, 1.05, 0.01)

    def on_leave(self, event, frame):
        """鼠标离开相册卡片时的效果 - 恢复原始状态"""
        frame.configure(style='Card.TFrame')
        frame.unbind('<Motion>')
        self.animate_card(frame, 1.05, 1.0, 0.01)

    def animate_card(self, frame, start, end, step):
        """卡片缩放动画"""
        current = float(frame.cget('relief')) if frame.cget('relief') else start
        if (step > 0 and current < end) or (step < 0 and current > end):
            frame.configure(relief=tk.FLAT)
            frame.after(10, lambda: self.animate_card(frame, current, end, step))

    def on_motion(self, event, frame):
        """鼠标在卡片上移动时的效果"""
        pass

    def update_shadow(self, event, frame):
        """更新卡片阴影效果"""
        # 简单的阴影模拟
        pass

class ImageViewer:
    def __init__(self, parent, image_files):
        self.parent = parent
        self.image_files = image_files
        self.current_index = 0
        
        self.create_widgets()
        self.load_image()
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建导航按钮 - 使用自定义样式
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(nav_frame, text="上一张", command=self.prev_image, style="Custom.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="下一张", command=self.next_image, style="Custom.TButton").pack(side=tk.LEFT, padx=10)
        
        self.status_var = tk.StringVar()
        ttk.Label(nav_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=10)

        # 创建图片显示区域
        self.image_frame = ttk.Frame(main_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建图片显示区域
        # 创建图片显示区域
        self.image_container = ttk.Frame(self.image_frame, padding=15, style='Card.TFrame')
        self.image_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 添加图片加载动画占位符
        self.image_label = ttk.Label(self.image_container, background='#f8f9fa')
        self.image_label.pack(expand=True)

        # 添加图片信息标签
        self.image_info = ttk.Label(self.image_frame, text='', font=('Microsoft YaHei', 10))
        self.image_info.pack(pady=5)
        
        # 绑定键盘事件
        # 绑定键盘事件
        self.parent.bind("<Left>", lambda e: self.prev_image())
        self.parent.bind("<Right>", lambda e: self.next_image())
        self.parent.bind("<Escape>", lambda e: self.parent.destroy())
        
    def load_image(self):
        """加载当前索引的图片"""
        if 0 <= self.current_index < len(self.image_files):
            image_path = self.image_files[self.current_index]
            
            # 加载并调整图片大小以适应窗口
            try:
                img = Image.open(image_path)
                
                # 获取窗口大小
                window_width = self.image_frame.winfo_width()
                window_height = self.image_frame.winfo_height()
                
                # 如果窗口还没初始化，使用默认大小
                if window_width == 1:
                    window_width = 800
                if window_height == 1:
                    window_height = 500
                    
                # 计算调整后的大小，保持纵横比
                img.thumbnail((window_width - 40, window_height - 40))
                photo = ImageTk.PhotoImage(img)
                
                self.image_label.config(image=photo)
                self.image_label.image = photo  # 保持引用
                
                # 更新状态和图片信息
                self.status_var.set(f"{self.current_index + 1}/{len(self.image_files)}")
                self.image_info.config(text=f"{os.path.basename(image_path)} ({img.width}×{img.height})")
                
            except Exception as e:
                print(f"无法加载图片 {image_path}: {e}")
                self.image_label.config(text=f"无法加载图片: {str(e)}")
                
    def prev_image(self):
        """显示上一张图片"""
        self.current_index = (self.current_index - 1) % len(self.image_files)
        self.load_image()
        
    def next_image(self):
        """显示下一张图片"""
        self.current_index = (self.current_index + 1) % len(self.image_files)
        self.load_image()

if __name__ == "__main__":
    root = ThemedTk()
    app = PhotoAlbumApp(root)
    root.mainloop()