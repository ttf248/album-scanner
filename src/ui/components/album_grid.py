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