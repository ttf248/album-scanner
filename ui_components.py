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
