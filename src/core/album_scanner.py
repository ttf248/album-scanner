from tkinter import messagebox
from pathlib import Path
from src.utils.image_utils import ImageProcessor

class AlbumScannerService:
    """漫画扫描服务"""
    
    def __init__(self, app):
        self.app = app
    
    def scan_albums(self):
        """扫描漫画"""
        folder_path = self.app.path_var.get().strip()
        if not folder_path:
            messagebox.showwarning("提示", "请先选择漫画文件夹\n\n💡 快捷键提示：\n• Ctrl+O: 选择文件夹\n• F5: 快速扫描")
            return
            
        # 使用pathlib验证路径
        path_obj = Path(folder_path)
        if not path_obj.exists():
            messagebox.showerror("错误", "所选文件夹不存在")
            return
            
        try:
            # 显示加载状态
            self.app.root.config(cursor="wait")
            self.app.status_bar.set_status("正在扫描漫画，请稍候... (按 ESC 可取消)")
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
        """处理未找到漫画的情况"""
        messagebox.showinfo("提示", "在所选文件夹中未找到包含图片的子文件夹")
        self.app.status_bar.set_status("未找到漫画")
        self.app.status_bar.set_info("")
        self.app.album_grid.display_albums([])
        
        # 清除缓存
        self.app.cached_scan_results = None
        self.app.cached_scan_path = None
    
    def _display_scan_results(self):
        """显示扫描结果 - 支持合集、智能分组和相册"""
        self.app.album_grid.display_albums(self.app.albums)
        
        # 统计不同类型的项目
        collections = [item for item in self.app.albums if item.get('type') == 'collection']
        smart_collections = [item for item in self.app.albums if item.get('type') == 'smart_collection']
        albums = [item for item in self.app.albums if item.get('type') == 'album']
        
        # 计算总图片数
        total_images = 0
        for item in self.app.albums:
            if item.get('type') in ['collection', 'smart_collection']:
                total_images += item.get('image_count', 0)
            else:
                total_images += len(item.get('image_files', []))
        
        # 统计各类型中包含的相册数
        collection_albums = sum(item.get('album_count', 0) for item in collections)
        smart_albums = sum(item.get('album_count', 0) for item in smart_collections)
        
        # 使用详细的状态设置方法
        self.app.status_bar.set_detailed_scan_results(
            collections=len(collections),
            smart_collections=len(smart_collections),
            albums=len(albums),
            total_images=total_images,
            collection_albums=collection_albums,
            smart_albums=smart_albums
        )
        
        # 如果项目很多，提示用户可以滚动和使用快捷键
        if len(self.app.albums) > 15:
            tip_text = f"找到 {len(self.app.albums)} 个项目！\n\n"
            
            # 添加功能说明
            if collections or smart_collections:
                tip_text += "📚 功能说明：\n"
                if collections:
                    tip_text += "• 📚 合集：手动创建的相册集合\n"
                if smart_collections:
                    tip_text += "• 🧠 智能分组：基于名称相似度自动分组\n"
                tip_text += "• 点击可查看其中的相册\n\n"
            
            tip_text += ("📋 浏览提示：\n"
                        "• 使用鼠标滚轮浏览所有内容\n"
                        "• 🏠 首页按钮返回扫描结果\n"
                        "• Ctrl+R 查看最近浏览的漫画\n"
                        "• Ctrl+F 管理收藏的漫画\n"
                        "• F5 重新扫描当前文件夹")
            messagebox.showinfo("扫描完成", tip_text)
    
    def _handle_scan_error(self, error):
        """处理扫描错误"""
        error_msg = f"扫描漫画时发生错误：{str(error)}"
        print(error_msg)
        messagebox.showerror("错误", error_msg)
        self.app.status_bar.set_status("扫描失败")
        self.app.status_bar.set_info("")
