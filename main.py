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
        
        # 按钮
        tk.Button(top_frame, text="浏览", command=self.browse_folder).pack(side='left', padx=2)
        tk.Button(top_frame, text="扫描", command=self.scan_albums).pack(side='left', padx=2)
        tk.Button(top_frame, text="最近", command=self.show_recent_albums).pack(side='left', padx=2)
        tk.Button(top_frame, text="收藏", command=self.show_favorites).pack(side='left', padx=2)
        
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
            messagebox.showwarning("提示", "请先选择相册文件夹")
            return
            
        # 使用pathlib验证路径
        path_obj = Path(folder_path)
        if not path_obj.exists():
            messagebox.showerror("错误", "所选文件夹不存在")
            return
            
        try:
            # 显示加载状态
            self.root.config(cursor="wait")
            self.status_bar.set_status("正在扫描相册，请稍候...")
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
            
            # 如果相册很多，提示用户可以滚动
            if len(self.albums) > 15:
                messagebox.showinfo("提示", f"找到 {len(self.albums)} 个相册！\n使用鼠标滚轮或拖拽滚动条浏览所有相册。")
            
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
            messagebox.showinfo("提示", "暂无最近浏览的相册")
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
            messagebox.showinfo("提示", "暂无收藏的相册")
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
            album_window.title(f"相册查看器 - {os.path.basename(folder_path)}")
            album_window.geometry("1000x750")
            album_window.minsize(800, 600)
            
            # 创建图片查看器
            ImageViewer(album_window, image_files, self.config_manager)
            
            album_name = os.path.basename(folder_path)
            self.status_bar.set_status(f"已打开相册: {album_name}")
            self.status_bar.set_info(f"{len(image_files)} 张图片")
            
        except Exception as e:
            messagebox.showerror("错误", f"打开相册时发生错误：{str(e)}")
            self.status_bar.set_status("打开相册失败")
    
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