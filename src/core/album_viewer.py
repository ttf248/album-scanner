import os
from tkinter import messagebox, Toplevel
from ..utils.image_utils import ImageProcessor
from ..ui.components.image_viewer import ImageViewer  # 直接从components导入
from ..ui.components.style_manager import get_safe_font  # 直接从components导入
from PIL import Image, ImageTk
import tkinter as tk

class AlbumViewerManager:
    """相册查看器管理器"""
    
    def __init__(self, app):
        self.app = app
    
    def open_album(self, folder_path):
        """打开相册查看"""
        try:
            image_files = ImageProcessor.get_image_files(folder_path)
            
            if not image_files:
                messagebox.showinfo("提示", "该文件夹中没有找到图片")
                return
            
            # 添加到最近浏览
            self.app.config_manager.add_recent_album(folder_path)
                
            # 创建图片查看器窗口
            album_window = self._create_album_window(folder_path)
            
            # 创建图片查看器
            try:
                viewer = ImageViewer(album_window, image_files, self.app.config_manager)
                
                # 更新主窗口状态
                album_name = os.path.basename(folder_path)
                self.app.status_bar.set_status(f"已打开相册: {album_name}")
                self.app.status_bar.set_info(f"{len(image_files)} 张图片")
                
            except Exception as e:
                print(f"创建图片查看器失败: {e}")
                # 创建简单的图片查看器
                self._create_simple_viewer(album_window, image_files, os.path.basename(folder_path))
            
        except Exception as e:
            messagebox.showerror("错误", f"打开相册时发生错误：{str(e)}")
            self.app.status_bar.set_status("打开相册失败")
    
    def _create_album_window(self, folder_path):
        """创建相册窗口"""
        album_window = Toplevel(self.app.root)
        album_name = os.path.basename(folder_path)
        album_window.title(f"📸 相册查看器 - {album_name}")
        album_window.geometry("1000x750")
        album_window.minsize(800, 600)
        
        # 设置窗口图标和属性
        album_window.configure(bg='#1D1D1F')
        
        # 居中显示窗口
        album_window.transient(self.app.root)
        album_window.grab_set()
        
        return album_window
    
    def _create_simple_viewer(self, window, image_files, album_name):
        """创建简单的图片查看器"""
        try:
            window.title(f"简单查看器 - {album_name}")
            window.configure(bg='black')
            
            # 当前图片索引
            current_index = [0]
            
            # 图片显示标签
            image_label = tk.Label(window, bg='black')
            image_label.pack(fill='both', expand=True)
            
            # 控制按钮
            control_frame = tk.Frame(window, bg='gray', height=50)
            control_frame.pack(side='bottom', fill='x')
            control_frame.pack_propagate(False)
            
            def load_image():
                try:
                    if image_files and 0 <= current_index[0] < len(image_files):
                        image_path = image_files[current_index[0]]
                        
                        # 加载图片
                        with Image.open(image_path) as img:
                            # 调整大小
                            window.update()
                            width = window.winfo_width() or 800
                            height = (window.winfo_height() or 600) - 50
                            
                            img.thumbnail((width, height), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(img)
                            
                            image_label.configure(image=photo)
                            image_label.image = photo
                        
                        # 更新标题
                        filename = os.path.basename(image_path)
                        window.title(f"📸 {filename} ({current_index[0]+1}/{len(image_files)})")
                        
                except Exception as e:
                    print(f"简单查看器加载图片失败: {e}")
                    image_label.configure(image='', text=f"无法加载图片\n{e}")
            
            def prev_image():
                if current_index[0] > 0:
                    current_index[0] -= 1
                    load_image()
            
            def next_image():
                if current_index[0] < len(image_files) - 1:
                    current_index[0] += 1
                    load_image()
            
            # 按钮 - 添加快捷键提示  
            tk.Button(control_frame, text="上一张 (←)", command=prev_image).pack(side='left', padx=5, pady=5)
            tk.Button(control_frame, text="下一张 (→)", command=next_image).pack(side='left', padx=5, pady=5)
            tk.Button(control_frame, text="关闭 (ESC)", command=window.destroy).pack(side='right', padx=5, pady=5)
            
            # 添加快捷键说明标签
            help_label = tk.Label(control_frame, 
                text="快捷键: ← → 切换图片 | ESC 关闭", 
                bg='gray', fg='white', font=get_safe_font('Arial', 9))
            help_label.pack(pady=2)
            
            # 键盘绑定
            def on_key(event):
                if event.keysym == 'Left':
                    prev_image()
                elif event.keysym == 'Right':
                    next_image()
                elif event.keysym == 'Escape':
                    window.destroy()
            
            window.bind('<Key>', on_key)
            window.focus_set()
            
            # 加载第一张图片
            window.after(100, load_image)
            
        except Exception as e:
            print(f"创建简单查看器失败: {e}")
            messagebox.showerror("错误", "无法创建图片查看器")
            window.destroy()
