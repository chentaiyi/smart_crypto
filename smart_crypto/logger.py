import logging
import os
import time



class Logger:
    def __init__(self):
        self.logger = logging.getLogger()
        flt = time.strftime("%Y%m%d%H%M%S", time.localtime())
        log_folder='log'
        current_folder = os.path.dirname(__file__)
        log_path = os.path.join(current_folder, log_folder)
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        log_file_name = flt+'.log'
        log_file = os.path.join(log_path,log_file_name)
        fh = logging.FileHandler(log_file,mode='a+',encoding='UTF8')
        sh = logging.StreamHandler()
        fmt= logging.Formatter('%(asctime)s-%(levelname)s-%(process)d %(message)s')
        fh.setFormatter(fmt)
        sh.setFormatter(fmt)
        fh.setLevel(logging.INFO)
        sh.setLevel(logging.INFO)
        self.logger.addHandler(fh)
        self.logger.addHandler(sh)
        self.logger.setLevel(logging.DEBUG)

    def ouputlog(self,message,level="INFO"):
        if level=="DEBUG":
            self.logger.debug(message)
        if level =="INFO":
            self.logger.info(message)
        if level == "WARNING":
            self.logger.warning(message)
        if level == "ERROR":
            self.logger.error(message)

logger = Logger()

if __name__ == "__main__":
    s="哈哈哈"
    logger.ouputlog("test log %s"%s,"INFO")