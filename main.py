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
        # 创建主窗口
        root = ThemedTk()
        
        # 创建应用程序
        from app_manager import PhotoAlbumApp
        app = PhotoAlbumApp(root)
        
        # 运行主循环
        root.mainloop()
        
    except Exception as e:
        error_msg = f"启动应用程序时发生错误：{e}"
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