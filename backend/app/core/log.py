import os
import logging
from logging.handlers import TimedRotatingFileHandler


def get_logger(log_name='app.log'):
    # logger = logging.getLogger()  # 使用 root logger
    logger_name = log_name.replace('.log', '')  # 具名 logger：如 "app", "ota"
    logger = logging.getLogger(logger_name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(__file__), '../data/logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, log_name)

    # 配置日志格式
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

    # 创建 FileHandler
    # file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler = TimedRotatingFileHandler(log_file, when='D', interval=1, backupCount=10, encoding='utf-8')
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    # 添加控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
    logger.propagate = False  # 不传递到 root logger，避免重复输出
    return logger


logger = get_logger()
