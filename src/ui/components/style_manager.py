import tkinter as tk
from tkinter import ttk
from ...utils.logger import get_logger, log_info, log_warning, log_error

def get_safe_font(font_family, size, style=None):
    """获取安全的字体配置"""
    try:
        if style:
            return (font_family, size, style)
        else:
            return (font_family, size)
    except:
        # 如果字体不可用，使用默认字体
        log_warning(f"字体 {font_family} 不可用，使用默认字体", 'ui.style')
        if style:
            return ('Arial', size, style)
        else:
            return ('Arial', size)

class StyleManager:
    """现代化样式管理器"""
    
    def __init__(self, root, style=None):
        self.root = root
        self.style = style
        self.logger = get_logger('ui.style')
        
        # 现代化颜色主题 - 基于 Arc 主题的配色方案
        self.colors = {
            # 主要背景色
            'bg_primary': '#F5F6FA',      # 主背景 - 浅灰蓝
            'bg_secondary': '#FFFFFF',     # 次要背景 - 纯白
            'bg_tertiary': '#FAFBFC',     # 第三背景 - 极浅灰
            
            # 文字颜色
            'text_primary': '#2F3349',     # 主要文字 - 深蓝灰
            'text_secondary': '#6C7293',   # 次要文字 - 中灰蓝
            'text_tertiary': '#A0A3BD',    # 第三文字 - 浅灰蓝
            'text_white': '#FFFFFF',       # 白色文字
            
            # 强调色
            'accent': '#5294E2',           # 主强调色 - Arc 蓝
            'accent_hover': '#4A90E2',     # 悬浮状态
            'accent_active': '#3B82E0',    # 激活状态
            'accent_light': '#E3F2FD',     # 浅色强调
            
            # 状态色
            'success': '#27AE60',          # 成功绿
            'success_light': '#E8F5E8',    # 浅绿背景
            'warning': '#F39C12',          # 警告橙
            'warning_light': '#FFF3CD',    # 浅橙背景
            'error': '#E74C3C',            # 错误红
            'error_light': '#FADBD8',      # 浅红背景
            
            # 卡片和容器
            'card_bg': '#FFFFFF',          # 卡片背景
            'card_hover': '#F8F9FA',       # 卡片悬浮
            'card_border': '#E1E8ED',      # 卡片边框
            'card_shadow': '#00000010',    # 卡片阴影
            
            # 边框和分割线
            'border': '#E1E8ED',           # 主边框
            'border_light': '#F0F3F7',     # 浅边框
            'divider': '#EBEEF3',          # 分割线
            
            # 按钮颜色
            'button_primary': '#5294E2',   # 主按钮
            'button_primary_hover': '#4A90E2',
            'button_secondary': '#F8F9FA', # 次要按钮
            'button_secondary_hover': '#E9ECEF',
            'button_danger': '#E74C3C',    # 危险按钮
            'button_danger_hover': '#C0392B',
            
            # 输入框
            'input_bg': '#FFFFFF',
            'input_border': '#E1E8ED',
            'input_focus': '#5294E2',
            
            # 滚动条
            'scrollbar_bg': '#F5F6FA',
            'scrollbar_thumb': '#C1C7D0',
            'scrollbar_thumb_hover': '#A8B2C1'
        }
        
        # 现代化字体配置
        self.fonts = {
            'title': get_safe_font('Segoe UI', 28, 'bold'),      # 大标题
            'heading': get_safe_font('Segoe UI', 20, 'bold'),    # 标题
            'subheading': get_safe_font('Segoe UI', 16, 'bold'), # 子标题
            'body': get_safe_font('Segoe UI', 14),               # 正文
            'body_medium': get_safe_font('Segoe UI', 14, 'bold'), # 中等正文
            'caption': get_safe_font('Segoe UI', 12),            # 说明文字
            'small': get_safe_font('Segoe UI', 11),              # 小字
            'button': get_safe_font('Segoe UI', 13, 'bold'),     # 按钮文字
            'button_small': get_safe_font('Segoe UI', 12),       # 小按钮
            'mono': get_safe_font('Consolas', 12),               # 等宽字体
        }
        
        # 尺寸和间距
        self.dimensions = {
            # 圆角
            'border_radius': 8,
            'border_radius_small': 4,
            'border_radius_large': 12,
            
            # 间距
            'padding_xs': 4,
            'padding_sm': 8,
            'padding_md': 12,
            'padding_lg': 16,
            'padding_xl': 20,
            'padding_xxl': 24,
            
            # 按钮尺寸
            'button_height': 36,
            'button_height_small': 28,
            'button_height_large': 44,
            
            # 卡片
            'card_padding': 16,
            'card_margin': 12,
            
            # 阴影
            'shadow_offset': 2,
            'shadow_blur': 8
        }
        
        log_info("样式管理器初始化完成", 'ui.style')
        self.configure_styles()
    
    def configure_styles(self):
        """配置现代化样式"""
        try:
            # 设置根窗口背景
            self.root.configure(bg=self.colors['bg_primary'])
            
            if self.style:
                self.configure_ttk_styles()
            
            log_info("现代化样式配置完成", 'ui.style')
        except Exception as e:
            log_error(f"配置样式时出错: {e}", 'ui.style')
    
    def configure_ttk_styles(self):
        """配置 TTK 样式"""
        # 配置按钮样式
        self.style.configure('Modern.TButton',
                           background=self.colors['button_primary'],
                           foreground=self.colors['text_white'],
                           font=self.fonts['button'],
                           borderwidth=0,
                           focuscolor='none',
                           relief='flat')
        
        self.style.map('Modern.TButton',
                      background=[('active', self.colors['button_primary_hover']),
                                ('pressed', self.colors['accent_active'])])
        
        # 次要按钮样式
        self.style.configure('Secondary.TButton',
                           background=self.colors['button_secondary'],
                           foreground=self.colors['text_primary'],
                           font=self.fonts['button'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.map('Secondary.TButton',
                      background=[('active', self.colors['button_secondary_hover'])])
        
        # 标签样式
        self.style.configure('Title.TLabel',
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_primary'],
                           font=self.fonts['title'])
        
        self.style.configure('Heading.TLabel',
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_primary'],
                           font=self.fonts['heading'])
        
        self.style.configure('Body.TLabel',
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_secondary'],
                           font=self.fonts['body'])
        
        # 框架样式
        self.style.configure('Card.TFrame',
                           background=self.colors['card_bg'],
                           relief='flat',
                           borderwidth=1)
    
    def get_button_style(self, button_type='primary'):
        """获取按钮样式配置"""
        styles = {
            'primary': {
                'bg': self.colors['button_primary'],
                'fg': self.colors['text_white'],
                'activebackground': self.colors['button_primary_hover'],
                'activeforeground': self.colors['text_white'],
                'font': self.fonts['button'],
                'relief': 'flat',
                'borderwidth': 0,
                'cursor': 'hand2'
            },
            'secondary': {
                'bg': self.colors['button_secondary'],
                'fg': self.colors['text_primary'],
                'activebackground': self.colors['button_secondary_hover'],
                'activeforeground': self.colors['text_primary'],
                'font': self.fonts['button'],
                'relief': 'flat',
                'borderwidth': 1,
                'cursor': 'hand2'
            },
            'danger': {
                'bg': self.colors['button_danger'],
                'fg': self.colors['text_white'],
                'activebackground': self.colors['button_danger_hover'],
                'activeforeground': self.colors['text_white'],
                'font': self.fonts['button'],
                'relief': 'flat',
                'borderwidth': 0,
                'cursor': 'hand2'
            }
        }
        return styles.get(button_type, styles['primary'])
    
    def get_card_style(self):
        """获取卡片样式配置"""
        return {
            'bg': self.colors['card_bg'],
            'relief': 'flat',
            'borderwidth': 1,
            'highlightthickness': 0
        }
    
    def create_hover_effect(self, widget, enter_color, leave_color):
        """为控件添加悬浮效果"""
        def on_enter(event):
            widget.configure(bg=enter_color)
        
        def on_leave(event):
            widget.configure(bg=leave_color)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)