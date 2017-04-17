# encoding=utf8
import logging
import os
from logging.handlers import BaseRotatingHandler

LOG_FORMAT  = '%(thread)d %(threadName)s %(asctime)s %(filename)s %(funcName)s [line:%(lineno)d] %(levelname)s %(message)s'
LOG_LEVEL   = logging.DEBUG

# 重写 RotatingFileHandler 自定义log的文件名
# 原来 xxx.log xxx.log.1 xxx.log.2 xxx.log.3 文件由近及远
# 现在 xxx.log xxx1.log xxx2.log  如果backupCount 是2位数时  则 01  02  03 三位数 001 002 .. 文件由近及远
class RotatingFileHandler(BaseRotatingHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        # if maxBytes > 0:
        #    mode = 'a'
        BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.placeholder = str(len(str(backupCount)))

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = ('%0'+ self.placeholder + 'd.')%i #  '%2d.'%i -> 02
                sfn = sfn.join(self.baseFilename.split('.'))
                # sfn = "%d_%s" % (i, self.baseFilename)
                # dfn = "%d_%s" % (i + 1, self.baseFilename)
                dfn = ('%0'+ self.placeholder + 'd.')%(i + 1)
                dfn = dfn.join(self.baseFilename.split('.'))
                if os.path.exists(sfn):
                    #print "%s -> %s" % (sfn, dfn)
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = (('%0'+ self.placeholder + 'd.')%1).join(self.baseFilename.split('.'))
            if os.path.exists(dfn):
                os.remove(dfn)
            # Issue 18940: A file may not have been created if delay is True.
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()

    def shouldRollover(self, record):

        if self.stream is None:                 # delay was set...
            self.stream = self._open()
        if self.maxBytes > 0:                   # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        return 0

def get_logger(name = 'log.log', path = ''):
    logger = logging.getLogger(name)
    filename = path + name

    if not os.path.exists(path):
        os.makedirs(path)

    # 配置
    logging.basicConfig(
            level=LOG_LEVEL,
            format= LOG_FORMAT,
            datefmt='%Y-%m-%d %H:%M:%S',
            )

    #定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大10M
    Rthandler = RotatingFileHandler(filename, mode = 'w',  maxBytes=10 * 1024 * 1024,backupCount=20, encoding='utf8')
    Rthandler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(LOG_FORMAT)
    Rthandler.setFormatter(formatter)

    logger.addHandler(Rthandler)

    return logger

# logging.disable(logging.DEBUG) # 关闭所有log

# 不让 requests打印debug日志 看着乱
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARNING)
logging.getLogger("selenium.webdriver.remote").setLevel(logging.WARNING)
logging.getLogger("selenium.webdriver").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)

# print(logging.Logger.manager.loggerDict) # 取使用debug模块的name

#日志级别大小关系为：critical > error > warning > info > debug

import os
CURRENT_PATH = os.getcwd()
log= get_logger('va_image.log', CURRENT_PATH + '\\log\\')