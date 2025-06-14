import os
from tkinter import messagebox
from src.utils.image_utils import ImageProcessor

class AlbumFavoritesManager:
    """漫画收藏管理器"""
    
    def __init__(self, app):
        self.app = app
    
    def show_favorites(self):
        """显示收藏的漫画"""
        favorites = self.app.config_manager.get_favorites()
        if not favorites:
            self._show_no_favorites_message()
            return
        
        # 过滤存在的路径
        valid_albums = self._filter_valid_favorites(favorites)
        
        if valid_albums:
            self._display_favorite_albums(valid_albums)
        else:
            messagebox.showinfo("提示", "收藏的漫画都不存在了")
            self.app.status_bar.set_status("收藏的漫画不存在")
    
    def _show_no_favorites_message(self):
        """显示无收藏的消息"""
        messagebox.showinfo("收藏夹", 
            "暂无收藏的漫画\n\n"
            "💡 使用方法：\n"
            "• 在漫画列表中点击 ⭐ 按钮收藏\n"
            "• 使用 Ctrl+F 快速访问收藏夹\n"
            "• 再次点击 ⭐ 按钮可取消收藏")
    
    def _filter_valid_favorites(self, favorites):
        """过滤有效的收藏路径"""
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
                print(f"处理收藏漫画时出错 {album_path}: {e}")
                continue
        return valid_albums
    
    def _display_favorite_albums(self, valid_albums):
        """显示有效的收藏漫画"""
        self.app.albums = valid_albums
        self.app.album_grid.display_albums(valid_albums)
        self.app.status_bar.set_status(f"显示 {len(valid_albums)} 个收藏的漫画")
        total_images = sum(len(album['image_files']) for album in valid_albums)
        self.app.status_bar.set_info(f"共 {total_images} 张图片")
        
        # 如果结果很多，提示滚动
        if len(valid_albums) > 10:
            self.app.status_bar.set_status(f"显示 {len(valid_albums)} 个收藏的漫画（支持滚动浏览）")
