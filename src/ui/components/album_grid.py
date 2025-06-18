import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Toplevel
import os
import subprocess
import platform
from ...utils.image_utils import ImageProcessor, SlideshowManager
from ...utils.image_cache import get_image_cache
from PIL import Image, ImageTk
import threading
from concurrent.futures import ThreadPoolExecutor
from .style_manager import StyleManager, get_safe_font
from .status_bar import StatusBar


class AlbumGrid:
    """现代化漫画网格组件 - 卡片式瀑布流布局"""
    
    def __init__(self, parent, open_callback, favorite_callback, style_manager=None):
        self.parent = parent
        self.open_callback = open_callback
        self.favorite_callback = favorite_callback
        self.is_favorite = None  # 由外部设置
        self.nav_bar = None  # 导航栏引用
        
        # 使用传入的样式管理器或创建新实例
        if style_manager:
            self.style_manager = style_manager
        else:
            from tkinter import ttk
            style = ttk.Style()
            self.style_manager = StyleManager(parent, style)
        
        # 使用全局图片缓存
        self.image_cache = get_image_cache()
        
        # 防抖动布局参数
        self.layout_timer = None
        self.layout_delay = 300  # 300ms防抖
        
        # 现代化布局参数 - 优化为更大的卡片和瀑布流
        self.columns = 2  # 默认列数，会根据窗口大小动态调整
        self.card_width = 400  # 增大卡片宽度
        self.card_spacing = 20  # 增大间距
        self.card_padding = 20  # 增大内边距
        self.min_columns = 1   # 最小列数
        self.max_columns = 6   # 最大列数
        
        # 右键菜单
        self.context_menu = None
        self.current_album_path = None  # 当前右键点击的相册路径
        
        # 确保初始化grid_frame
        self.grid_frame = None
        self.canvas = None
        self.scrollbar = None
        self.scrollable_frame = None
        self.create_widgets()
        self.create_empty_state()
        self._create_context_menu()
    
    def _create_context_menu(self):
        """创建右键菜单"""
        try:
            self.context_menu = tk.Menu(self.parent, tearoff=0)
            
            # 添加菜单项 - 注意索引顺序
            self.context_menu.add_command(
                label="📂 打开相册", 
                command=self._open_album_from_menu
            )
            self.context_menu.add_command(
                label="📁 打开所在文件夹", 
                command=self._open_folder_from_menu
            )
            self.context_menu.add_separator()  # 索引 2
            self.context_menu.add_command(   # 索引 3
                label="⭐ 添加/移除收藏", 
                command=self._toggle_favorite_from_menu
            )
            self.context_menu.add_separator()  # 索引 4
            self.context_menu.add_command(   # 索引 5
                label="📋 复制路径", 
                command=self._copy_path_from_menu
            )
            self.context_menu.add_command(   # 索引 6
                label="🔍 显示属性", 
                command=self._show_album_properties
            )
            
            print("右键菜单创建成功")
            
        except Exception as e:
            print(f"创建右键菜单失败: {e}")
    
    def _open_album_from_menu(self):
        """从右键菜单打开相册"""
        if self.current_album_path and self.open_callback:
            self.open_callback(self.current_album_path)
    
    def _open_folder_from_menu(self):
        """从右键菜单打开所在文件夹"""
        if self.current_album_path:
            self._open_folder_in_explorer(self.current_album_path)
    
    def _toggle_favorite_from_menu(self):
        """从右键菜单切换收藏状态"""
        if self.current_album_path and self.favorite_callback:
            self.favorite_callback(self.current_album_path)
    
    def _copy_path_from_menu(self):
        """从右键菜单复制路径"""
        if self.current_album_path:
            try:
                self.parent.clipboard_clear()
                self.parent.clipboard_append(self.current_album_path)
                # 显示提示
                if hasattr(self, 'status_callback'):
                    self.status_callback(f"路径已复制: {os.path.basename(self.current_album_path)}")
                print(f"路径已复制到剪贴板: {self.current_album_path}")
            except Exception as e:
                print(f"复制路径失败: {e}")
                messagebox.showerror("错误", f"复制路径失败: {str(e)}")
    
    def _show_album_properties(self):
        """显示相册属性"""
        if not self.current_album_path:
            return
        
        try:
            # 获取相册信息
            album_name = os.path.basename(self.current_album_path)
            image_files = ImageProcessor.get_image_files(self.current_album_path)
            
            # 计算文件夹大小
            total_size = 0
            for image_file in image_files:
                try:
                    total_size += os.path.getsize(image_file)
                except:
                    continue
            
            size_mb = total_size / (1024 * 1024)
            
            # 获取文件夹创建和修改时间
            try:
                stat_info = os.stat(self.current_album_path)
                import time
                created_time = time.ctime(stat_info.st_ctime)
                modified_time = time.ctime(stat_info.st_mtime)
            except:
                created_time = "未知"
                modified_time = "未知"
            
            # 构建属性信息
            properties_text = f"""相册属性信息

相册名称: {album_name}
完整路径: {self.current_album_path}

图片信息:
• 图片数量: {len(image_files)} 张
• 文件夹大小: {size_mb:.1f} MB

时间信息:
• 创建时间: {created_time}
• 修改时间: {modified_time}

收藏状态: {'已收藏' if self.is_favorite and self.is_favorite(self.current_album_path) else '未收藏'}"""
            
            # 显示属性对话框
            messagebox.showinfo(f"相册属性 - {album_name}", properties_text)
            
        except Exception as e:
            print(f"显示相册属性失败: {e}")
            messagebox.showerror("错误", f"无法获取相册属性: {str(e)}")
    
    def _open_folder_in_explorer(self, folder_path):
        """在文件管理器中打开文件夹"""
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows系统使用explorer
                subprocess.run(['explorer', '/select,', folder_path], check=False)
            elif system == "Darwin":  # macOS
                # macOS系统使用open
                subprocess.run(['open', '-R', folder_path], check=False)
            elif system == "Linux":
                # Linux系统尝试使用不同的文件管理器
                file_managers = ['nautilus', 'dolphin', 'thunar', 'pcmanfm', 'caja']
                opened = False
                
                for fm in file_managers:
                    try:
                        subprocess.run([fm, folder_path], check=True)
                        opened = True
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                
                if not opened:
                    # 如果所有文件管理器都失败，尝试用xdg-open
                    subprocess.run(['xdg-open', folder_path], check=False)
            else:
                # 其他系统，尝试通用方法
                subprocess.run(['xdg-open', folder_path], check=False)
            
            print(f"已在文件管理器中打开: {folder_path}")
            
        except Exception as e:
            print(f"打开文件夹失败: {e}")
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")
    
    def _show_context_menu(self, event, album_path):
        """显示右键菜单"""
        try:
            self.current_album_path = album_path
            print(f"右键点击相册: {os.path.basename(album_path)}")
            
            # 更新收藏菜单项状态 - 修正索引为3
            if self.is_favorite and self.is_favorite(album_path):
                self.context_menu.entryconfig(3, label="⭐ 移除收藏")
            else:
                self.context_menu.entryconfig(3, label="☆ 添加收藏")
            
            # 显示菜单
            self.context_menu.post(event.x_root, event.y_root)
            print(f"右键菜单已显示在位置: ({event.x_root}, {event.y_root})")
            
        except Exception as e:
            print(f"显示右键菜单失败: {e}")
            import traceback
            traceback.print_exc()

    def create_widgets(self):
        """创建现代化网格组件"""
        try:
            # 主容器 - 使用现代化背景
            self.grid_frame = tk.Frame(self.parent, bg=self.style_manager.colors['bg_primary'])
            self.grid_frame.pack(fill='both', expand=True, padx=16, pady=(8, 16))
            
            # 创建Canvas和现代化滚动条
            self.canvas = tk.Canvas(self.grid_frame, 
                                  bg=self.style_manager.colors['bg_primary'], 
                                  highlightthickness=0,
                                  relief='flat')
            
            # 现代化滚动条样式
            style = ttk.Style()
            style.configure('Modern.Vertical.TScrollbar',
                           background=self.style_manager.colors['scrollbar_bg'],
                           troughcolor=self.style_manager.colors['scrollbar_bg'],
                           borderwidth=0,
                           arrowcolor=self.style_manager.colors['scrollbar_thumb'],
                           darkcolor=self.style_manager.colors['scrollbar_thumb'],
                           lightcolor=self.style_manager.colors['scrollbar_thumb'])
            
            self.scrollbar = ttk.Scrollbar(self.grid_frame, 
                                         orient='vertical', 
                                         command=self.canvas.yview,
                                         style='Modern.Vertical.TScrollbar')
            
            self.scrollable_frame = tk.Frame(self.canvas, bg=self.style_manager.colors['bg_primary'])
            
            # 配置滚动
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            )
            
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            # 布局Canvas和滚动条
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")
            
            # 绑定鼠标滚轮事件 - 改进滚动体验
            self._bind_mousewheel()
            
            # 绑定窗口大小变化事件 - 实现响应式瀑布流（使用防抖）
            self._bind_resize_events()
            
        except Exception as e:
            print(f"创建AlbumGrid组件时出错: {e}")
            # 创建一个基本的框架作为备用
            self.grid_frame = tk.Frame(self.parent, bg='white')
            self.grid_frame.pack(fill='both', expand=True)
            
            # 显示错误信息
            error_label = tk.Label(self.grid_frame, text="界面初始化失败，使用简化模式", 
                                 bg='white', fg='red')
            error_label.pack(expand=True)
    
    def _bind_mousewheel(self):
        """绑定鼠标滚轮事件"""
        def _on_mousewheel(event):
            if self.canvas:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            if self.canvas:
                self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            if self.canvas:
                self.canvas.unbind_all("<MouseWheel>")
        
        if self.canvas:
            self.canvas.bind('<Enter>', _bind_to_mousewheel)
            self.canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def _bind_resize_events(self):
        """绑定窗口大小变化事件 - 使用防抖"""
        def _on_canvas_resize(event):
            # 取消之前的定时器
            if self.layout_timer:
                self.parent.after_cancel(self.layout_timer)
            
            # 设置新的防抖定时器
            self.layout_timer = self.parent.after(self.layout_delay, self._relayout_albums)
        
        if self.canvas:
            self.canvas.bind('<Configure>', _on_canvas_resize)
    
    def _relayout_albums(self):
        """重新布局漫画卡片（防抖后执行）"""
        try:
            self.layout_timer = None  # 清除定时器引用
            if hasattr(self, 'albums') and self.albums:
                self._create_modern_album_cards(self.albums)
        except Exception as e:
            print(f"重新布局漫画时出错: {e}")
    
    def create_empty_state(self):
        """创建空状态引导页面"""
        self.empty_frame = tk.Frame(self.scrollable_frame, bg=self.style_manager.colors['bg_primary'])
        
        # 空状态容器
        empty_container = tk.Frame(self.empty_frame, 
                                 bg=self.style_manager.colors['card_bg'],
                                 relief='flat',
                                 bd=1)
        empty_container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # 内容区域
        content_area = tk.Frame(empty_container, bg=self.style_manager.colors['card_bg'])
        content_area.pack(fill='both', expand=True, padx=60, pady=60)
        
        # 图标
        icon_label = tk.Label(content_area, 
                            text="📸",
                            font=self.style_manager.fonts['title'],
                            bg=self.style_manager.colors['card_bg'],
                            fg=self.style_manager.colors['accent'])
        icon_label.pack(pady=(0, 20))
        
        # 主标题
        title_label = tk.Label(content_area,
                             text="欢迎使用漫画扫描器",
                             font=self.style_manager.fonts['heading'],
                             bg=self.style_manager.colors['card_bg'],
                             fg=self.style_manager.colors['text_primary'])
        title_label.pack(pady=(0, 12))
        
        # 副标题
        subtitle_label = tk.Label(content_area,
                                text="现代化的图片管理工具，让您的漫画井然有序",
                                font=self.style_manager.fonts['body'],
                                bg=self.style_manager.colors['card_bg'],
                                fg=self.style_manager.colors['text_secondary'])
        subtitle_label.pack(pady=(0, 30))
        
        # 操作步骤
        steps_frame = tk.Frame(content_area, bg=self.style_manager.colors['card_bg'])
        steps_frame.pack(fill='x', pady=(0, 30))
        
        steps = [
            ("1️⃣", "选择文件夹", "点击\"选择文件夹\"按钮或按 Ctrl+O"),
            ("2️⃣", "扫描漫画", "点击\"扫描漫画\"按钮或按 Ctrl+S 开始扫描"),
            ("3️⃣", "浏览管理", "在卡片视图中浏览和管理您的漫画")
        ]
        
        for icon, title, desc in steps:
            step_frame = tk.Frame(steps_frame, bg=self.style_manager.colors['card_bg'])
            step_frame.pack(fill='x', pady=8)
            
            # 步骤图标
            step_icon = tk.Label(step_frame,
                               text=icon,
                               font=self.style_manager.fonts['subheading'],
                               bg=self.style_manager.colors['card_bg'])
            step_icon.pack(side='left', padx=(0, 12))
            
            # 步骤内容
            step_content = tk.Frame(step_frame, bg=self.style_manager.colors['card_bg'])
            step_content.pack(side='left', fill='x', expand=True)
            
            step_title = tk.Label(step_content,
                                text=title,
                                font=self.style_manager.fonts['body_medium'],
                                bg=self.style_manager.colors['card_bg'],
                                fg=self.style_manager.colors['text_primary'],
                                anchor='w')
            step_title.pack(fill='x')
            
            step_desc = tk.Label(step_content,
                               text=desc,
                               font=self.style_manager.fonts['caption'],
                               bg=self.style_manager.colors['card_bg'],
                               fg=self.style_manager.colors['text_secondary'],
                               anchor='w')
            step_desc.pack(fill='x')
        
        # 快速开始按钮
        quick_start_frame = tk.Frame(content_area, bg=self.style_manager.colors['card_bg'])
        quick_start_frame.pack(pady=(20, 0))
        
        start_btn_style = self.style_manager.get_button_style('primary')
        start_btn = tk.Button(quick_start_frame,
                            text="🚀 快速开始",
                            command=self.quick_start,
                            **start_btn_style,
                            padx=24,
                            pady=12)
        start_btn.pack()
        
        self.style_manager.create_hover_effect(
            start_btn,
            self.style_manager.colors['button_primary_hover'],
            self.style_manager.colors['button_primary']
        )
        
        # 移除 tooltip
        
        # 默认显示空状态
        self.show_empty_state()
    
    def quick_start(self):
        """快速开始 - 触发选择文件夹"""
        if hasattr(self.parent, 'browse_folder'):
            self.parent.browse_folder()
        elif self.nav_bar and hasattr(self.nav_bar, 'browse_callback'):
            self.nav_bar.browse_callback()
    
    def show_empty_state(self):
        """显示空状态"""
        # 显示空状态
        self.empty_frame.pack(fill='both', expand=True)
    
    def hide_empty_state(self):
        """隐藏空状态"""
        self.empty_frame.pack_forget()
    
    def _show_empty_state(self):
        """显示空状态（兼容旧方法）"""
        self.show_empty_state()
    
    def display_albums(self, albums):
        """显示漫画（兼容性方法）"""
        self.update_albums(albums)
    
    def update_albums(self, albums):
        """更新漫画显示"""
        try:
            self.albums = albums
            
            print(f"AlbumGrid.update_albums 被调用，albums数量: {len(albums) if albums else 0}")
            
            # 清除现有显示
            if self.scrollable_frame:
                for widget in self.scrollable_frame.winfo_children():
                    widget.destroy()
            
            if not albums:
                print("没有漫画数据，显示空状态")
                self.show_empty_state()
                return
            
            # 隐藏空状态
            self.hide_empty_state()
            
            # 启动封面预加载
            self._start_cover_preload(albums)
            
            # 创建现代化漫画卡片
            self._create_modern_album_cards(albums)
            
        except Exception as e:
            print(f"更新漫画显示时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _start_cover_preload(self, albums):
        """启动封面预加载"""
        try:
            if not albums:
                return
            
            # 提取相册路径
            album_paths = [album.get('path') for album in albums if album.get('path')]
            
            if album_paths:
                # 延迟启动预加载，避免阻塞UI创建
                self.parent.after(500, lambda: self._preload_covers(album_paths))
                print(f"计划预加载 {len(album_paths)} 个相册的封面")
                
        except Exception as e:
            print(f"启动封面预加载失败: {e}")
    
    def _preload_covers(self, album_paths):
        """执行封面预加载"""
        try:
            # 分批预加载，避免一次性加载太多
            batch_size = 10
            current_batch = album_paths[:batch_size]
            remaining_paths = album_paths[batch_size:]
            
            # 预加载当前批次
            self.image_cache.preload_album_covers(
                current_batch, 
                size=(320, 350), 
                widget=self.parent
            )
            
            # 如果还有剩余，安排下一批预加载
            if remaining_paths:
                self.parent.after(2000, lambda: self._preload_covers(remaining_paths))
                print(f"预加载了 {len(current_batch)} 个封面，剩余 {len(remaining_paths)} 个")
            else:
                print("所有封面预加载完成")
                
        except Exception as e:
            print(f"执行封面预加载失败: {e}")

    def _load_cover_async(self, album_path, cover_label):
        """异步加载封面图片 - 使用新的缓存系统"""
        try:
            # 查找漫画中的第一张图片
            import glob
            image_files = []
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                pattern = os.path.join(album_path, f'*{ext}')
                image_files.extend(glob.glob(pattern))
                pattern = os.path.join(album_path, f'*{ext.upper()}')
                image_files.extend(glob.glob(pattern))
            
            if not image_files:
                # 没有图片时显示文件夹图标
                cover_label.configure(
                    text='📁\n空漫画', 
                    font=self.style_manager.fonts['body'],
                    fg=self.style_manager.colors['text_tertiary']
                )
                return
            
            # 按文件名排序，取第一张
            image_files.sort()
            first_image = image_files[0]
            
            # 使用缓存系统异步加载
            target_size = (210, 280)  # 3:4 竖屏比例
            
            def on_success(photo):
                """加载成功回调"""
                try:
                    if cover_label.winfo_exists():
                        cover_label.configure(image=photo, text='')
                        cover_label.image = photo  # 保持引用
                except Exception as e:
                    print(f"更新封面图片失败: {e}")
            
            def on_error(error):
                """加载失败回调"""
                try:
                    if cover_label.winfo_exists():
                        cover_label.configure(
                            text='❌\n加载失败', 
                            font=self.style_manager.fonts['body'],
                            fg=self.style_manager.colors['error']
                        )
                except Exception as e:
                    print(f"更新错误状态失败: {e}")
            
            # 异步加载图片
            self.image_cache.load_image_async(
                first_image, 
                target_size, 
                cover_label, 
                on_success, 
                on_error
            )
                        
        except Exception as e:
            print(f"启动封面加载失败: {e}")
            try:
                cover_label.configure(
                    text='❌\n加载失败', 
                    font=self.style_manager.fonts['body'],
                    fg=self.style_manager.colors['error']
                )
            except:
                pass
    
    def _load_cover_image(self, album_path, callback, size=(320, 350)):
        """异步加载封面图片 - 重构为使用新缓存系统"""
        try:
            # 查找漫画中的第一张图片作为封面
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
            
            image_file = None
            for file in os.listdir(album_path):
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_file = os.path.join(album_path, file)
                    break
            
            if not image_file:
                callback(None)
                return
            
            def on_success(photo):
                callback(photo)
            
            def on_error(error):
                print(f"加载封面失败 {album_path}: {error}")
                callback(None)
            
            # 使用缓存系统异步加载 - 需要一个widget来执行回调
            # 这里使用parent作为widget
            self.image_cache.load_image_async(
                image_file,
                size,
                self.parent,
                on_success,
                on_error
            )
                
        except Exception as e:
            print(f"查找封面图片失败 {album_path}: {e}")
            callback(None)
    
    def _load_specific_cover_image(self, image_path, callback, size=(320, 350)):
        """加载指定的封面图片"""
        try:
            if not image_path or not os.path.exists(image_path):
                callback(None)
                return
            
            def on_success(photo):
                callback(photo)
            
            def on_error(error):
                print(f"加载指定封面失败 {image_path}: {error}")
                callback(None)
            
            # 使用缓存系统异步加载
            self.image_cache.load_image_async(
                image_path,
                size,
                self.parent,
                on_success,
                on_error
            )
                
        except Exception as e:
            print(f"加载指定封面图片失败 {image_path}: {e}")
            callback(None)
    
    def _open_collection(self, collection):
        """打开合集，显示合集内的相册列表"""
        try:
            albums = collection.get('albums', [])
            if not albums:
                print("合集中没有相册")
                return
            
            # 更新当前显示的相册列表为合集内的相册
            self.albums = albums
            self._create_modern_album_cards(albums)
            
            # 如果有导航栏，更新导航状态
            if hasattr(self, 'nav_bar') and self.nav_bar:
                collection_name = collection.get('name', '未知合集')
                # 这里可以添加面包屑导航或返回按钮的逻辑
                print(f"进入合集: {collection_name}")
            
        except Exception as e:
            print(f"打开合集失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_modern_album_cards(self, albums):
        """创建现代化漫画卡片 - 优化性能"""
        try:
            if not self.scrollable_frame:
                return
            
            # 计算响应式列数 - 基于固定卡片宽度420px
            canvas_width = self.canvas.winfo_width()
            if canvas_width > 1:
                # 根据固定卡片宽度420和间距计算最佳列数
                available_width = canvas_width - (self.card_spacing * 2)  # 减去左右边距
                card_total_width = 420 + self.card_spacing
                calculated_columns = max(self.min_columns, available_width // card_total_width)
                self.columns = min(self.max_columns, calculated_columns)
            else:
                # 窗口尚未完全初始化时使用默认值
                self.columns = 2
            
            # 清空现有内容 - 批量操作减少重绘
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            # 创建网格容器
            grid_container = tk.Frame(self.scrollable_frame, bg=self.style_manager.colors['bg_primary'])
            grid_container.pack(fill='both', expand=True, padx=self.card_spacing, pady=self.card_spacing)
            
            # 批量创建卡片 - 减少单次操作
            cards_to_create = []
            for i, album in enumerate(albums):
                try:
                    # 验证漫画数据完整性
                    if not isinstance(album, dict):
                        continue
                        
                    album_name = album.get('name', '未知漫画')
                    image_count = album.get('image_count', 0)
                    album_path = album.get('path', '')
                    
                    if not album_path:
                        continue
                    
                    row = i // self.columns
                    col = i % self.columns
                    
                    cards_to_create.append((i, album, row, col))
                        
                except Exception as e:
                    print(f"准备漫画项时出错 {i}: {e}")
                    continue
            
            # 分批创建卡片，减少UI阻塞
            self._create_cards_batch(grid_container, cards_to_create, 0)
                
        except Exception as e:
            print(f"创建漫画卡片时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_cards_batch(self, grid_container, cards_to_create, start_index, batch_size=5):
        """分批创建卡片，避免UI阻塞"""
        try:
            end_index = min(start_index + batch_size, len(cards_to_create))
            
            for i in range(start_index, end_index):
                album_index, album, row, col = cards_to_create[i]
                
                card = self._create_modern_album_card(grid_container, album)
                card.grid(row=row, column=col, 
                         padx=self.card_spacing//2, 
                         pady=self.card_spacing//2, 
                         sticky='nsew')
            
            # 如果还有更多卡片要创建，安排下一批
            if end_index < len(cards_to_create):
                self.parent.after(10, lambda: self._create_cards_batch(
                    grid_container, cards_to_create, end_index, batch_size))
            else:
                # 所有卡片创建完成，配置网格权重
                for i in range(self.columns):
                    grid_container.grid_columnconfigure(i, weight=1)
                
                # 更新滚动区域
                self.scrollable_frame.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
        except Exception as e:
            print(f"分批创建卡片时出错: {e}")
    
    def _create_modern_album_card(self, parent, album):
        """创建现代化单个漫画卡片 - 支持合集和相册"""
        try:
            album_path = album['path']
            album_name = album['name']
            album_type = album.get('type', 'album')  # 'album' 或 'collection'
            
            # 根据类型获取不同的信息
            if album_type == 'collection':
                # 合集信息
                album_count = album.get('album_count', 0)
                image_count = album.get('image_count', 0)
                display_text = f'{album_count} 个相册'
                icon = '📚'  # 合集图标
            else:
                # 单个相册信息
                image_count = album.get('image_count', 0)
                display_text = f'{image_count} 张图片'
                icon = '🖼️'  # 相册图标
            
            # 卡片主容器 - 固定尺寸420x560
            card = tk.Frame(parent, 
                          bg=self.style_manager.colors['card_bg'],
                          relief='flat',
                          bd=1,
                          highlightthickness=0,
                          width=420,
                          height=560)
            card.pack_propagate(False)  # 禁止子组件改变卡片大小
            
            # 绑定右键菜单到卡片 - 使用更强的绑定
            def show_menu(event):
                print(f"卡片右键事件触发: {album_path}")
                self._show_context_menu(event, album_path)
                return "break"  # 阻止事件继续传播
            
            card.bind("<Button-3>", show_menu)
            
            # 添加卡片悬浮效果
            self.style_manager.create_hover_effect(
                card,
                self.style_manager.colors['card_hover'],
                self.style_manager.colors['card_bg']
            )
            
            # 封面区域 - 适应420x560卡片尺寸
            cover_frame = tk.Frame(card, 
                                 bg=self.style_manager.colors['card_bg'], 
                                 height=350)
            cover_frame.pack(fill='x', padx=self.card_padding, pady=(self.card_padding, 8))
            cover_frame.pack_propagate(False)
            
            # 封面图片容器
            cover_container = tk.Frame(cover_frame, 
                                     bg=self.style_manager.colors['bg_tertiary'],
                                     relief='flat')
            cover_container.pack(fill='both', expand=True)
            
            # 绑定右键菜单到封面容器
            cover_container.bind("<Button-3>", show_menu)
            
            # 封面图片标签
            cover_label = tk.Label(cover_container, 
                                 bg=self.style_manager.colors['bg_tertiary'], 
                                 text='📷\n加载中...',
                                 font=self.style_manager.fonts['body'], 
                                 fg=self.style_manager.colors['text_tertiary'])
            cover_label.pack(fill='both', expand=True)
            
            # 绑定右键菜单到封面标签
            cover_label.bind("<Button-3>", show_menu)
            
            # 异步加载封面 - 根据类型选择不同的加载方式
            if album_type == 'collection':
                # 合集使用第一个相册的封面
                cover_image = album.get('cover_image')
                if cover_image:
                    self._load_specific_cover_image(cover_image, 
                                                   lambda photo, label=cover_label: self._update_cover(label, photo),
                                                   size=(320, 350))
                else:
                    cover_label.configure(text='📚\n合集', 
                                        font=self.style_manager.fonts['body'],
                                        fg=self.style_manager.colors['text_tertiary'])
            else:
                # 单个相册正常加载
                self._load_cover_image(album_path, 
                                     lambda photo, label=cover_label: self._update_cover(label, photo),
                                     size=(320, 350))
            
            # 信息区域 - 限制高度确保按钮可见
            info_frame = tk.Frame(card, bg=self.style_manager.colors['card_bg'], height=120)
            info_frame.pack(fill='x', padx=self.card_padding, pady=(0, 8))
            info_frame.pack_propagate(False)
            
            # 绑定右键菜单到信息区域
            info_frame.bind("<Button-3>", show_menu)
            
            # 漫画名称
            name_label = tk.Label(info_frame, 
                                text=album_name,
                                font=self.style_manager.fonts['subheading'],
                                bg=self.style_manager.colors['card_bg'], 
                                fg=self.style_manager.colors['text_primary'], 
                                anchor='nw',
                                wraplength=360,
                                justify='left',
                                height=3)
            name_label.pack(fill='x')
            
            # 绑定右键菜单到名称标签
            name_label.bind("<Button-3>", show_menu)
            
            # 统计信息容器
            stats_frame = tk.Frame(info_frame, bg=self.style_manager.colors['card_bg'])
            stats_frame.pack(fill='x', pady=(4, 0))
            
            # 绑定右键菜单到统计信息
            stats_frame.bind("<Button-3>", show_menu)
            
            # 统计信息 - 根据类型显示不同内容
            count_icon = tk.Label(stats_frame, 
                                text=icon,
                                font=self.style_manager.fonts['caption'],
                                bg=self.style_manager.colors['card_bg'])
            count_icon.pack(side='left')
            count_icon.bind("<Button-3>", show_menu)
            
            count_label = tk.Label(stats_frame, 
                                 text=display_text,
                                 font=self.style_manager.fonts['caption'],
                                 bg=self.style_manager.colors['card_bg'], 
                                 fg=self.style_manager.colors['text_secondary'])
            count_label.pack(side='left', padx=(4, 0))
            count_label.bind("<Button-3>", show_menu)
            
            # 如果是合集，显示总图片数
            if album_type == 'collection' and image_count > 0:
                total_label = tk.Label(stats_frame, 
                                     text=f'共 {image_count} 张图片',
                                     font=self.style_manager.fonts['small'],
                                     bg=self.style_manager.colors['card_bg'], 
                                     fg=self.style_manager.colors['text_tertiary'])
                total_label.pack(side='right')
                total_label.bind("<Button-3>", show_menu)
            
            # 路径显示
            path_label = tk.Label(info_frame, 
                                text=album_path,
                                font=self.style_manager.fonts['small'],
                                bg=self.style_manager.colors['card_bg'], 
                                fg=self.style_manager.colors['text_tertiary'], 
                                anchor='nw',
                                wraplength=360,
                                justify='left',
                                height=2)
            path_label.pack(fill='x', pady=(2, 0))
            path_label.bind("<Button-3>", show_menu)
            
            # 按钮区域
            button_frame = tk.Frame(card, bg=self.style_manager.colors['card_bg'])
            button_frame.pack(fill='x', padx=self.card_padding, pady=(0, self.card_padding))
            button_frame.bind("<Button-3>", show_menu)
            
            # 打开按钮 - 根据类型显示不同文本
            open_btn_style = self.style_manager.get_button_style('primary')
            if album_type == 'collection':
                btn_text = '📚 查看合集'
                open_command = lambda: self._open_collection(album)
            else:
                btn_text = '📂 打开漫画'
                open_command = lambda: self.open_callback(album_path)
                
            open_btn = tk.Button(button_frame, 
                               text=btn_text,
                               command=open_command,
                               **open_btn_style,
                               padx=12, 
                               pady=6)
            open_btn.pack(side='left')
            
            self.style_manager.create_hover_effect(
                open_btn,
                self.style_manager.colors['button_primary_hover'],
                self.style_manager.colors['button_primary']
            )
            
            # 收藏按钮
            is_fav = self.is_favorite(album_path) if self.is_favorite else False
            fav_text = '⭐ 已收藏' if is_fav else '☆ 收藏'
            fav_style = self.style_manager.get_button_style('secondary')
            
            if is_fav:
                fav_style['fg'] = self.style_manager.colors['warning']
            
            fav_btn = tk.Button(button_frame, 
                              text=fav_text,
                              command=lambda: self._toggle_favorite(album_path, fav_btn),
                              **fav_style,
                              padx=12, 
                              pady=6)
            fav_btn.pack(side='right')
            
            self.style_manager.create_hover_effect(
                fav_btn,
                self.style_manager.colors['button_secondary_hover'],
                fav_style['bg']
            )
            
            # 添加双击打开功能
            def on_double_click(event):
                print(f"双击打开相册: {album_path}")
                self.open_callback(album_path)
                return "break"
            
            # 为所有主要组件绑定双击事件
            for widget in [card, cover_container, cover_label, info_frame, name_label]:
                widget.bind("<Double-Button-1>", on_double_click)
            
            print(f"创建卡片完成，路径: {album_path}")
            return card
            
        except Exception as e:
            print(f"创建漫画卡片时出错: {e}")
            import traceback
            traceback.print_exc()
            # 返回错误卡片
            error_card = tk.Frame(parent, 
                                bg=self.style_manager.colors.get('error_light', '#ffebee'),
                                relief='flat', 
                                bd=1)
            error_label = tk.Label(error_card, 
                                 text='❌ 加载失败',
                                 font=self.style_manager.fonts['body'],
                                 bg=self.style_manager.colors.get('error_light', '#ffebee'), 
                                 fg=self.style_manager.colors.get('error', '#d32f2f'))
            error_label.pack(pady=20)
            return error_card
    
    def _toggle_favorite(self, album_path, button):
        """切换收藏状态并更新按钮"""
        try:
            # 调用收藏回调
            self.favorite_callback(album_path)
            
            # 更新按钮显示
            is_fav = self.is_favorite(album_path) if self.is_favorite else False
            fav_text = '⭐ 已收藏' if is_fav else '☆ 收藏'
            button.configure(text=fav_text)
            
            if is_fav:
                button.configure(fg=self.style_manager.colors['warning'])
            else:
                button.configure(fg=self.style_manager.colors['text_primary'])
                
        except Exception as e:
            print(f"切换收藏状态时出错: {e}")
    
    def _add_hover_effects(self, album_frame, open_btn, fav_btn):
        """添加悬停效果"""
        try:
            # 漫画卡片悬停效果
            def on_album_enter(event):
                album_frame.configure(relief='solid', bd=2)
                
            def on_album_leave(event):
                album_frame.configure(relief='solid', bd=1)
            
            album_frame.bind('<Enter>', on_album_enter)
            album_frame.bind('<Leave>', on_album_leave)
            
            # 按钮悬停效果
            def on_open_btn_enter(event):
                open_btn.configure(bg='#0056D6')
                
            def on_open_btn_leave(event):
                open_btn.configure(bg='#007AFF')
                
            open_btn.bind('<Enter>', on_open_btn_enter)
            open_btn.bind('<Leave>', on_open_btn_leave)
            
            # 收藏按钮悬停效果
            def on_fav_btn_enter(event):
                current_bg = fav_btn.cget('bg')
                if current_bg == '#FF9500':  # 已收藏
                    fav_btn.configure(bg='#E6830C')
                else:  # 未收藏
                    fav_btn.configure(bg='#6D6D80')
                    
            def on_fav_btn_leave(event):
                current_bg = fav_btn.cget('bg')
                if current_bg == '#E6830C':  # 已收藏悬停
                    fav_btn.configure(bg='#FF9500')
                else:  # 未收藏悬停
                    fav_btn.configure(bg='#8E8E93')
                    
            fav_btn.bind('<Enter>', on_fav_btn_enter)
            fav_btn.bind('<Leave>', on_fav_btn_leave)
            
        except Exception as e:
            print(f"添加悬停效果时出错: {e}")
    
    def _create_fallback_display(self, albums):
        """创建基本的显示方式作为备用"""
        try:
            # 清除现有内容
            if hasattr(self, 'scrollable_frame') and self.scrollable_frame:
                for widget in self.scrollable_frame.winfo_children():
                    widget.destroy()
                
                # 创建简单的列表显示
                error_label = tk.Label(self.scrollable_frame, 
                                     text="界面组件出错，使用简化显示", 
                                     font=get_safe_font('Arial', 14), 
                                     bg='#F2F2F7', fg='#FF3B30')
                error_label.pack(pady=10)
                
                # 简单显示漫画
                for album in albums:
                    try:
                        album_name = album.get('name', '未知漫画')
                        album_path = album.get('path', '')
                        image_count = album.get('image_count', 0)
                        
                        simple_frame = tk.Frame(self.scrollable_frame, bg='white', relief='solid', bd=1)
                        simple_frame.pack(fill='x', padx=10, pady=2)
                        
                        info_text = f"{album_name} ({image_count} 张图片)"
                        tk.Label(simple_frame, text=info_text, bg='white', anchor='w').pack(side='left', padx=10, pady=5)
                        
                        if album_path:
                            tk.Button(simple_frame, text="打开", 
                                    command=lambda p=album_path: self.open_callback(p)).pack(side='right', padx=10)
                    except Exception as e:
                        print(f"创建简化漫画项时出错: {e}")
                        continue
                        
        except Exception as e:
            print(f"创建备用显示时出错: {e}")
    
    def _update_cover(self, label, photo):
        """更新封面图片"""
        try:
            if photo and label.winfo_exists():
                label.configure(image=photo, text="")
                label.image = photo  # 保持引用
        except Exception as e:
            print(f"更新封面时出错: {e}")
    
    def __del__(self):
        """清理资源"""
        try:
            # 取消防抖定时器
            if hasattr(self, 'layout_timer') and self.layout_timer:
                try:
                    self.parent.after_cancel(self.layout_timer)
                except:
                    pass
            
            # 注意：不再管理executor，因为使用的是全局缓存
            # if hasattr(self, 'executor'):
            #     self.executor.shutdown(wait=False)
        except:
            pass