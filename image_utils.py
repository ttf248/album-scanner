import os
import glob
from PIL import Image, ImageTk, ExifTags
import threading
import time

class ImageProcessor:
    """图片处理器，负责图片的扫描、加载和处理"""
    
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']
    
    @classmethod
    def scan_albums(cls, root_path):
        """扫描指定路径下的所有包含图片的文件夹"""
        if not os.path.exists(root_path):
            return []
        
        albums = []
        for root, dirs, files in os.walk(root_path):
            # 检查当前目录是否包含图片文件
            has_images = any(os.path.splitext(file)[1].lower() in cls.IMAGE_EXTENSIONS 
                           for file in files)
            if has_images:
                image_files = cls.get_image_files(root)
                if image_files:
                    albums.append({
                        'path': root,
                        'name': os.path.basename(root),
                        'image_files': image_files,
                        'cover_image': image_files[0] if image_files else None,
                        'image_count': len(image_files),
                        'folder_size': cls.get_folder_size(image_files)
                    })
        
        return albums
    
    @classmethod
    def get_folder_size(cls, image_files):
        """计算文件夹大小"""
        total_size = 0
        for file_path in image_files:
            try:
                total_size += os.path.getsize(file_path)
            except OSError:
                continue
        return cls.format_size(total_size)
    
    @classmethod
    def format_size(cls, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"
    
    @classmethod
    def get_image_files(cls, folder_path):
        """获取文件夹中的所有图片文件"""
        image_files = []
        for ext in cls.IMAGE_EXTENSIONS:
            pattern = os.path.join(folder_path, f'*{ext}')
            image_files.extend(glob.glob(pattern, recursive=False))
            # 同时检查大写扩展名
            pattern_upper = os.path.join(folder_path, f'*{ext.upper()}')
            image_files.extend(glob.glob(pattern_upper, recursive=False))
        
        # 去重并排序
        image_files = list(set(image_files))
        image_files.sort()
        return image_files
    
    @classmethod
    def create_thumbnail(cls, image_path, size=(200, 200)):
        """创建图片缩略图"""
        try:
            img = Image.open(image_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"无法创建缩略图 {image_path}: {e}")
            return None
    
    @classmethod
    def load_image_with_mode(cls, image_path, window_width, window_height, mode="fit", rotation=0):
        """根据指定模式加载图片"""
        try:
            img = Image.open(image_path)
            
            # 自动旋转（基于EXIF）
            img = cls.auto_rotate_image(img)
            
            # 手动旋转
            if rotation != 0:
                img = img.rotate(rotation, expand=True)
            
            original_width, original_height = img.size
            
            if mode == "fit":
                img.thumbnail((window_width - 40, window_height - 40), Image.Resampling.LANCZOS)
            elif mode == "fill":
                img_ratio = img.width / img.height
                win_ratio = (window_width - 40) / (window_height - 40)
                
                if img_ratio > win_ratio:
                    new_height = window_height - 40
                    new_width = int(new_height * img_ratio)
                else:
                    new_width = window_width - 40
                    new_height = int(new_width / img_ratio)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                left = (new_width - (window_width - 40)) // 2
                top = (new_height - (window_height - 40)) // 2
                img = img.crop((left, top, left + window_width - 40, top + window_height - 40))
            # mode == "original" 时不做任何处理
            
            return ImageTk.PhotoImage(img), img.width, img.height, original_width, original_height
        except Exception as e:
            print(f"无法加载图片 {image_path}: {e}")
            return None, 0, 0, 0, 0
    
    @classmethod
    def auto_rotate_image(cls, img):
        """根据EXIF信息自动旋转图片"""
        try:
            exif = img._getexif()
            if exif is not None:
                for tag, value in exif.items():
                    if ExifTags.TAGS.get(tag) == 'Orientation':
                        if value == 3:
                            img = img.rotate(180, expand=True)
                        elif value == 6:
                            img = img.rotate(270, expand=True)
                        elif value == 8:
                            img = img.rotate(90, expand=True)
                        break
        except (AttributeError, KeyError, TypeError):
            pass
        return img
    
    @classmethod
    def get_image_exif(cls, image_path):
        """获取图片EXIF信息"""
        try:
            img = Image.open(image_path)
            exif_data = {}
            
            if hasattr(img, '_getexif'):
                exif = img._getexif()
                if exif is not None:
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
            
            # 添加文件信息
            stat = os.stat(image_path)
            exif_data['文件大小'] = cls.format_size(stat.st_size)
            exif_data['修改时间'] = time.ctime(stat.st_mtime)
            exif_data['图片尺寸'] = f"{img.width}x{img.height}"
            
            return exif_data
        except Exception as e:
            print(f"无法获取EXIF信息 {image_path}: {e}")
            return {}

class SlideshowManager:
    """幻灯片管理器"""
    
    def __init__(self, image_viewer, interval=3):
        self.image_viewer = image_viewer
        self.interval = interval
        self.is_playing = False
        self.timer = None
    
    def start_slideshow(self):
        """开始幻灯片播放"""
        if not self.is_playing:
            self.is_playing = True
            self._next_slide()
    
    def stop_slideshow(self):
        """停止幻灯片播放"""
        self.is_playing = False
        if self.timer:
            self.timer.cancel()
    
    def _next_slide(self):
        """播放下一张"""
        if self.is_playing:
            self.image_viewer.next_image()
            self.timer = threading.Timer(self.interval, self._next_slide)
            self.timer.start()
    
    def set_interval(self, interval):
        """设置播放间隔"""
        self.interval = interval
