import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import os
from ttkthemes import ThemedTk
from config import ConfigManager
from image_utils import ImageProcessor
from ui_components import StyleManager, NavigationBar, AlbumGrid, ImageViewer, StatusBar

class PhotoAlbumApp:
    """主应用程序类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("相册扫描器")
        
        # 初始化管理器
        self.config_manager = ConfigManager()
        
        # 设置窗口
        window_size = self.config_manager.config.get('window_size', '1000x700')
        self.root.geometry(window_size)
        self.root.minsize(800, 600)
        self.root.set_theme("arc")
        
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
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        """创建UI组件"""
        # 状态栏
        self.status_bar = StatusBar(self.root)
        
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
        
        # 初始状态
        self.status_bar.set_status("请选择相册路径并扫描")
        
    def browse_folder(self):
        """浏览并选择文件夹"""
        folder_selected = filedialog.askdirectory(
            title="选择相册文件夹",
            initialdir=self.folder_path if self.folder_path else None
        )
        if folder_selected:
            self.folder_path = folder_selected
            self.path_var.set(folder_selected)
            self.config_manager.set_last_path(folder_selected)
            self.status_bar.set_status("已选择路径，点击扫描开始")
            
    def scan_albums(self):
        """扫描相册"""
        if not self.folder_path:
            messagebox.showwarning("警告", "请先选择相册文件夹")
            return
            
        try:
            # 显示加载状态
            self.root.config(cursor="wait")
            self.status_bar.set_status("正在扫描相册...")
            self.root.update()
            
            # 扫描相册
            self.albums = ImageProcessor.scan_albums(self.folder_path)
            
            if not self.albums:
                messagebox.showinfo("提示", "未找到包含图片的文件夹")
                self.status_bar.set_status("未找到相册")
                return
                
            # 显示相册
            self.album_grid.display_albums(self.albums)
            self.status_bar.set_status(f"找到 {len(self.albums)} 个相册")
            self.status_bar.set_info(f"共 {sum(len(album['image_files']) for album in self.albums)} 张图片")
            
        except Exception as e:
            messagebox.showerror("错误", f"扫描相册时发生错误：{str(e)}")
            self.status_bar.set_status("扫描失败")
        finally:
            self.root.config(cursor="")
    
    def show_recent_albums(self):
        """显示最近浏览的相册"""
        recent_albums = self.config_manager.get_recent_albums()
        if not recent_albums:
            messagebox.showinfo("提示", "没有最近浏览的相册")
            return
        
        # 过滤存在的路径并创建相册数据
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
        else:
            messagebox.showinfo("提示", "最近浏览的相册都不存在了")
    
    def show_favorites(self):
        """显示收藏的相册"""
        favorites = self.config_manager.get_favorites()
        if not favorites:
            messagebox.showinfo("提示", "没有收藏的相册")
            return
        
        # 过滤存在的路径并创建相册数据
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
        else:
            messagebox.showinfo("提示", "收藏的相册都不存在了")
    
    def toggle_favorite(self, album_path):
        """切换收藏状态"""
        if self.config_manager.is_favorite(album_path):
            self.config_manager.remove_favorite(album_path)
            self.status_bar.set_status("已从收藏中移除")
        else:
            self.config_manager.add_favorite(album_path)
            self.status_bar.set_status("已添加到收藏")
        
        # 刷新当前显示
        if self.albums:
            self.album_grid.display_albums(self.albums)
            
    def open_album(self, folder_path):
        """打开相册查看"""
        try:
            image_files = ImageProcessor.get_image_files(folder_path)
            
            if not image_files:
                messagebox.showinfo("提示", "该文件夹中没有图片")
                return
            
            # 添加到最近浏览
            self.config_manager.add_recent_album(folder_path)
                
            # 创建图片查看器窗口
            album_window = Toplevel(self.root)
            album_window.title(f"相册 - {os.path.basename(folder_path)}")
            album_window.geometry("900x700")
            album_window.minsize(600, 400)
            
            # 创建图片查看器
            ImageViewer(album_window, image_files, self.config_manager)
            
            self.status_bar.set_status(f"打开相册: {os.path.basename(folder_path)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"打开相册时发生错误：{str(e)}")
    
    def on_closing(self):
        """窗口关闭时保存配置"""
        # 保存窗口大小
        self.config_manager.config['window_size'] = self.root.geometry()
        self.config_manager.save_config()
        self.root.destroy()

def main():
    """主函数"""
    try:
        root = ThemedTk()
        app = PhotoAlbumApp(root)
        root.mainloop()
    except Exception as e:
        print(f"启动应用程序时发生错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()