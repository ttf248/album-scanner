import sys
from ttkthemes import ThemedTk

# 设置默认编码
if sys.platform.startswith('win'):
    # Windows环境下设置控制台编码
    try:
        import locale
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass

def main():
    """主函数"""
    try:
        # 初始化日志系统
        from src.utils.logger import get_logger, log_info, log_error, log_exception
        logger = get_logger('main')
        log_info("=== 漫画阅读器启动 ===", 'main')
        
        # 创建主窗口
        log_info("创建主窗口", 'main')
        root = ThemedTk()
        
        # 创建应用程序
        log_info("初始化应用程序", 'main')
        from app_manager import PhotoAlbumApp
        app = PhotoAlbumApp(root)
        
        log_info("应用程序启动成功，进入主循环", 'main')
        # 运行主循环
        root.mainloop()
        
        log_info("=== 应用程序正常退出 ===", 'main')
        
    except Exception as e:
        error_msg = f"启动应用程序时发生错误：{e}"
        
        # 尝试使用日志系统记录错误
        try:
            from src.utils.logger import log_exception
            log_exception(error_msg, 'main')
        except:
            # 如果日志系统也失败，使用print
            print(error_msg)
            import traceback
            traceback.print_exc()
        
        # 显示错误对话框
        try:
            import tkinter.messagebox
            tkinter.messagebox.showerror("启动错误", f"应用程序启动失败：{str(e)}")
        except:
            pass

if __name__ == "__main__":
    main()