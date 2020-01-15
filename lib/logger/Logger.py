import os
import logging
import datetime

class Logger():
    def __init__(self, path, name, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        #format
        format = "%(asctime)s - [%(levelname)s](%(name)s):%(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(format, datefmt=date_format)

        #dir/file
        #path = os.path.dirname(os.path.realpath(__file__))
        self.__root_path = path
        self.__path = os.path.join(self.__root_path, name)
        filename = datetime.datetime.now().strftime('%Y%m%d-%H%M%S.log')

        if not os.path.exists(self.__path):
            os.makedirs(self.__path)

        filepath = os.path.join(self.__path,  filename)

        file_handler = logging.FileHandler(filepath);
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def setLevel(self, level):
        self.logger.setLevel(level)

    @property
    def root_path(self):
        return self.__root_path
