import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import os
from ttkthemes import ThemedTk
from config import ConfigManager
from image_utils import ImageProcessor
from ui_components import StyleManager, NavigationBar, AlbumGrid, ImageViewer, StatusBar

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
        
        # 状态栏
        self.status_bar = StatusBar(self.root)
        
        # 初始状态
        self.status_bar.set_status("欢迎使用相册扫描器")
        
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
            initialdir=self.folder_path if self.folder_path else os.path.expanduser('~')
        )
        if folder_selected:
            self.folder_path = folder_selected
            self.path_var.set(folder_selected)
            self.config_manager.set_last_path(folder_selected)
            self.status_bar.set_status(f"已选择: {os.path.basename(folder_selected)}")
            
    def scan_albums(self):
        """扫描相册"""
        folder_path = self.path_var.get().strip()
        if not folder_path:
            messagebox.showwarning("提示", "请先选择相册文件夹")
            return
            
        if not os.path.exists(folder_path):
            messagebox.showerror("错误", "所选文件夹不存在")
            return
            
        try:
            # 显示加载状态
            self.root.config(cursor="wait")
            self.status_bar.set_status("正在扫描相册，请稍候...")
            self.root.update()
            
            # 执行扫描
            self.albums = ImageProcessor.scan_albums(folder_path)
            
            if not self.albums:
                messagebox.showinfo("提示", "在所选文件夹中未找到包含图片的子文件夹")
                self.status_bar.set_status("未找到相册")
                self.status_bar.set_info("")
                self.album_grid.display_albums([])
                return
                
            # 显示结果
            self.album_grid.display_albums(self.albums)
            total_images = sum(len(album['image_files']) for album in self.albums)
            
            self.status_bar.set_status(f"扫描完成，找到 {len(self.albums)} 个相册")
            self.status_bar.set_info(f"共 {total_images} 张图片")
            
        except Exception as e:
            messagebox.showerror("错误", f"扫描相册时发生错误：{str(e)}")
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
            if os.path.exists(album_path):
                image_files = ImageProcessor.get_image_files(album_path)
                if image_files:
                    valid_albums.append({
                        'path': album_path,
                        'name': os.path.basename(album_path),
                        'image_files': image_files,
                        'cover_image': image_files[0],
                        'image_count': len(image_files),
                        'folder_size': ImageProcessor.get_folder_size(image_files)
                    })
        
        if valid_albums:
            self.albums = valid_albums
            self.album_grid.display_albums(valid_albums)
            self.status_bar.set_status(f"显示 {len(valid_albums)} 个最近浏览的相册")
            total_images = sum(len(album['image_files']) for album in valid_albums)
            self.status_bar.set_info(f"共 {total_images} 张图片")
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
            if os.path.exists(album_path):
                image_files = ImageProcessor.get_image_files(album_path)
                if image_files:
                    valid_albums.append({
                        'path': album_path,
                        'name': os.path.basename(album_path),
                        'image_files': image_files,
                        'cover_image': image_files[0],
                        'image_count': len(image_files),
                        'folder_size': ImageProcessor.get_folder_size(image_files)
                    })
        
        if valid_albums:
            self.albums = valid_albums
            self.album_grid.display_albums(valid_albums)
            self.status_bar.set_status(f"显示 {len(valid_albums)} 个收藏的相册")
            total_images = sum(len(album['image_files']) for album in valid_albums)
            self.status_bar.set_info(f"共 {total_images} 张图片")
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
        print(f"启动应用程序时发生错误：{e}")
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