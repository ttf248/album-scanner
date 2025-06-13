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
    """瀑布流相册网格"""
    
    def __init__(self, parent, open_callback, favorite_callback):
        self.parent = parent
        self.open_callback = open_callback
        self.favorite_callback = favorite_callback
        self.is_favorite = None  # 由外部设置
        self.nav_bar = None  # 导航栏引用
        
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
        
    def display_albums(self, albums):
        """显示相册（带滚动支持）"""
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
                    
                    # 创建相册卡片
                    album_frame = tk.Frame(self.scrollable_frame, bg='white', relief='solid', bd=1)
                    album_frame.pack(fill='x', padx=15, pady=8)
                    
                    # 相册信息
                    info_frame = tk.Frame(album_frame, bg='white')
                    info_frame.pack(fill='x', padx=15, pady=12)
                    
                    # 名称
                    name_label = tk.Label(info_frame, text=album_name, 
                                         font=get_safe_font('Arial', 14, 'bold'), 
                                         bg='white', fg='black')
                    name_label.pack(anchor='w')
                    
                    # 统计信息
                    stats_text = f"{image_count} 张图片"
                    if 'folder_size' in album and album['folder_size']:
                        stats_text += f" • {album['folder_size']}"
                    stats_label = tk.Label(info_frame, text=stats_text, 
                                          font=get_safe_font('Arial', 12), 
                                          bg='white', fg='gray')
                    stats_label.pack(anchor='w', pady=(2, 0))
                    
                    # 按钮框架
                    btn_frame = tk.Frame(info_frame, bg='white')
                    btn_frame.pack(anchor='w', pady=(8, 0))
                    
                    # 打开按钮
                    open_btn = tk.Button(btn_frame, text="打开", 
                                       font=get_safe_font('Arial', 10), 
                                       bg='#007AFF', fg='white',
                                       relief='flat', bd=0, padx=15, pady=6,
                                       cursor='hand2',
                                       command=lambda path=album_path: self.open_callback(path))
                    open_btn.pack(side='left', padx=(0, 8))
                    
                    # 收藏按钮
                    is_fav = self.is_favorite(album_path) if self.is_favorite else False
                    fav_text = "⭐" if is_fav else "☆"
                    fav_color = '#FF9500' if is_fav else '#C7C7CC'
                    fav_btn = tk.Button(btn_frame, text=fav_text, 
                                      font=get_safe_font('Arial', 12), 
                                      bg=fav_color, fg='white',
                                      relief='flat', bd=0, padx=12, pady=6,
                                      cursor='hand2',
                                      command=lambda path=album_path: self.favorite_callback(path))
                    fav_btn.pack(side='left')
                    
                    # 添加悬停效果
                    if hasattr(self, '_add_hover_effects'):
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
    
    def _create_fallback_display(self, albums):
        """创建备用显示"""
        try:
            if not self.grid_frame:
                return
                
            # 清除现有内容
            for widget in self.grid_frame.winfo_children():
                widget.destroy()
            
            if not albums:
                tk.Label(self.grid_frame, text="暂无相册", bg='white', fg='gray').pack(expand=True)
                return
            
            # 最简单的列表
            for album in albums:
                try:
                    frame = tk.Frame(self.grid_frame, bg='lightgray', relief='raised', bd=1)
                    frame.pack(fill='x', padx=5, pady=2)
                    
                    name = album.get('name', '未知相册')
                    count = album.get('image_count', 0)
                    path = album.get('path', '')
                    
                    tk.Label(frame, text=f"{name} ({count} 张图片)", bg='lightgray').pack(side='left', padx=5)
                    
                    if path:
                        tk.Button(frame, text="打开", 
                                command=lambda p=path: self.open_callback(p)).pack(side='right', padx=5)
                except Exception as e:
                    print(f"创建备用显示项时出错: {e}")
                    continue
                    
        except Exception as e:
            print(f"创建备用显示时出错: {e}")

    def _add_hover_effects(self, card_frame, open_btn, fav_btn):
        """添加悬停效果"""
        try:
            original_bg = card_frame.cget('bg')
            
            def on_enter(event):
                try:
                    card_frame.configure(bg='#F8F9FA')
                    # 更新内部组件背景
                    for child in card_frame.winfo_children():
                        if hasattr(child, 'configure'):
                            try:
                                child.configure(bg='#F8F9FA')
                                # 递归更新子组件
                                self._update_child_bg(child, '#F8F9FA')
                            except:
                                pass
                except:
                    pass
            
            def on_leave(event):
                try:
                    card_frame.configure(bg=original_bg)
                    # 恢复内部组件背景
                    for child in card_frame.winfo_children():
                        if hasattr(child, 'configure'):
                            try:
                                child.configure(bg=original_bg)
                                # 递归恢复子组件
                                self._update_child_bg(child, original_bg)
                            except:
                                pass
                except:
                    pass
            
            # 绑定事件
            card_frame.bind('<Enter>', on_enter)
            card_frame.bind('<Leave>', on_leave)
            
            # 为子组件也绑定事件
            for child in card_frame.winfo_children():
                try:
                    child.bind('<Enter>', on_enter)
                    child.bind('<Leave>', on_leave)
                    # 递归绑定子组件
                    self._bind_hover_recursive(child, on_enter, on_leave)
                except:
                    pass
        except Exception as e:
            print(f"绑定悬停效果时出错: {e}")
    
    def _update_child_bg(self, widget, bg_color):
        """递归更新子组件背景色"""
        try:
            for child in widget.winfo_children():
                if hasattr(child, 'configure'):
                    try:
                        # 跳过按钮，保持其原有颜色
                        if child.winfo_class() != 'Button':
                            child.configure(bg=bg_color)
                        self._update_child_bg(child, bg_color)
                    except:
                        pass
        except:
            pass
    
    def _bind_hover_recursive(self, widget, on_enter, on_leave):
        """递归绑定悬停事件"""
        try:
            for child in widget.winfo_children():
                try:
                    child.bind('<Enter>', on_enter)
                    child.bind('<Leave>', on_leave)
                    self._bind_hover_recursive(child, on_enter, on_leave)
                except:
                    pass
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
        
        # 设置窗口属性
        self.parent.configure(bg='#1D1D1F')
        
        self.create_widgets()
        self.bind_events()
        self.load_current_image()
    
    def create_widgets(self):
        """创建查看器组件"""
        # 顶部工具栏
        self.toolbar = tk.Frame(self.parent, bg='#2C2C2E', height=50)
        self.toolbar.pack(side='top', fill='x')
        self.toolbar.pack_propagate(False)
        
        # 工具栏内容
        toolbar_content = tk.Frame(self.toolbar, bg='#2C2C2E')
        toolbar_content.pack(fill='both', expand=True, padx=15, pady=10)
        
        # 文件信息
        self.file_info_var = tk.StringVar()
        info_label = tk.Label(toolbar_content, textvariable=self.file_info_var,
                             font=get_safe_font('Arial', 12, 'bold'),
                             bg='#2C2C2E', fg='white')
        info_label.pack(side='left')
        
        # 右侧按钮
        btn_frame = tk.Frame(toolbar_content, bg='#2C2C2E')
        btn_frame.pack(side='right')
        
        # 缩放按钮
        zoom_out_btn = tk.Button(btn_frame, text="缩小", 
                               font=get_safe_font('Arial', 10),
                               bg='#48484A', fg='white', relief='flat',
                               command=self.zoom_out)
        zoom_out_btn.pack(side='left', padx=2)
        
        zoom_in_btn = tk.Button(btn_frame, text="放大", 
                              font=get_safe_font('Arial', 10),
                              bg='#48484A', fg='white', relief='flat',
                              command=self.zoom_in)
        zoom_in_btn.pack(side='left', padx=2)
        
        reset_btn = tk.Button(btn_frame, text="重置", 
                            font=get_safe_font('Arial', 10),
                            bg='#48484A', fg='white', relief='flat',
                            command=self.reset_zoom)
        reset_btn.pack(side='left', padx=2)
        
        # 主图片显示区域
        self.image_frame = tk.Frame(self.parent, bg='#1D1D1F')
        self.image_frame.pack(fill='both', expand=True)
        
        # 图片标签
        self.image_label = tk.Label(self.image_frame, bg='#1D1D1F')
        self.image_label.pack(expand=True)
        
        # 底部控制栏
        self.control_frame = tk.Frame(self.parent, bg='#2C2C2E', height=60)
        self.control_frame.pack(side='bottom', fill='x')
        self.control_frame.pack_propagate(False)
        
        # 控制栏内容
        control_content = tk.Frame(self.control_frame, bg='#2C2C2E')
        control_content.pack(fill='both', expand=True, padx=20, pady=15)
        
        # 导航按钮
        prev_btn = tk.Button(control_content, text="⬅ 上一张", 
                           font=get_safe_font('Arial', 12, 'bold'),
                           bg='#007AFF', fg='white', relief='flat',
                           padx=20, pady=8, command=self.prev_image)
        prev_btn.pack(side='left')
        
        next_btn = tk.Button(control_content, text="下一张 ➡", 
                           font=get_safe_font('Arial', 12, 'bold'),
                           bg='#007AFF', fg='white', relief='flat',
                           padx=20, pady=8, command=self.next_image)
        next_btn.pack(side='left', padx=(10, 0))
        
        # 进度信息
        self.progress_var = tk.StringVar()
        progress_label = tk.Label(control_content, textvariable=self.progress_var,
                                font=get_safe_font('Arial', 12),
                                bg='#2C2C2E', fg='#8E8E93')
        progress_label.pack(side='right')
    
    def bind_events(self):
        """绑定事件"""
        # 键盘事件
        self.parent.bind('<Key>', self.on_key_press)
        self.parent.focus_set()
        
        # 双击全屏
        self.image_label.bind('<Double-Button-1>', self.toggle_fullscreen)
        
        # 鼠标滚轮缩放
        self.image_label.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # 窗口大小变化时重新调整图片
        self.parent.bind('<Configure>', self.on_window_resize)
    
    def load_current_image(self):
        """加载当前图片"""
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        try:
            image_path = self.image_files[self.current_index]
            
            # 使用PIL加载图片
            with Image.open(image_path) as img:
                # 获取原始尺寸
                original_width, original_height = img.size
                
                # 获取显示区域尺寸
                display_width = self.image_frame.winfo_width() or 800
                display_height = self.image_frame.winfo_height() or 600
                
                # 计算缩放比例
                if display_width > 100 and display_height > 100:  # 确保窗口已初始化
                    scale_x = display_width / original_width
                    scale_y = display_height / original_height
                    scale = min(scale_x, scale_y) * 0.9  # 留一些边距
                    
                    # 应用用户缩放
                    scale *= self.zoom_factor
                    
                    # 计算新尺寸
                    new_width = int(original_width * scale)
                    new_height = int(original_height * scale)
                    
                    # 调整图片大小
                    if new_width > 0 and new_height > 0:
                        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # 转换为PhotoImage
                        self.current_image = ImageTk.PhotoImage(resized_img)
                        
                        # 显示图片
                        self.image_label.configure(image=self.current_image)
                        self.image_label.image = self.current_image  # 保持引用
            
            # 更新信息显示
            filename = os.path.basename(image_path)
            self.file_info_var.set(f"📸 {filename}")
            
            progress_text = f"{self.current_index + 1} / {len(self.image_files)}"
            self.progress_var.set(progress_text)
            
        except Exception as e:
            print(f"加载图片失败 {image_path}: {e}")
            # 显示错误信息
            error_text = f"无法加载图片\n{os.path.basename(image_path)}"
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
    
    def zoom_in(self):
        """放大"""
        self.zoom_factor *= 1.2
        self.load_current_image()
    
    def zoom_out(self):
        """缩小"""
        self.zoom_factor /= 1.2
        if self.zoom_factor < 0.1:
            self.zoom_factor = 0.1
        self.load_current_image()
    
    def reset_zoom(self):
        """重置缩放"""
        self.zoom_factor = 1.0
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
    
    def on_key_press(self, event):
        """键盘事件处理"""
        if event.keysym == 'Left':
            self.prev_image()
        elif event.keysym == 'Right':
            self.next_image()
        elif event.keysym == 'Escape':
            if self.is_fullscreen:
                self.toggle_fullscreen()
            else:
                self.parent.destroy()
        elif event.keysym == 'F11':
            self.toggle_fullscreen()
        elif event.keysym == 'plus' or event.keysym == 'equal':
            self.zoom_in()
        elif event.keysym == 'minus':
            self.zoom_out()
        elif event.keysym == '0':
            self.reset_zoom()
    
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
        """上一张图片"""
        self.current_index = (self.current_index - 1) % len(self.image_files)
        self.load_image()
        
    def next_image(self):
        """下一张图片"""
        self.current_index = (self.current_index + 1) % len(self.image_files)
        self.load_image()
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
        """上一张图片"""
        self.current_index = (self.current_index - 1) % len(self.image_files)
        self.load_image()
        
    def next_image(self):
        """下一张图片"""
        self.current_index = (self.current_index + 1) % len(self.image_files)
        self.load_image()
