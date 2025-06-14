import tkinter as tk
from tkinter import ttk, messagebox
from .style_manager import StyleManager

class SettingsDialog:
    """设置对话框"""
    
    def __init__(self, parent, config_manager, style_manager=None):
        self.parent = parent
        self.config_manager = config_manager
        self.style_manager = style_manager
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("设置")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # 设置窗口属性
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_widgets()
        
        # 加载当前配置
        self.load_settings()
        
        # 界面创建完成后居中显示
        self.center_window()
        
    def center_window(self):
        """将窗口居中显示"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_widgets(self):
        """创建设置界面组件"""
        # 主容器
        main_frame = tk.Frame(self.dialog)
        if self.style_manager:
            main_frame.configure(bg=self.style_manager.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(main_frame, text="应用设置", font=('Microsoft YaHei', 16, 'bold'))
        if self.style_manager:
            title_label.configure(
                bg=self.style_manager.colors['bg_primary'],
                fg=self.style_manager.colors['text_primary']
            )
        title_label.pack(pady=(0, 20))
        
        # 相册切换设置组
        album_frame = tk.LabelFrame(main_frame, text="相册切换设置", font=('Microsoft YaHei', 12))
        if self.style_manager:
            album_frame.configure(
                bg=self.style_manager.colors['bg_primary'],
                fg=self.style_manager.colors['text_primary']
            )
        album_frame.pack(fill='x', pady=(0, 15))
        
        # 自动切换相册选项
        self.auto_switch_var = tk.BooleanVar()
        auto_switch_cb = tk.Checkbutton(
            album_frame,
            text="启用自动切换相册",
            variable=self.auto_switch_var,
            font=('Microsoft YaHei', 10)
        )
        if self.style_manager:
            auto_switch_cb.configure(
                bg=self.style_manager.colors['bg_primary'],
                fg=self.style_manager.colors['text_primary'],
                selectcolor=self.style_manager.colors['card_bg']
            )
        auto_switch_cb.pack(anchor='w', padx=10, pady=5)
        
        # 说明文字
        desc_label = tk.Label(
            album_frame,
            text="启用后，在图片浏览时可以自动切换到上一个/下一个相册",
            font=('Microsoft YaHei', 9),
            wraplength=400
        )
        if self.style_manager:
            desc_label.configure(
                bg=self.style_manager.colors['bg_primary'],
                fg=self.style_manager.colors['text_secondary']
            )
        desc_label.pack(anchor='w', padx=25, pady=(0, 10))
        
        # 显示提示设置组
        notification_frame = tk.LabelFrame(main_frame, text="提示设置", font=('Microsoft YaHei', 12))
        if self.style_manager:
            notification_frame.configure(
                bg=self.style_manager.colors['bg_primary'],
                fg=self.style_manager.colors['text_primary']
            )
        notification_frame.pack(fill='x', pady=(0, 15))
        
        # 显示切换提示选项
        self.show_notification_var = tk.BooleanVar()
        notification_cb = tk.Checkbutton(
            notification_frame,
            text="显示相册切换提示",
            variable=self.show_notification_var,
            font=('Microsoft YaHei', 10)
        )
        if self.style_manager:
            notification_cb.configure(
                bg=self.style_manager.colors['bg_primary'],
                fg=self.style_manager.colors['text_primary'],
                selectcolor=self.style_manager.colors['card_bg']
            )
        notification_cb.pack(anchor='w', padx=10, pady=5)
        
        # 说明文字
        notif_desc_label = tk.Label(
            notification_frame,
            text="启用后，切换相册时会显示提示信息",
            font=('Microsoft YaHei', 9),
            wraplength=400
        )
        if self.style_manager:
            notif_desc_label.configure(
                bg=self.style_manager.colors['bg_primary'],
                fg=self.style_manager.colors['text_secondary']
            )
        notif_desc_label.pack(anchor='w', padx=25, pady=(0, 10))
        
        # 按钮区域
        button_frame = tk.Frame(main_frame)
        if self.style_manager:
            button_frame.configure(bg=self.style_manager.colors['bg_primary'])
        button_frame.pack(fill='x', pady=(20, 0))
        
        # 取消按钮
        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            command=self.cancel,
            font=('Microsoft YaHei', 10),
            width=10
        )
        if self.style_manager:
            btn_style = self.style_manager.get_button_style('secondary')
            cancel_btn.configure(**btn_style)
        cancel_btn.pack(side='right', padx=(10, 0))
        
        # 确定按钮
        ok_btn = tk.Button(
            button_frame,
            text="确定",
            command=self.save_settings,
            font=('Microsoft YaHei', 10),
            width=10
        )
        if self.style_manager:
            btn_style = self.style_manager.get_button_style('primary')
            ok_btn.configure(**btn_style)
        ok_btn.pack(side='right')
        
        # 恢复默认按钮
        reset_btn = tk.Button(
            button_frame,
            text="恢复默认",
            command=self.reset_to_default,
            font=('Microsoft YaHei', 10),
            width=10
        )
        if self.style_manager:
            btn_style = self.style_manager.get_button_style('secondary')
            reset_btn.configure(**btn_style)
        reset_btn.pack(side='left')
        
    def load_settings(self):
        """加载当前设置"""
        self.auto_switch_var.set(self.config_manager.get_auto_switch_album())
        self.show_notification_var.set(self.config_manager.get_show_switch_notification())
        
    def save_settings(self):
        """保存设置"""
        try:
            # 保存设置
            self.config_manager.set_auto_switch_album(self.auto_switch_var.get())
            self.config_manager.set_show_switch_notification(self.show_notification_var.get())
            
            # 显示成功消息
            messagebox.showinfo("设置", "设置已保存")
            
            # 关闭对话框
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败：{str(e)}")
            
    def reset_to_default(self):
        """恢复默认设置"""
        if messagebox.askyesno("确认", "确定要恢复默认设置吗？"):
            self.auto_switch_var.set(True)
            self.show_notification_var.set(True)
            
    def cancel(self):
        """取消设置"""
        self.dialog.destroy()
        
    def show(self):
        """显示对话框"""
        # 确保窗口可见并置于前台
        self.dialog.deiconify()
        self.dialog.lift()
        self.dialog.focus_set()
        
        # 等待窗口关闭
        self.dialog.wait_window()