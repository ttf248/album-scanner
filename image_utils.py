import os
import glob
import sys
from PIL import Image, ImageTk, ExifTags
from pathlib import Path
import threading
import time

class ImageProcessor:
    """图片处理器，负责图片的扫描、加载和处理"""
    
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']
    
    @classmethod
    def scan_albums(cls, root_path):
        """扫描指定路径下的所有包含图片的文件夹"""
        albums = []
        
        try:
            # 使用pathlib处理路径，更好地支持Unicode
            root_path = Path(root_path)
            
            if not root_path.exists():
                print(f"路径不存在: {root_path}")
                return albums
            
            # 遍历所有子文件夹
            for item in root_path.iterdir():
                if item.is_dir():
                    try:
                        # 获取文件夹中的图片文件
                        image_files = cls.get_image_files(str(item))
                        
                        if image_files:
                            # 计算文件夹大小
                            folder_size = cls.get_folder_size(image_files)
                            
                            album_info = {
                                'path': str(item),
                                'name': item.name,
                                'image_files': image_files,
                                'cover_image': image_files[0],
                                'image_count': len(image_files),
                                'folder_size': folder_size
                            }
                            albums.append(album_info)
                            
                    except Exception as e:
                        print(f"处理文件夹时出错 {item}: {e}")
                        continue
                        
        except Exception as e:
            print(f"扫描根目录时出错 {root_path}: {e}")
            
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
        """获取文件夹中的所有图片文件，支持Unicode路径"""
        image_files = []
        
        try:
            folder_path = Path(folder_path)
            
            if not folder_path.exists():
                return image_files
            
            # 遍历文件夹中的所有文件
            for file_path in folder_path.iterdir():
                if file_path.is_file():
                    # 检查文件扩展名
                    if file_path.suffix.lower() in cls.IMAGE_EXTENSIONS:
                        try:
                            # 验证文件是否可读
                            if file_path.exists() and file_path.stat().st_size > 0:
                                image_files.append(str(file_path))
                        except Exception as e:
                            print(f"检查文件时出错 {file_path}: {e}")
                            continue
                            
        except Exception as e:
            print(f"读取文件夹时出错 {folder_path}: {e}")
            
        # 按文件名排序
        try:
            image_files.sort(key=lambda x: Path(x).name.lower())
        except Exception as e:
            print(f"排序文件时出错: {e}")
            
        return image_files
    
    @classmethod
    def create_thumbnail(cls, image_path, size=(200, 200)):
        """创建图片缩略图，支持Unicode路径"""
        try:
            # 使用pathlib处理路径
            image_path = Path(image_path)
            
            if not image_path.exists():
                print(f"图片文件不存在: {image_path}")
                return None
                
            # 打开图片
            with Image.open(str(image_path)) as img:
                # 自动旋转（基于EXIF）
                img = cls.auto_rotate_image(img)
                
                # 创建缩略图 - 保持宽高比
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 创建白色背景
                background = Image.new('RGB', size, '#F2F2F7')
                
                # 计算居中位置
                x = (size[0] - img.width) // 2
                y = (size[1] - img.height) // 2
                
                # 粘贴图片到背景
                if img.mode == 'RGBA':
                    background.paste(img, (x, y), img)
                else:
                    background.paste(img, (x, y))
                
                return background
                
        except Exception as e:
            print(f"创建缩略图时出错 {image_path}: {e}")
            return None
    
    @classmethod
    def load_image_with_mode(cls, image_path, window_width, window_height, mode="fit", rotation=0):
        """根据指定模式加载图片，支持Unicode路径"""
        try:
            image_path = Path(image_path)
            
            if not image_path.exists():
                print(f"图片文件不存在: {image_path}")
                return None, 0, 0, 0, 0
                
            img = Image.open(str(image_path))
            
            # 自动旋转（基于EXIF）
            img = cls.auto_rotate_image(img)
            
            # 手动旋转
            if rotation != 0:
                img = img.rotate(rotation, expand=True)
            
            original_width, original_height = img.size
            
            if mode == "fit":
                # 适应窗口大小
                img.thumbnail((window_width - 40, window_height - 40), Image.Resampling.LANCZOS)
            elif mode == "fill":
                # 填充窗口
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
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(img)
            return photo, img.width, img.height, original_width, original_height
            
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
