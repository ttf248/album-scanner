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
        return {'last_path': ''}
    
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
