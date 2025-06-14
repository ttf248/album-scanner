import os
import hashlib
import threading
import queue
from pathlib import Path
from PIL import Image, ImageTk
from concurrent.futures import ThreadPoolExecutor
from .logger import get_logger, log_info, log_error, log_exception

class ImageCache:
    """异步图片缓存管理器"""
    
    def __init__(self, cache_dir=None, max_memory_items=100, max_workers=2):
        """初始化缓存管理器
        
        Args:
            cache_dir: 磁盘缓存目录
            max_memory_items: 内存中最大缓存项数
            max_workers: 最大工作线程数
        """
        self.logger = get_logger('image_cache')
        
        # 缓存目录
        if cache_dir is None:
            cache_dir = Path.home() / '.comic_reader' / 'cache'
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 内存缓存 - LRU实现
        self.memory_cache = {}
        self.access_order = []
        self.max_memory_items = max_memory_items
        
        # 异步加载队列
        self.load_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='ImageCache')
        
        # 回调管理
        self.callbacks = {}  # {cache_key: [callback_list]}
        self.loading_set = set()  # 正在加载的项目
        
        # 启动工作线程
        self._start_workers()
        
        log_info(f"图片缓存管理器初始化完成，缓存目录: {self.cache_dir}", 'image_cache')
    
    def _start_workers(self):
        """启动工作线程"""
        for i in range(2):  # 启动2个工作线程
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
    
    def _worker(self):
        """工作线程主循环"""
        while True:
            try:
                task = self.load_queue.get(timeout=1)
                if task is None:  # 退出信号
                    break
                
                self._process_load_task(task)
                self.load_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                log_error(f"工作线程处理任务时出错: {e}", 'image_cache')
    
    def _process_load_task(self, task):
        """处理加载任务"""
        try:
            image_path, size, cache_key = task
            
            # 检查磁盘缓存
            cached_path = self._get_cache_path(cache_key)
            
            if cached_path.exists():
                # 从磁盘缓存加载
                try:
                    with Image.open(cached_path) as img:
                        photo = ImageTk.PhotoImage(img)
                        self._cache_loaded_image(cache_key, photo)
                        return
                except Exception as e:
                    log_error(f"从磁盘缓存加载图片失败: {e}", 'image_cache')
                    # 删除损坏的缓存文件
                    cached_path.unlink(missing_ok=True)
            
            # 从原始文件加载
            self._load_and_cache_image(image_path, size, cache_key, cached_path)
            
        except Exception as e:
            log_exception(f"处理加载任务时出错: {e}", 'image_cache')
            self._notify_load_error(cache_key, e)
        finally:
            self.loading_set.discard(cache_key)
    
    def _load_and_cache_image(self, image_path, size, cache_key, cached_path):
        """加载并缓存图片"""
        try:
            # 安全地加载图片
            with Image.open(image_path) as img:
                # 检查图片尺寸是否合理
                width, height = img.size
                max_pixels = 50 * 1024 * 1024  # 50兆像素
                if width * height > max_pixels:
                    raise ValueError(f"图片尺寸超出限制: {width*height} > {max_pixels}")
                
                # 安全加载图片
                img.load()
                original_img = img.copy()
            
            # 创建缩略图
            thumbnail = original_img.copy()
            thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
            
            # 保存到磁盘缓存
            try:
                thumbnail.save(cached_path, 'PNG', optimize=True)
            except Exception as e:
                log_error(f"保存缓存文件失败: {e}", 'image_cache')
            
            # 创建PhotoImage并缓存到内存
            photo = ImageTk.PhotoImage(thumbnail)
            self._cache_loaded_image(cache_key, photo)
            
        except Exception as e:
            log_error(f"加载图片失败 {image_path}: {e}", 'image_cache')
            self._notify_load_error(cache_key, e)
    
    def _cache_loaded_image(self, cache_key, photo):
        """将加载的图片缓存到内存并通知回调"""
        # 缓存到内存
        self._add_to_memory_cache(cache_key, photo)
        
        # 通知所有等待的回调
        if cache_key in self.callbacks:
            callbacks = self.callbacks.pop(cache_key, [])
            for callback in callbacks:
                try:
                    # 在主线程中执行回调
                    callback[0].after_idle(callback[1], photo)
                except Exception as e:
                    log_error(f"执行回调时出错: {e}", 'image_cache')
    
    def _notify_load_error(self, cache_key, error):
        """通知加载错误"""
        if cache_key in self.callbacks:
            callbacks = self.callbacks.pop(cache_key, [])
            for callback in callbacks:
                try:
                    # 在主线程中执行错误回调
                    if len(callback) > 2 and callback[2]:
                        callback[0].after_idle(callback[2], error)
                except Exception as e:
                    log_error(f"执行错误回调时出错: {e}", 'image_cache')
    
    def _add_to_memory_cache(self, key, value):
        """添加到内存缓存（LRU）"""
        if key in self.memory_cache:
            # 更新访问顺序
            self.access_order.remove(key)
        elif len(self.memory_cache) >= self.max_memory_items:
            # 移除最久未使用的项
            oldest_key = self.access_order.pop(0)
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = value
        self.access_order.append(key)
    
    def _get_from_memory_cache(self, key):
        """从内存缓存获取（更新LRU）"""
        if key in self.memory_cache:
            # 更新访问顺序
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.memory_cache[key]
        return None
    
    def _get_cache_path(self, cache_key):
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.png"
    
    def _generate_cache_key(self, image_path, size):
        """生成缓存键"""
        # 使用文件路径、修改时间和尺寸生成唯一键
        try:
            stat = os.stat(image_path)
            key_data = f"{image_path}_{stat.st_mtime}_{size[0]}x{size[1]}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except Exception:
            # 如果获取文件信息失败，使用路径和尺寸
            key_data = f"{image_path}_{size[0]}x{size[1]}"
            return hashlib.md5(key_data.encode()).hexdigest()
    
    def load_image_async(self, image_path, size, widget, success_callback, error_callback=None):
        """异步加载图片
        
        Args:
            image_path: 图片路径
            size: 目标尺寸 (width, height)
            widget: 用于在主线程中执行回调的widget
            success_callback: 成功回调 callback(photo)
            error_callback: 错误回调 callback(error)
        """
        cache_key = self._generate_cache_key(image_path, size)
        
        # 检查内存缓存
        cached_photo = self._get_from_memory_cache(cache_key)
        if cached_photo:
            # 立即执行回调
            widget.after_idle(success_callback, cached_photo)
            return
        
        # 添加到回调列表
        if cache_key not in self.callbacks:
            self.callbacks[cache_key] = []
        self.callbacks[cache_key].append((widget, success_callback, error_callback))
        
        # 如果还没有开始加载，添加到队列
        if cache_key not in self.loading_set:
            self.loading_set.add(cache_key)
            task = (image_path, size, cache_key)
            self.load_queue.put(task)
    
    def clear_memory_cache(self):
        """清空内存缓存"""
        self.memory_cache.clear()
        self.access_order.clear()
        log_info("内存缓存已清空", 'image_cache')
    
    def clear_disk_cache(self):
        """清空磁盘缓存"""
        try:
            import shutil
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            log_info("磁盘缓存已清空", 'image_cache')
        except Exception as e:
            log_error(f"清空磁盘缓存失败: {e}", 'image_cache')
    
    def get_cache_size(self):
        """获取缓存大小信息"""
        memory_size = len(self.memory_cache)
        disk_size = 0
        disk_files = 0
        
        try:
            for cache_file in self.cache_dir.glob('*.png'):
                disk_files += 1
                disk_size += cache_file.stat().st_size
        except Exception as e:
            log_error(f"计算磁盘缓存大小失败: {e}", 'image_cache')
        
        return {
            'memory_items': memory_size,
            'disk_files': disk_files,
            'disk_size_mb': disk_size / (1024 * 1024)
        }
    
    def shutdown(self):
        """关闭缓存管理器"""
        # 停止工作线程
        for _ in range(2):
            self.load_queue.put(None)
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        log_info("图片缓存管理器已关闭", 'image_cache')

# 全局缓存实例
_global_cache = None

def get_image_cache():
    """获取全局图片缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = ImageCache()
    return _global_cache
