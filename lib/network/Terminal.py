import re

from lib.logger.LoggerPrinter import LoggerPrinter

class Terminal(LoggerPrinter):
    def __init__(self):
        self.__recv_handlers = []

    def _conv_str(self, data):
        ansi_text = str(data, encoding = 'utf-8', errors='ignore').replace('\r\n', '\n')
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -\/]*[@-~])')
        text = ansi_escape.sub('', ansi_text)
        return text

    def _print(self, level, message):
        text = '(%s) %s' % (self._logger_class, message.strip())
        try:
            func = getattr(self._logger, level)
            func(text)
        except:
            print(text)

    def register_recv_handler(self, handler):
        if callable(handler):
            self.__recv_handlers.append(handler)
            return True
        return False

    def _call_recv_handlers(self, *args, **kwargs):
        for handler in self.__recv_handlers:
            try:
                handler( *args, **kwargs)
            except:
                self._print_error('recv handler %s error!' % handler.__name__)


    def send_message(self, data):
        None

    def send_break_signal(self):
        None

    def recv_message(self, callback=None):
        None

    def get_status(self):
        None
