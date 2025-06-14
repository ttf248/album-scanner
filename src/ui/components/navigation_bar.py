import tkinter as tk
from tkinter import ttk
from .style_manager import get_safe_font, StyleManager

class NavigationBar:
    """现代化导航栏组件"""
    
    def __init__(self, parent, browse_callback, scan_callback, path_var, recent_callback, favorites_callback, style_manager=None):
        self.parent = parent
        self.browse_callback = browse_callback
        self.scan_callback = scan_callback
        self.path_var = path_var
        self.recent_callback = recent_callback
        self.favorites_callback = favorites_callback
        
        # 新增回调
        self.home_callback = None  # 将由app_manager设置
        self.settings_callback = None  # 将由app_manager设置
        
        # 使用传入的样式管理器或创建新实例
        if style_manager:
            self.style_manager = style_manager
        else:
            from tkinter import ttk
            style = ttk.Style()
            self.style_manager = StyleManager(parent, style)
        
        # 确保样式管理器正确初始化
        self._ensure_style_manager()
        
        self.create_widgets()
    
    def _ensure_style_manager(self):
        """确保样式管理器正确初始化，提供默认配置"""
        # 检查是否有colors属性
        if not hasattr(self.style_manager, 'colors') or not self.style_manager.colors:
            # 提供默认颜色配置
            self.style_manager.colors = {
                'bg': '#f5f5f5',
                'card_bg': '#ffffff',
                'text_primary': '#333333',
                'text_secondary': '#666666',
                'text_tertiary': '#999999',
                'accent': '#007acc',
                'accent_light': '#e6f3ff',
                'button_primary': '#007acc',
                'button_primary_hover': '#005999',
                'button_secondary': '#f0f0f0',
                'button_secondary_hover': '#e0e0e0',
                'bg_tertiary': '#f8f9fa'
            }
        
        # 检查是否有fonts属性
        if not hasattr(self.style_manager, 'fonts') or not self.style_manager.fonts:
            # 提供默认字体配置
            self.style_manager.fonts = {
                'body': ('Segoe UI', 10),
                'caption': ('Segoe UI', 9),
                'small': ('Segoe UI', 8),
                'mono': ('Consolas', 9)
            }
        
        # 检查是否有dimensions属性
        if not hasattr(self.style_manager, 'dimensions') or not self.style_manager.dimensions:
            # 提供默认尺寸配置
            self.style_manager.dimensions = {
                'padding_sm': 4,
                'padding_lg': 12,
                'padding_xl': 16
            }
        
        # 确保方法存在
        if not hasattr(self.style_manager, 'get_button_style'):
            self.style_manager.get_button_style = self._default_get_button_style
        
        if not hasattr(self.style_manager, 'create_hover_effect'):
            self.style_manager.create_hover_effect = self._default_create_hover_effect
        
        if not hasattr(self.style_manager, 'add_tooltip'):
            self.style_manager.add_tooltip = self._default_add_tooltip
    
    def _default_get_button_style(self, button_type):
        """默认按钮样式"""
        if button_type == 'primary':
            return {
                'bg': self.style_manager.colors['button_primary'],
                'fg': 'white',
                'font': self.style_manager.fonts['body'],
                'relief': 'flat',
                'borderwidth': 0,
                'cursor': 'hand2'
            }
        else:
            return {
                'bg': self.style_manager.colors['button_secondary'],
                'fg': self.style_manager.colors['text_primary'],
                'font': self.style_manager.fonts['body'],
                'relief': 'flat',
                'borderwidth': 0,
                'cursor': 'hand2'
            }
    
    def _default_create_hover_effect(self, widget, hover_color, normal_color):
        """默认悬浮效果"""
        def on_enter(e):
            try:
                widget.configure(bg=hover_color)
            except:
                pass
        
        def on_leave(e):
            try:
                widget.configure(bg=normal_color)
            except:
                pass
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def _default_add_tooltip(self, widget, text):
        """默认工具提示"""
        def show_tooltip(event):
            # 简单的工具提示实现
            pass
        
        widget.bind('<Enter>', show_tooltip)
    
    def create_widgets(self):
        """创建现代化导航栏组件"""
        try:
            # 导航栏主框架 - 使用卡片样式
            self.nav_frame = tk.Frame(self.parent, 
                                    bg=self.style_manager.colors.get('card_bg', '#ffffff'), 
                                    height=120,  # 增加高度以容纳面包屑
                                    relief='flat',
                                    bd=1)
            self.nav_frame.pack(side='top', fill='x', padx=16, pady=(16, 8))
            self.nav_frame.pack_propagate(False)
            
            # 内容框架
            content_frame = tk.Frame(self.nav_frame, bg=self.style_manager.colors.get('card_bg', '#ffffff'))
            content_frame.pack(fill='both', expand=True, 
                              padx=self.style_manager.dimensions.get('padding_xl', 16), 
                              pady=self.style_manager.dimensions.get('padding_lg', 12))
            
            # 面包屑导航区域
            self.breadcrumb_frame = tk.Frame(content_frame, bg=self.style_manager.colors.get('card_bg', '#ffffff'))
            self.breadcrumb_frame.pack(side='top', fill='x', pady=(0, 8))
            
            # 创建面包屑导航
            self.create_breadcrumb()
            
            # 顶部按钮区域
            button_frame = tk.Frame(content_frame, bg=self.style_manager.colors.get('card_bg', '#ffffff'))
            button_frame.pack(side='top', fill='x')
            
            # 创建现代化按钮
            self.create_modern_buttons(button_frame)
            
            # 路径显示区域
            path_frame = tk.Frame(content_frame, bg=self.style_manager.colors.get('card_bg', '#ffffff'))
            path_frame.pack(side='bottom', fill='x', pady=(12, 0))
            
            # 路径标签和显示
            self.create_path_display(path_frame)
        except Exception as e:
            print(f"创建导航栏组件时出错: {e}")
            # 创建简化版本
            self._create_simple_widgets()
    
    def _create_simple_widgets(self):
        """创建简化版导航栏（错误恢复）"""
        self.nav_frame = tk.Frame(self.parent, bg='#ffffff', height=80)
        self.nav_frame.pack(side='top', fill='x', padx=16, pady=(16, 8))
        
        # 简单按钮
        tk.Button(self.nav_frame, text='选择文件夹', command=self.browse_callback).pack(side='left', padx=5)
        tk.Button(self.nav_frame, text='扫描漫画', command=self.scan_callback).pack(side='left', padx=5)
        tk.Button(self.nav_frame, text='最近浏览', command=self.recent_callback).pack(side='left', padx=5)
        tk.Button(self.nav_frame, text='我的收藏', command=self.favorites_callback).pack(side='left', padx=5)
        
        # 简单路径显示
        tk.Label(self.nav_frame, textvariable=self.path_var).pack(side='bottom', fill='x')

    def create_breadcrumb(self):
        """创建面包屑导航"""
        # 清空现有面包屑
        for widget in self.breadcrumb_frame.winfo_children():
            widget.destroy()
        
        # 面包屑容器
        breadcrumb_container = tk.Frame(self.breadcrumb_frame, bg=self.style_manager.colors['card_bg'])
        breadcrumb_container.pack(side='left')
        
        # 首页按钮
        home_btn = tk.Button(breadcrumb_container,
                           text="🏠 首页",
                           command=self.go_home,
                           font=self.style_manager.fonts['caption'],
                           bg=self.style_manager.colors['card_bg'],
                           fg=self.style_manager.colors['accent'],
                           relief='flat',
                           borderwidth=0,
                           padx=8,
                           pady=4,
                           cursor='hand2')
        home_btn.pack(side='left')
        
        self.style_manager.create_hover_effect(
            home_btn,
            self.style_manager.colors['accent_light'],
            self.style_manager.colors['card_bg']
        )
        self.style_manager.add_tooltip(home_btn, "返回扫描结果首页")
        
        # 分隔符和当前位置将由update_breadcrumb动态更新
        self.current_location_label = tk.Label(breadcrumb_container,
                                             text="",
                                             font=self.style_manager.fonts['caption'],
                                             bg=self.style_manager.colors['card_bg'],
                                             fg=self.style_manager.colors['text_secondary'])
        self.current_location_label.pack(side='left', padx=(4, 0))
    
    def update_breadcrumb(self, location_type="home", location_name=""):
        """更新面包屑显示"""
        if location_type == "home":
            self.current_location_label.configure(text="")
        elif location_type == "recent":
            self.current_location_label.configure(text=" > 📝 最近浏览")
        elif location_type == "favorites":
            self.current_location_label.configure(text=" > ⭐ 我的收藏")
        elif location_type == "scan":
            folder_name = location_name or "扫描结果"
            if len(folder_name) > 20:
                folder_name = folder_name[:17] + "..."
            self.current_location_label.configure(text=f" > 📁 {folder_name}")
    
    def go_home(self):
        """返回首页（扫描结果）"""
        if self.home_callback:
            self.home_callback()
    
    def create_modern_buttons(self, parent):
        """创建现代化导航按钮"""
        # 按钮配置：文本、回调函数、类型、快捷键、工具提示
        buttons_config = [
            {
                'text': '📁 选择文件夹',
                'command': self.browse_callback,
                'type': 'primary',
                'shortcut': 'Ctrl+O',
                'tooltip': '选择要扫描的文件夹 (Ctrl+O)'
            },
            {
                'text': '🔍 扫描漫画',
                'command': self.scan_callback,
                'type': 'primary',
                'shortcut': 'Ctrl+S',
                'tooltip': '开始扫描选定文件夹中的漫画 (Ctrl+S)'
            },
            {
                'text': '🕒 最近浏览',
                'command': self.recent_callback,
                'type': 'secondary',
                'shortcut': 'Ctrl+R',
                'tooltip': '查看最近浏览的漫画 (Ctrl+R)'
            },
            {
                'text': '⭐ 我的收藏',
                'command': self.favorites_callback,
                'type': 'secondary',
                'shortcut': 'Ctrl+F',
                'tooltip': '查看收藏的漫画 (Ctrl+F)'
            },
            {
                'text': '⚙️ 设置',
                'command': lambda: self.settings_callback() if self.settings_callback else None,
                'type': 'secondary',
                'shortcut': 'Ctrl+,',
                'tooltip': '打开设置对话框 (Ctrl+,)'
            }
        ]
        
        self.buttons = []
        
        for i, config in enumerate(buttons_config):
            # 创建按钮容器
            btn_container = tk.Frame(parent, bg=self.style_manager.colors['card_bg'])
            btn_container.pack(side='left', padx=(0, 12) if i < len(buttons_config) - 1 else (0, 0))
            
            # 获取按钮样式
            btn_style = self.style_manager.get_button_style(config['type'])
            
            # 创建按钮
            btn = tk.Button(btn_container, 
                          text=config['text'],
                          command=config['command'],
                          **btn_style,
                          padx=self.style_manager.dimensions['padding_lg'],
                          pady=self.style_manager.dimensions['padding_sm'])
            btn.pack()
            
            # 添加悬浮效果
            if config['type'] == 'primary':
                self.style_manager.create_hover_effect(
                    btn, 
                    self.style_manager.colors['button_primary_hover'],
                    self.style_manager.colors['button_primary']
                )
            else:
                self.style_manager.create_hover_effect(
                    btn, 
                    self.style_manager.colors['button_secondary_hover'],
                    self.style_manager.colors['button_secondary']
                )
            
            # 添加工具提示
            self.style_manager.add_tooltip(btn, config['tooltip'])
            
            # 快捷键标签
            if config.get('shortcut'):
                shortcut_label = tk.Label(btn_container, 
                                        text=config['shortcut'],
                                        font=self.style_manager.fonts['small'],
                                        bg=self.style_manager.colors['card_bg'],
                                        fg=self.style_manager.colors['text_tertiary'])
                shortcut_label.pack(pady=(2, 0))
            
            self.buttons.append(btn)
    
    def create_path_display(self, parent):
        """创建路径显示区域"""
        # 路径容器
        path_container = tk.Frame(parent, 
                                bg=self.style_manager.colors['bg_tertiary'],
                                relief='flat',
                                bd=1)
        path_container.pack(fill='x', pady=(8, 0))
        
        # 内容框架
        path_content = tk.Frame(path_container, bg=self.style_manager.colors['bg_tertiary'])
        path_content.pack(fill='x', padx=12, pady=8)
        
        # 路径图标和标签
        path_icon = tk.Label(path_content, 
                           text="📍",
                           font=self.style_manager.fonts['body'],
                           bg=self.style_manager.colors['bg_tertiary'],
                           fg=self.style_manager.colors['text_secondary'])
        path_icon.pack(side='left')
        
        path_label = tk.Label(path_content, 
                            text="当前路径:",
                            font=self.style_manager.fonts['body'],
                            bg=self.style_manager.colors['bg_tertiary'],
                            fg=self.style_manager.colors['text_secondary'])
        path_label.pack(side='left', padx=(4, 8))
        
        # 路径显示 - 支持长路径省略
        self.path_display = tk.Label(path_content, 
                                   textvariable=self.path_var,
                                   font=self.style_manager.fonts['mono'],
                                   bg=self.style_manager.colors['bg_tertiary'],
                                   fg=self.style_manager.colors['text_primary'],
                                   anchor='w',
                                   justify='left')
        self.path_display.pack(side='left', fill='x', expand=True)
        
        # 为路径显示添加悬浮提示（显示完整路径）
        def show_full_path(event):
            full_path = self.path_var.get()
            if full_path:
                self.style_manager.add_tooltip(self.path_display, full_path)
        
        self.path_display.bind('<Enter>', show_full_path)
        
        # 路径复制按钮
        copy_btn = tk.Button(path_content,
                           text="📋",
                           command=self.copy_path_to_clipboard,
                           font=self.style_manager.fonts['small'],
                           bg=self.style_manager.colors['bg_tertiary'],
                           fg=self.style_manager.colors['text_secondary'],
                           relief='flat',
                           borderwidth=0,
                           padx=4,
                           cursor='hand2')
        copy_btn.pack(side='right')
        
        self.style_manager.add_tooltip(copy_btn, "复制路径到剪贴板")
        self.style_manager.create_hover_effect(
            copy_btn,
            self.style_manager.colors['accent_light'],
            self.style_manager.colors['bg_tertiary']
        )
    
    def copy_path_to_clipboard(self):
        """复制当前路径到剪贴板"""
        path = self.path_var.get()
        if path:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(path)
            # 可以添加一个临时提示表示复制成功
            print(f"路径已复制到剪贴板: {path}")
    
    def update_button_states(self, has_path=False, is_scanning=False):
        """更新按钮状态"""
        if len(self.buttons) >= 2:
            # 扫描按钮只在有路径时启用
            scan_btn = self.buttons[1]
            if has_path and not is_scanning:
                scan_btn.configure(state='normal')
            else:
                scan_btn.configure(state='disabled')
            
            # 扫描时禁用选择文件夹按钮
            browse_btn = self.buttons[0]
            if is_scanning:
                browse_btn.configure(state='disabled')
            else:
                browse_btn.configure(state='normal')