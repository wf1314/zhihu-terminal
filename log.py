import os
import logging
from logging.handlers import RotatingFileHandler
from setting import DEBUG
from setting import LOG_DIR


def get_logger():
    """
    获取日志对象
    :return:
    """
    log_dir = LOG_DIR if LOG_DIR else '/tmp/zhihu/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG) if DEBUG else log.setLevel(logging.INFO)
    log_file = os.path.join(log_dir, 'log.log')
    handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 30, backupCount=10)
    handler1 = logging.StreamHandler()
    default_format = logging.Formatter(
        '[%(levelname)1.1s %(asctime)s.%(msecs)03d %(module)s:%(lineno)d]%(' 'message)s ')
    handler.setFormatter(fmt=default_format)
    handler1.setFormatter(fmt=default_format)
    log.addHandler(handler)
    log.addHandler(handler1)
    log.debug('----------初始化日志-----------')
    return log