import os
from tkinter import messagebox
from src.utils.image_utils import ImageProcessor

class AlbumHistoryManager:
    """漫画历史记录管理器"""
    
    def __init__(self, app):
        self.app = app
    
    def show_recent_albums(self):
        """显示最近浏览的漫画"""
        recent_albums = self.app.config_manager.get_recent_albums()
        if not recent_albums:
            self._show_no_recent_message()
            return
        
        # 过滤存在的路径
        valid_albums = self._filter_valid_albums(recent_albums)
        
        if valid_albums:
            self._display_recent_albums(valid_albums)
        else:
            messagebox.showinfo("提示", "最近浏览的漫画都不存在了")
            self.app.status_bar.set_status("最近浏览的漫画不存在")
    
    def _show_no_recent_message(self):
        """显示无最近记录的消息"""
        messagebox.showinfo("最近浏览", 
            "暂无最近浏览的漫画\n\n"
            "💡 提示：\n"
            "• 打开任何漫画后会自动记录\n"
            "• 使用 Ctrl+R 快速访问最近浏览\n"
            "• 使用 Ctrl+F 管理收藏的漫画")
    
    def _filter_valid_albums(self, recent_albums):
        """过滤有效的漫画路径"""
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
                print(f"处理最近漫画时出错 {album_path}: {e}")
                continue
        return valid_albums
    
    def _display_recent_albums(self, valid_albums):
        """显示有效的最近漫画"""
        self.app.albums = valid_albums
        self.app.album_grid.display_albums(valid_albums)
        self.app.status_bar.set_status(f"显示 {len(valid_albums)} 个最近浏览的漫画")
        total_images = sum(len(album['image_files']) for album in valid_albums)
        self.app.status_bar.set_info(f"共 {total_images} 张图片")
        
        # 如果结果很多，提示滚动
        if len(valid_albums) > 10:
            self.app.status_bar.set_status(f"显示 {len(valid_albums)} 个最近浏览的漫画（支持滚动浏览）")
