import tkinter as tk
from .style_manager import get_safe_font # Assuming get_safe_font is in style_manager.py

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