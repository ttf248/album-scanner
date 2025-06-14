import tkinter as tk

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