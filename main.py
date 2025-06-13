import tkinter as tk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk
from config import ConfigManager
from image_utils import ImageProcessor
from ui_components import StyleManager, NavigationBar, AlbumGrid, ImageViewer

class PhotoAlbumApp:
    """主应用程序类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("相册扫描器")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.set_theme("arc")
        
        # 初始化管理器
        self.config_manager = ConfigManager()
        
        # 设置样式
        from tkinter import ttk
        self.style = ttk.Style()
        self.style_manager = StyleManager(self.root, self.style)
        
        # 初始化变量
        self.folder_path = self.config_manager.get_last_path()
        self.path_var = tk.StringVar(value=self.folder_path)
        
        # 创建UI组件
        self.create_widgets()
        
    def create_widgets(self):
        """创建UI组件"""
        # 导航栏
        self.nav_bar = NavigationBar(
            self.root, 
            self.browse_folder, 
            self.scan_albums, 
            self.path_var
        )
        
        # 相册网格
        self.album_grid = AlbumGrid(self.root, self.open_album)
        
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
            
    def scan_albums(self):
        """扫描相册"""
        if not self.folder_path:
            messagebox.showwarning("警告", "请先选择相册文件夹")
            return
            
        try:
            # 显示加载状态
            self.root.config(cursor="wait")
            self.root.update()
            
            # 扫描相册
            albums = ImageProcessor.scan_albums(self.folder_path)
            
            if not albums:
                messagebox.showinfo("提示", "未找到包含图片的文件夹")
                return
                
            # 显示相册
            self.album_grid.display_albums(albums)
            
        except Exception as e:
            messagebox.showerror("错误", f"扫描相册时发生错误：{str(e)}")
        finally:
            self.root.config(cursor="")
            
    def open_album(self, folder_path):
        """打开相册查看"""
        try:
            image_files = ImageProcessor.get_image_files(folder_path)
            
            if not image_files:
                messagebox.showinfo("提示", "该文件夹中没有图片")
                return
                
            # 创建图片查看器窗口
            album_window = tk.Toplevel(self.root)
            album_window.title(f"相册 - {os.path.basename(folder_path)}")
            album_window.geometry("900x700")
            album_window.minsize(600, 400)
            
            # 创建图片查看器
            ImageViewer(album_window, image_files)
            
        except Exception as e:
            messagebox.showerror("错误", f"打开相册时发生错误：{str(e)}")

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