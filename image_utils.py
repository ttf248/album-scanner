import os
import glob
from PIL import Image, ImageTk

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
                        'cover_image': image_files[0] if image_files else None
                    })
        
        return albums
    
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
    def load_image_with_mode(cls, image_path, window_width, window_height, mode="fit"):
        """根据指定模式加载图片"""
        try:
            img = Image.open(image_path)
            
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
            
            return ImageTk.PhotoImage(img), img.width, img.height
        except Exception as e:
            print(f"无法加载图片 {image_path}: {e}")
            return None, 0, 0
