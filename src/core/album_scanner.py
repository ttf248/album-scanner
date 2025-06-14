from tkinter import messagebox
from pathlib import Path
from src.utils.image_utils import ImageProcessor

class AlbumScannerService:
    """相册扫描服务"""
    
    def __init__(self, app):
        self.app = app
    
    def scan_albums(self):
        """扫描相册"""
        folder_path = self.app.path_var.get().strip()
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
            self.app.root.config(cursor="wait")
            self.app.status_bar.set_status("正在扫描相册，请稍候... (按 ESC 可取消)")
            self.app.root.update()
            
            # 执行扫描
            self.app.albums = ImageProcessor.scan_albums(str(path_obj))
            
            if not self.app.albums:
                self._handle_no_albums_found()
                return
                
            # 显示结果
            self._display_scan_results()
            
        except Exception as e:
            self._handle_scan_error(e)
        finally:
            self.app.root.config(cursor="")
    
    def _handle_no_albums_found(self):
        """处理未找到相册的情况"""
        messagebox.showinfo("提示", "在所选文件夹中未找到包含图片的子文件夹")
        self.app.status_bar.set_status("未找到相册")
        self.app.status_bar.set_info("")
        self.app.album_grid.display_albums([])
    
    def _display_scan_results(self):
        """显示扫描结果"""
        self.app.album_grid.display_albums(self.app.albums)
        total_images = sum(len(album['image_files']) for album in self.app.albums)
        
        # 显示扫描结果统计
        if len(self.app.albums) > 10:
            self.app.status_bar.set_status(f"扫描完成，找到 {len(self.app.albums)} 个相册（支持滚动浏览）")
        else:
            self.app.status_bar.set_status(f"扫描完成，找到 {len(self.app.albums)} 个相册")
        self.app.status_bar.set_info(f"共 {total_images} 张图片")
        
        # 如果相册很多，提示用户可以滚动和使用快捷键
        if len(self.app.albums) > 15:
            messagebox.showinfo("扫描完成", 
                f"找到 {len(self.app.albums)} 个相册！\n\n"
                "📋 浏览提示：\n"
                "• 使用鼠标滚轮浏览所有相册\n"
                "• Ctrl+R 查看最近浏览的相册\n"
                "• Ctrl+F 管理收藏的相册\n"
                "• F5 重新扫描当前文件夹")
    
    def _handle_scan_error(self, error):
        """处理扫描错误"""
        error_msg = f"扫描相册时发生错误：{str(error)}"
        print(error_msg)
        messagebox.showerror("错误", error_msg)
        self.app.status_bar.set_status("扫描失败")
        self.app.status_bar.set_info("")
