
class LoggerPrinter():
    def _print_debug(self, message):
        self._print('debug', message)

    def _print_info(self, message):
        self._print('info', message)

    def _print_error(self, message):
        self._print('warning', message)

    def _print(self, level, message):
        text = '(%s) %s' % (self._logger_class, message)
        try:
            func = getattr(self._logger, level)
            func(text)
        except:
            print(text)

    def get_logger(self):
        return self._logger
