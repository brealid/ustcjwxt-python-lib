import logging, sys


logger = logging.Logger('ustcjwxt', level="INFO")

def set_logger_level(level):
    logger.setLevel(level)

def set_logger_file(filename, **kwargs):
    handler = logging.FileHandler(filename, **kwargs)
    logger.addHandler(handler)

def set_logger_format(fmt = "%(asctime)s [%(levelname)s] %(message)s", datefmt = "%Y-%m-%d %H:%M:%S", **kwargs):
    formatter = logging.Formatter(fmt, datefmt, **kwargs)
    for handler in logger.handlers:
        handler.setFormatter(formatter)

def log_debug(msg):
    logger.debug(msg)

def log_info(msg):
    logger.info(msg)

def log_warning(msg):
    logger.warning(msg)

def log_error(msg):
    logger.error(msg)


set_logger_file('/dev/stderr' if sys.platform == 'linux' else 'CON', mode='w')
set_logger_format()