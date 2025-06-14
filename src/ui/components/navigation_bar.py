import tkinter as tk
from .style_manager import get_safe_font

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
        
        # 浏览按钮 - 添加快捷键提示
        browse_btn = tk.Button(left_frame, text="📁 选择 (Ctrl+O)",
                              font=get_safe_font('Arial', 12, 'bold'), 
                              bg='#007AFF', fg='white',
                              relief='flat', bd=0, padx=15, pady=8,
                              cursor='hand2', command=self.browse_callback)
        browse_btn.pack(side='left', padx=(0, 8))
        
        # 扫描按钮 - 添加快捷键提示
        scan_btn = tk.Button(left_frame, text="🔍 扫描 (Ctrl+S/F5)",
                            font=get_safe_font('Arial', 12, 'bold'), 
                            bg='#34C759', fg='white',
                            relief='flat', bd=0, padx=15, pady=8,
                            cursor='hand2', command=self.scan_callback)
        scan_btn.pack(side='left', padx=(0, 8))
        
        # 最近浏览按钮 - 添加快捷键提示
        recent_btn = tk.Button(left_frame, text="📚 最近 (Ctrl+R)",
                              font=get_safe_font('Arial', 12, 'bold'), 
                              bg='#FF9500', fg='white',
                              relief='flat', bd=0, padx=15, pady=8,
                              cursor='hand2', command=self.recent_callback)
        recent_btn.pack(side='left', padx=(0, 8))
        
        # 收藏按钮 - 添加快捷键提示
        fav_btn = tk.Button(left_frame, text="⭐ 收藏 (Ctrl+F)",
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
        
        # 更新快速操作提示，添加快捷键信息
        tips = [
            "1. 点击「📁 选择」按钮或按 Ctrl+O 选择包含图片的文件夹",
            "2. 点击「🔍 扫描」按钮或按 Ctrl+S/F5 自动发现相册",
            "3. 使用 Ctrl+R 查看最近浏览，Ctrl+F 管理收藏夹",
            "4. 在瀑布流中浏览和管理您的相册"
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