import logging, sys, datetime


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



strf_time = lambda x: x.strftime("%Y-%m-%d %H:%M:%S")
strf_current_time = lambda: strf_time(datetime.datetime.now())
class progress_info:
    def __init__(self, rg, info):
        self.start_iter = False
        self.it = iter(rg)
        self.cnt = 0
        self.info = info
    
    def __iter__(self):
        self.start_iter = True
        return self
    
    def __next__(self):
        try:
            val = next(self.it)
            self.cnt += 1
            print(f'{strf_current_time()} [INFO] {self.info}{self.cnt * "."}', file=sys.stderr, end='\r')
            return val
        except StopIteration:
            raise StopIteration
        
    def __del__(self):
        print()