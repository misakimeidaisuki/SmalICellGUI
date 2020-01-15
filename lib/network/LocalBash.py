import select
import pexpect
import time

from .Terminal import Terminal

class LocalBash(Terminal):
    class SpawnExpection(Exception):
        pass

    def __init__(self, bash_location='/bin/bash', logger=None):
        super().__init__()
        try:
            self.__proc = pexpect.spawn(bash_location)
        except:
            self._print_error('cannot create bash process!')
            raise self.SpawnExpection

        self._logger = logger;
        self._logger_class = 'LocalBash'
        self.send_message('')

    def get_status(self):
        return self.__proc.isalive()

    def kill_process(self):
        self.__proc.kill(0)

    def recv_message(self, callback=None):
        while True:
            try:
                if self.__proc.isalive() is False:
                    self._print_error('process is not alive!')
                    self.kill_process()
                    return

                recv = self._conv_str(self.__proc.readline())
                self._print_debug(recv)
                #callback(recv)
                self._call_recv_handlers(recv)

            except pexpect.EOF:
                self.kill_process()
                self._print_error('EOF')
                break
            except pexpect.TIMEOUT:
                self._print_info('TIMEOUT, wait 1s')
                time.sleep(1)
                continue
            except :
                self.kill_process()
                self._print_error('unknown errors!')
                break

    def send_message(self, data):
        try:
            self.__proc.sendline(data.strip())
        except:
            self._print_error('send message error!')

    def send_break_signal(self):
        try:
            self.__proc.send('\x03')
            self.send_message('')
        except:
            self._print_error('send break signal error!')
