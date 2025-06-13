import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import os
import sys
from pathlib import Path
from ttkthemes import ThemedTk
from config import ConfigManager
from image_utils import ImageProcessor
from ui_components import StyleManager, NavigationBar, AlbumGrid, ImageViewer, StatusBar

# 设置默认编码
if sys.platform.startswith('win'):
    # Windows环境下设置控制台编码
    try:
        import locale
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass

class PhotoAlbumApp:
    """现代化相册扫描器主应用程序"""
    
    def __init__(self, root):
        self.root = root
        
        # 首先初始化管理器
        self.config_manager = ConfigManager()
        
        # 然后设置窗口
        self.setup_window()
        
        # 设置样式
        from tkinter import ttk
        self.style = ttk.Style()
        self.style_manager = StyleManager(self.root, self.style)
        
        # 初始化变量
        self.folder_path = self.config_manager.get_last_path()
        self.path_var = tk.StringVar(value=self.folder_path)
        self.albums = []
        
        # 创建UI组件
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
        
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("相册扫描器 - 现代化图片管理")
        
        # 窗口大小和位置
        window_size = self.config_manager.config.get('window_size', '1200x800')
        self.root.geometry(window_size)
        self.root.minsize(900, 600)
        
        # 设置主题
        try:
            self.root.set_theme("arc")
        except:
            pass  # 如果主题不可用，使用默认主题
        
        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap('icon.ico')  # 可以添加应用图标
            pass
        except:
            pass
        
    def create_widgets(self):
        """创建现代化UI组件"""
        try:
            # 导航栏
            self.nav_bar = NavigationBar(
                self.root, 
                self.browse_folder, 
                self.scan_albums, 
                self.path_var,
                self.show_recent_albums,
                self.show_favorites
            )
            
            # 相册网格
            self.album_grid = AlbumGrid(self.root, self.open_album, self.toggle_favorite)
            # 设置收藏检查函数
            self.album_grid.is_favorite = self.config_manager.is_favorite
            # 建立与导航栏的关联
            if hasattr(self, 'nav_bar'):
                self.album_grid.nav_bar = self.nav_bar
            
            # 状态栏
            self.status_bar = StatusBar(self.root)
            
            # 初始状态
            self.status_bar.set_status("欢迎使用相册扫描器")
            
        except Exception as e:
            print(f"创建UI组件时发生错误: {e}")
            import traceback
            traceback.print_exc()
            # 创建简化版本的UI
            self.create_fallback_ui()

    def create_fallback_ui(self):
        """创建备用简化UI"""
        print("使用简化界面模式")
        
        # 简单的顶部框架
        top_frame = tk.Frame(self.root, bg='lightgray')
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # 路径输入
        tk.Label(top_frame, text="相册路径:", bg='lightgray').pack(side='left')
        path_entry = tk.Entry(top_frame, textvariable=self.path_var, width=50)
        path_entry.pack(side='left', padx=5)
        
        # 按钮 - 添加快捷键提示
        tk.Button(top_frame, text="浏览 (Ctrl+O)", command=self.browse_folder).pack(side='left', padx=2)
        tk.Button(top_frame, text="扫描 (Ctrl+S)", command=self.scan_albums).pack(side='left', padx=2)
        tk.Button(top_frame, text="最近 (Ctrl+R)", command=self.show_recent_albums).pack(side='left', padx=2)
        tk.Button(top_frame, text="收藏 (Ctrl+F)", command=self.show_favorites).pack(side='left', padx=2)
        
        # 主内容区域
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 创建简单的相册网格
        try:
            from ui_components import AlbumGrid
            self.album_grid = AlbumGrid(main_frame, self.open_album, self.toggle_favorite)
            self.album_grid.is_favorite = self.config_manager.is_favorite
        except Exception as e:
            print(f"创建简化相册网格时出错: {e}")
            import traceback
            traceback.print_exc()
            # 创建最基本的显示
            self.album_grid = self.create_basic_album_display(main_frame)
        
        # 简单的状态显示
        status_frame = tk.Frame(self.root, bg='lightgray', height=30)
        status_frame.pack(side='bottom', fill='x')
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="使用简化界面模式")
        status_label = tk.Label(status_frame, textvariable=self.status_var, bg='lightgray')
        status_label.pack(side='left', padx=10, pady=5)
        
        # 创建一个简单的状态栏对象
        class SimpleStatusBar:
            def __init__(self, status_var):
                self.status_var = status_var
            def set_status(self, message):
                self.status_var.set(message)
            def set_info(self, message):
                pass  # 简化版本不显示额外信息
        
        self.status_bar = SimpleStatusBar(self.status_var)

    def create_basic_album_display(self, parent):
        """创建最基本的相册显示"""
        app_instance = self  # 保存对主应用的引用
        
        class BasicAlbumDisplay:
            def __init__(self, parent):
                self.parent = parent
                self.display_frame = tk.Frame(parent, bg='white')
                self.display_frame.pack(fill='both', expand=True)
                # 确保有grid_frame属性以保持兼容性
                self.grid_frame = self.display_frame
                
            def display_albums(self, albums):
                try:
                    # 清除现有内容
                    for widget in self.display_frame.winfo_children():
                        widget.destroy()
                    
                    if not albums or len(albums) == 0:
                        tk.Label(self.display_frame, text="暂无相册", 
                               bg='white', fg='gray').pack(expand=True)
                        return
                    
                    # 简单列表显示
                    for album in albums:
                        try:
                            frame = tk.Frame(self.display_frame, bg='lightblue', relief='raised', bd=1)
                            frame.pack(fill='x', padx=5, pady=2)
                            
                            # 确保相册信息完整
                            album_name = album.get('name', '未知相册')
                            image_count = album.get('image_count', 0)
                            album_path = album.get('path', '')
                            
                            tk.Label(frame, text=f"{album_name} ({image_count} 张图片)", 
                                   bg='lightblue').pack(side='left', padx=10, pady=5)
                            
                            if album_path:
                                tk.Button(frame, text="打开", 
                                        command=lambda p=album_path: app_instance.open_album(p)).pack(side='right', padx=5)
                        except Exception as e:
                            print(f"显示相册时出错: {e}")
                            continue
                except Exception as e:
                    print(f"BasicAlbumDisplay.display_albums出错: {e}")
        
        return BasicAlbumDisplay(parent)

    def bind_events(self):
        """绑定事件"""
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 键盘快捷键
        self.root.bind('<Control-o>', lambda e: self.browse_folder())
        self.root.bind('<Control-s>', lambda e: self.scan_albums())
        self.root.bind('<Control-r>', lambda e: self.show_recent_albums())
        self.root.bind('<Control-f>', lambda e: self.show_favorites())
        self.root.bind('<F5>', lambda e: self.scan_albums())
        
    def browse_folder(self):
        """浏览并选择文件夹"""
        folder_selected = filedialog.askdirectory(
            title="选择相册文件夹",
            initialdir=self.folder_path if self.folder_path else str(Path.home())
        )
        if folder_selected:
            # 确保路径正确处理Unicode字符
            folder_selected = str(Path(folder_selected))
            self.folder_path = folder_selected
            self.path_var.set(folder_selected)
            self.config_manager.set_last_path(folder_selected)
            
            # 显示文件夹名称，处理长路径
            folder_name = Path(folder_selected).name
            if len(folder_name) > 30:
                display_name = folder_name[:27] + "..."
            else:
                display_name = folder_name
            self.status_bar.set_status(f"已选择: {display_name}")
            
    def scan_albums(self):
        """扫描相册"""
        folder_path = self.path_var.get().strip()
        if not folder_path:
            messagebox.showwarning("提示", "请先选择相册文件夹\n\n💡 快捷键提示：\n• Ctrl+O: 选择文件夹\n• F5: 快速扫描")
            return
            
        # 使用pathlib验证路径
        path_obj = Path(folder_path)
        if not path_obj.exists():
            messagebox.showerror("错误", "所选文件夹不存在")
            return
            
        try:
            # 显示加载状态
            self.root.config(cursor="wait")
            self.status_bar.set_status("正在扫描相册，请稍候... (按 ESC 可取消)")
            self.root.update()
            
            # 执行扫描
            self.albums = ImageProcessor.scan_albums(str(path_obj))
            
            if not self.albums:
                messagebox.showinfo("提示", "在所选文件夹中未找到包含图片的子文件夹")
                self.status_bar.set_status("未找到相册")
                self.status_bar.set_info("")
                self.album_grid.display_albums([])
                return
                
            # 显示结果
            self.album_grid.display_albums(self.albums)
            total_images = sum(len(album['image_files']) for album in self.albums)
            
            # 显示扫描结果统计
            if len(self.albums) > 10:
                self.status_bar.set_status(f"扫描完成，找到 {len(self.albums)} 个相册（支持滚动浏览）")
            else:
                self.status_bar.set_status(f"扫描完成，找到 {len(self.albums)} 个相册")
            self.status_bar.set_info(f"共 {total_images} 张图片")
            
            # 如果相册很多，提示用户可以滚动和使用快捷键
            if len(self.albums) > 15:
                messagebox.showinfo("扫描完成", 
                    f"找到 {len(self.albums)} 个相册！\n\n"
                    "📋 浏览提示：\n"
                    "• 使用鼠标滚轮浏览所有相册\n"
                    "• Ctrl+R 查看最近浏览的相册\n"
                    "• Ctrl+F 管理收藏的相册\n"
                    "• F5 重新扫描当前文件夹")
            
        except Exception as e:
            error_msg = f"扫描相册时发生错误：{str(e)}"
            print(error_msg)
            messagebox.showerror("错误", error_msg)
            self.status_bar.set_status("扫描失败")
            self.status_bar.set_info("")
        finally:
            self.root.config(cursor="")

    def show_recent_albums(self):
        """显示最近浏览的相册"""
        recent_albums = self.config_manager.get_recent_albums()
        if not recent_albums:
            messagebox.showinfo("最近浏览", 
                "暂无最近浏览的相册\n\n"
                "💡 提示：\n"
                "• 打开任何相册后会自动记录\n"
                "• 使用 Ctrl+R 快速访问最近浏览\n"
                "• 使用 Ctrl+F 管理收藏的相册")
            return
        
        # 过滤存在的路径
        valid_albums = []
        for album_path in recent_albums:
            try:
                if os.path.exists(album_path):
                    image_files = ImageProcessor.get_image_files(album_path)
                    if image_files and len(image_files) > 0:
                        valid_albums.append({
                            'path': album_path,
                            'name': os.path.basename(album_path),
                            'image_files': image_files,
                            'cover_image': image_files[0],
                            'image_count': len(image_files),
                            'folder_size': ImageProcessor.get_folder_size(image_files)
                        })
            except Exception as e:
                print(f"处理最近相册时出错 {album_path}: {e}")
                continue
        
        if valid_albums:
            self.albums = valid_albums
            self.album_grid.display_albums(valid_albums)
            self.status_bar.set_status(f"显示 {len(valid_albums)} 个最近浏览的相册")
            total_images = sum(len(album['image_files']) for album in valid_albums)
            self.status_bar.set_info(f"共 {total_images} 张图片")
            
            # 如果结果很多，提示滚动
            if len(valid_albums) > 10:
                self.status_bar.set_status(f"显示 {len(valid_albums)} 个最近浏览的相册（支持滚动浏览）")
        else:
            messagebox.showinfo("提示", "最近浏览的相册都不存在了")
            self.status_bar.set_status("最近浏览的相册不存在")
    
    def show_favorites(self):
        """显示收藏的相册"""
        favorites = self.config_manager.get_favorites()
        if not favorites:
            messagebox.showinfo("收藏夹", 
                "暂无收藏的相册\n\n"
                "💡 使用方法：\n"
                "• 在相册列表中点击 ⭐ 按钮收藏\n"
                "• 使用 Ctrl+F 快速访问收藏夹\n"
                "• 再次点击 ⭐ 按钮可取消收藏")
            return
        
        # 过滤存在的路径
        valid_albums = []
        for album_path in favorites:
            try:
                if os.path.exists(album_path):
                    image_files = ImageProcessor.get_image_files(album_path)
                    if image_files and len(image_files) > 0:
                        valid_albums.append({
                            'path': album_path,
                            'name': os.path.basename(album_path),
                            'image_files': image_files,
                            'cover_image': image_files[0],
                            'image_count': len(image_files),
                            'folder_size': ImageProcessor.get_folder_size(image_files)
                        })
            except Exception as e:
                print(f"处理收藏相册时出错 {album_path}: {e}")
                continue
        
        if valid_albums:
            self.albums = valid_albums
            self.album_grid.display_albums(valid_albums)
            self.status_bar.set_status(f"显示 {len(valid_albums)} 个收藏的相册")
            total_images = sum(len(album['image_files']) for album in valid_albums)
            self.status_bar.set_info(f"共 {total_images} 张图片")
            
            # 如果结果很多，提示滚动
            if len(valid_albums) > 10:
                self.status_bar.set_status(f"显示 {len(valid_albums)} 个收藏的相册（支持滚动浏览）")
        else:
            messagebox.showinfo("提示", "收藏的相册都不存在了")
            self.status_bar.set_status("收藏的相册不存在")
    
    def toggle_favorite(self, album_path):
        """切换收藏状态"""
        if self.config_manager.is_favorite(album_path):
            self.config_manager.remove_favorite(album_path)
            self.status_bar.set_status(f"已从收藏中移除: {os.path.basename(album_path)}")
        else:
            self.config_manager.add_favorite(album_path)
            self.status_bar.set_status(f"已添加到收藏: {os.path.basename(album_path)}")
        
        # 刷新当前显示
        if self.albums:
            self.album_grid.display_albums(self.albums)
            
    def open_album(self, folder_path):
        """打开相册查看"""
        try:
            image_files = ImageProcessor.get_image_files(folder_path)
            
            if not image_files:
                messagebox.showinfo("提示", "该文件夹中没有找到图片")
                return
            
            # 添加到最近浏览
            self.config_manager.add_recent_album(folder_path)
                
            # 创建图片查看器窗口
            album_window = Toplevel(self.root)
            album_name = os.path.basename(folder_path)
            album_window.title(f"📸 相册查看器 - {album_name}")
            album_window.geometry("1000x750")
            album_window.minsize(800, 600)
            
            # 设置窗口图标和属性
            album_window.configure(bg='#1D1D1F')
            
            # 居中显示窗口
            album_window.transient(self.root)
            album_window.grab_set()
            
            # 创建图片查看器
            try:
                viewer = ImageViewer(album_window, image_files, self.config_manager)
                
                # 更新主窗口状态
                self.status_bar.set_status(f"已打开相册: {album_name}")
                self.status_bar.set_info(f"{len(image_files)} 张图片")
                
            except Exception as e:
                print(f"创建图片查看器失败: {e}")
                # 创建简单的图片查看器
                self.create_simple_viewer(album_window, image_files, album_name)
            
        except Exception as e:
            messagebox.showerror("错误", f"打开相册时发生错误：{str(e)}")
            self.status_bar.set_status("打开相册失败")
    
    def create_simple_viewer(self, window, image_files, album_name):
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

    def on_closing(self):
        """窗口关闭时保存配置"""
        try:
            # 保存窗口大小
            self.config_manager.config['window_size'] = self.root.geometry()
            self.config_manager.save_config()
        except Exception as e:
            print(f"保存配置时发生错误: {e}")
        finally:
            self.root.destroy()

def main():
    """主函数"""
    try:
        # 创建主窗口
        root = ThemedTk()
        
        # 创建应用程序
        app = PhotoAlbumApp(root)
        
        # 运行主循环
        root.mainloop()
        
    except Exception as e:
        error_msg = f"启动应用程序时发生错误：{e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        
        # 显示错误对话框
        try:
            import tkinter.messagebox
            tkinter.messagebox.showerror("启动错误", f"应用程序启动失败：{str(e)}")
        except:
            pass

if __name__ == "__main__":
    main()