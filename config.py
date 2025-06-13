import os
import json

class ConfigManager:
    """配置管理器，负责处理应用程序配置的读取和保存"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser('~'), '.album_scanner_config.json')
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
        return self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            'last_path': '',
            'zoom_mode': 'fit',
            'theme': 'arc',
            'language': 'zh-CN',
            'slideshow_interval': 3,
            'recent_albums': [],
            'favorites': [],
            'window_size': '1000x700',
            'show_exif': True,
            'auto_rotate': True
        }
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get_last_path(self):
        """获取上次使用的路径"""
        return self.config.get('last_path', '')
    
    def set_last_path(self, path):
        """设置并保存路径"""
        self.config['last_path'] = path
        self.save_config()
    
    def get_zoom_mode(self):
        """获取缩放模式"""
        return self.config.get('zoom_mode', 'fit')
    
    def set_zoom_mode(self, mode):
        """设置缩放模式"""
        self.config['zoom_mode'] = mode
        self.save_config()
    
    def add_recent_album(self, album_path):
        """添加到最近浏览"""
        recent = self.config.get('recent_albums', [])
        if album_path in recent:
            recent.remove(album_path)
        recent.insert(0, album_path)
        self.config['recent_albums'] = recent[:10]  # 保留最近10个
        self.save_config()
    
    def get_recent_albums(self):
        """获取最近浏览的相册"""
        return self.config.get('recent_albums', [])
    
    def add_favorite(self, album_path):
        """添加到收藏"""
        favorites = self.config.get('favorites', [])
        if album_path not in favorites:
            favorites.append(album_path)
            self.config['favorites'] = favorites
            self.save_config()
    
    def remove_favorite(self, album_path):
        """从收藏中移除"""
        favorites = self.config.get('favorites', [])
        if album_path in favorites:
            favorites.remove(album_path)
            self.config['favorites'] = favorites
            self.save_config()
    
    def get_favorites(self):
        """获取收藏的相册"""
        return self.config.get('favorites', [])
    
    def is_favorite(self, album_path):
        """检查是否为收藏"""
        return album_path in self.config.get('favorites', [])
