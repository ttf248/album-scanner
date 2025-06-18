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
        """扫描漫画文件夹，支持合集功能"""
        albums = []
        
        try:
            # 使用pathlib处理路径，更好地支持Unicode
            root_path = Path(root_path)
            
            if not root_path.exists():
                print(f"路径不存在: {root_path}")
                return albums
            
            # 扫描根目录的直接子文件夹
            for item in root_path.iterdir():
                if item.is_dir():
                    # 检查这个文件夹是否包含图片（作为单个相册）
                    image_files = cls.get_image_files(str(item))
                    
                    if image_files:
                        # 这是一个包含图片的相册
                        folder_size = cls.get_folder_size(image_files)
                        album_info = {
                            'path': str(item),
                            'name': item.name,
                            'image_files': image_files,
                            'cover_image': image_files[0],
                            'image_count': len(image_files),
                            'folder_size': folder_size,
                            'type': 'album'  # 标记为单个相册
                        }
                        albums.append(album_info)
                    else:
                        # 检查是否包含子相册（作为合集）
                        sub_albums = []
                        cls._scan_folder_recursive(item, sub_albums)
                        
                        if sub_albums:
                            # 这是一个合集，包含多个相册
                            total_images = sum(len(album['image_files']) for album in sub_albums)
                            total_size_bytes = sum(cls._parse_size_to_bytes(album['folder_size']) for album in sub_albums)
                            
                            # 使用第一个相册的第一张图作为合集封面
                            cover_image = sub_albums[0]['cover_image'] if sub_albums else None
                            
                            collection_info = {
                                'path': str(item),
                                'name': item.name,
                                'albums': sub_albums,  # 包含的相册列表
                                'cover_image': cover_image,
                                'album_count': len(sub_albums),
                                'image_count': total_images,
                                'folder_size': cls.format_size(total_size_bytes),
                                'type': 'collection'  # 标记为合集
                            }
                            albums.append(collection_info)
                        
        except Exception as e:
            print(f"扫描根目录时出错 {root_path}: {e}")
            
        return albums
    
    @classmethod
    def _scan_folder_recursive(cls, folder_path, albums):
        """递归扫描文件夹"""
        try:
            for item in folder_path.iterdir():
                if item.is_dir():
                    try:
                        # 获取当前文件夹中的图片文件
                        image_files = cls.get_image_files(str(item))
                        
                        if image_files and len(image_files) > 0:
                            # 计算文件夹大小
                            folder_size = cls.get_folder_size(image_files)
                            
                            # 确保有封面图片
                            cover_image = image_files[0] if image_files else None
                            
                            album_info = {
                                'path': str(item),
                                'name': item.name,
                                'image_files': image_files,
                                'cover_image': cover_image,
                                'image_count': len(image_files),
                                'folder_size': folder_size
                            }
                            albums.append(album_info)
                        
                        # 递归扫描子文件夹
                        cls._scan_folder_recursive(item, albums)
                        
                    except Exception as e:
                        print(f"处理文件夹时出错 {item}: {e}")
                        continue
                        
        except Exception as e:
            print(f"递归扫描文件夹时出错 {folder_path}: {e}")
    
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
    def _parse_size_to_bytes(cls, size_str):
        """将格式化的大小字符串转换回字节数"""
        try:
            if not size_str or size_str == "0B":
                return 0
            
            # 提取数字和单位
            import re
            match = re.match(r'([0-9.]+)([A-Z]+)', size_str.upper())
            if not match:
                return 0
            
            value = float(match.group(1))
            unit = match.group(2)
            
            multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
            return int(value * multipliers.get(unit, 1))
        except Exception:
            return 0
    
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
        """创建缩略图，支持Unicode路径"""
        try:
            # 使用pathlib处理路径
            image_path = Path(image_path)
            
            if not image_path.exists():
                print(f"图片文件不存在: {image_path}")
                return None
                
            # 打开图片
            with Image.open(str(image_path)) as img:
                # 转换为RGB模式（处理RGBA和其他模式）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 创建缩略图 - 保持比例
                img.thumbnail(size, Image.Resampling.LANCZOS)
                return img.copy()
                
        except Exception as e:
            print(f"创建缩略图时出错 {image_path}: {e}")
            return None
    
    @classmethod
    def load_image_with_mode(cls, image_path, window_width, window_height, mode="fit", rotation=0):
        """加载图片并按指定模式调整大小"""
        try:
            image_path = Path(image_path)
            
            if not image_path.exists():
                return None, 0, 0, 0, 0
                
            with Image.open(str(image_path)) as img:
                orig_width, orig_height = img.size
                
                # 转换颜色模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 旋转图片
                if rotation != 0:
                    img = img.rotate(rotation, expand=True)
                
                # 根据模式调整大小
                if mode == "fit":
                    # 适应窗口，保持比例
                    img.thumbnail((window_width, window_height), Image.Resampling.LANCZOS)
                elif mode == "fill":
                    # 填充窗口，可能裁剪
                    ratio = max(window_width/img.width, window_height/img.height)
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                elif mode == "original":
                    # 保持原始大小
                    pass
                
                # 转换为PhotoImage
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(img)
                return photo, img.width, img.height, orig_width, orig_height
                
        except Exception as e:
            print(f"加载图片失败 {image_path}: {e}")
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
        if self.is_playing:
            self.stop_slideshow()
            self.start_slideshow()
    
    def set_interval(self, interval):
        """设置播放间隔"""
        self.interval = interval
