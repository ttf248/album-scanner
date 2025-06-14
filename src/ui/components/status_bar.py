import tkinter as tk
from .style_manager import get_safe_font, StyleManager
from ...utils.logger import get_logger, log_info, log_error, log_exception

class StatusBar:
    """现代化状态栏组件"""
    
    def __init__(self, parent, style_manager=None):
        self.parent = parent
        self.status_var = tk.StringVar()
        self.info_var = tk.StringVar()
        self.progress_var = tk.StringVar()
        self.logger = get_logger('ui.status')
        
        # 使用传入的样式管理器或创建新实例
        if style_manager:
            self.style_manager = style_manager
        else:
            from tkinter import ttk
            style = ttk.Style()
            self.style_manager = StyleManager(parent, style)
        
        try:
            self.create_widgets()
            log_info("状态栏组件创建成功", 'ui.status')
        except Exception as e:
            log_exception(f"创建状态栏组件时出错: {e}", 'ui.status')
    
    def create_widgets(self):
        """创建现代化状态栏组件"""
        # 状态栏主框架 - 使用卡片样式
        self.status_frame = tk.Frame(self.parent, 
                                   bg=self.style_manager.colors['card_bg'], 
                                   height=50,
                                   relief='flat',
                                   bd=1)
        self.status_frame.pack(side='bottom', fill='x', padx=16, pady=(8, 16))
        self.status_frame.pack_propagate(False)
        
        # 内容框架
        content_frame = tk.Frame(self.status_frame, bg=self.style_manager.colors['card_bg'])
        content_frame.pack(fill='both', expand=True, 
                          padx=self.style_manager.dimensions['padding_lg'], 
                          pady=self.style_manager.dimensions['padding_sm'])
        
        # 左侧状态区域
        left_frame = tk.Frame(content_frame, bg=self.style_manager.colors['card_bg'])
        left_frame.pack(side='left', fill='y')
        
        # 状态图标和文字
        self.status_icon = tk.Label(left_frame, 
                                  text="ℹ️",
                                  font=self.style_manager.fonts['body'],
                                  bg=self.style_manager.colors['card_bg'],
                                  fg=self.style_manager.colors['text_secondary'])
        self.status_icon.pack(side='left', padx=(0, 6))
        
        self.status_label = tk.Label(left_frame, 
                                   textvariable=self.status_var,
                                   font=self.style_manager.fonts['body'],
                                   bg=self.style_manager.colors['card_bg'],
                                   fg=self.style_manager.colors['text_primary'])
        self.status_label.pack(side='left')
        
        # 中间进度区域（可选显示）
        self.progress_frame = tk.Frame(content_frame, bg=self.style_manager.colors['card_bg'])
        self.progress_frame.pack(side='left', fill='x', expand=True, padx=(20, 20))
        
        self.progress_label = tk.Label(self.progress_frame,
                                     textvariable=self.progress_var,
                                     font=self.style_manager.fonts['caption'],
                                     bg=self.style_manager.colors['card_bg'],
                                     fg=self.style_manager.colors['text_secondary'])
        self.progress_label.pack()
        
        # 右侧信息区域
        right_frame = tk.Frame(content_frame, bg=self.style_manager.colors['card_bg'])
        right_frame.pack(side='right', fill='y')
        
        # 统计信息
        self.info_label = tk.Label(right_frame, 
                                 textvariable=self.info_var,
                                 font=self.style_manager.fonts['caption'],
                                 bg=self.style_manager.colors['card_bg'],
                                 fg=self.style_manager.colors['text_secondary'])
        self.info_label.pack(side='right')
        
        # 分隔符
        separator = tk.Frame(right_frame, 
                           bg=self.style_manager.colors['divider'],
                           width=1,
                           height=20)
        separator.pack(side='right', padx=(10, 10), fill='y')
        
        # 时间戳标签
        self.timestamp_var = tk.StringVar()
        self.timestamp_label = tk.Label(right_frame,
                                      textvariable=self.timestamp_var,
                                      font=self.style_manager.fonts['small'],
                                      bg=self.style_manager.colors['card_bg'],
                                      fg=self.style_manager.colors['text_tertiary'])
        self.timestamp_label.pack(side='right')
        
        # 初始化时间戳
        self.update_timestamp()
        log_info("状态栏组件初始化完成", 'ui.status')
    
    def set_status(self, message, status_type='info'):
        """设置状态消息"""
        try:
            self.status_var.set(message)
            
            # 根据状态类型更新图标和颜色
            status_config = {
                'info': {
                    'icon': 'ℹ️',
                    'color': self.style_manager.colors['text_primary']
                },
                'success': {
                    'icon': '✅',
                    'color': self.style_manager.colors['success']
                },
                'warning': {
                    'icon': '⚠️',
                    'color': self.style_manager.colors['warning']
                },
                'error': {
                    'icon': '❌',
                    'color': self.style_manager.colors['error']
                },
                'loading': {
                    'icon': '🔄',
                    'color': self.style_manager.colors['accent']
                }
            }
            
            config = status_config.get(status_type, status_config['info'])
            self.status_icon.configure(text=config['icon'])
            self.status_label.configure(fg=config['color'])
            
            # 更新时间戳
            self.update_timestamp()
            
            # 记录状态变更
            log_info(f"状态更新 [{status_type.upper()}]: {message}", 'ui.status')
        except Exception as e:
            log_error(f"设置状态时出错: {e}", 'ui.status')
    
    def set_info(self, message):
        """设置信息消息"""
        self.info_var.set(message)
    
    def set_progress(self, message):
        """设置进度信息"""
        self.progress_var.set(message)
        if message:
            self.progress_frame.pack(side='left', fill='x', expand=True, padx=(20, 20))
        else:
            self.progress_frame.pack_forget()
    
    def update_timestamp(self):
        """更新时间戳"""
        import datetime
        now = datetime.datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        self.timestamp_var.set(timestamp)
    
    def set_scan_results(self, album_count, image_count, scan_time=None):
        """设置扫描结果信息"""
        if album_count == 0:
            info_text = "未发现漫画"
        else:
            info_text = f"发现 {album_count} 个漫画，共 {image_count} 张图片"
            
        if scan_time:
            info_text += f" (耗时 {scan_time:.1f}s)"
            
        self.set_info(info_text)
        
        # 设置对应的状态
        if album_count > 0:
            self.set_status("扫描完成", 'success')
        else:
            self.set_status("扫描完成，未发现漫画", 'warning')
    
    def show_loading(self, message="正在处理..."):
        """显示加载状态"""
        self.set_status(message, 'loading')
        self.set_progress("请稍候...")
        log_info(f"显示加载状态: {message}", 'ui.status')
    
    def hide_loading(self):
        """隐藏加载状态"""
        self.set_progress("")
        log_info("隐藏加载状态", 'ui.status')