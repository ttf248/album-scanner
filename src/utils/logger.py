import logging
import sys
from datetime import datetime

class ConsoleLogger:
    """控制台日志管理器 - 统一管理应用程序日志输出"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConsoleLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.setup_logging()
            ConsoleLogger._initialized = True
    
    def setup_logging(self):
        """设置日志配置"""
        # 创建根日志器
        self.logger = logging.getLogger('comic_reader')
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            
            # 设置日志格式
            formatter = logging.Formatter(
                fmt='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            # 添加处理器到日志器
            self.logger.addHandler(console_handler)
            
            # 防止日志向上传播到根日志器
            self.logger.propagate = False
    
    def get_logger(self, name=None):
        """获取指定名称的日志器"""
        if name:
            return logging.getLogger(f'comic_reader.{name}')
        return self.logger
    
    def debug(self, message, module_name=None):
        """调试信息"""
        logger = self.get_logger(module_name)
        logger.debug(message)
    
    def info(self, message, module_name=None):
        """普通信息"""
        logger = self.get_logger(module_name)
        logger.info(message)
    
    def warning(self, message, module_name=None):
        """警告信息"""
        logger = self.get_logger(module_name)
        logger.warning(message)
    
    def error(self, message, module_name=None):
        """错误信息"""
        logger = self.get_logger(module_name)
        logger.error(message)
    
    def critical(self, message, module_name=None):
        """严重错误"""
        logger = self.get_logger(module_name)
        logger.critical(message)
    
    def exception(self, message, module_name=None):
        """记录异常信息（包含堆栈跟踪）"""
        logger = self.get_logger(module_name)
        logger.exception(message)

# 创建全局日志实例
console_logger = ConsoleLogger()

def get_logger(module_name=None):
    """获取日志器的便捷函数"""
    return console_logger.get_logger(module_name)

def log_info(message, module_name=None):
    """记录信息日志的便捷函数"""
    console_logger.info(message, module_name)

def log_warning(message, module_name=None):
    """记录警告日志的便捷函数"""
    console_logger.warning(message, module_name)

def log_error(message, module_name=None):
    """记录错误日志的便捷函数"""
    console_logger.error(message, module_name)

def log_debug(message, module_name=None):
    """记录调试日志的便捷函数"""
    console_logger.debug(message, module_name)

def log_exception(message, module_name=None):
    """记录异常日志的便捷函数"""
    console_logger.exception(message, module_name)
