import paramiko
import select

from .Terminal import Terminal

class RemoteClient(Terminal):
    class SSHTimeoutException(Exception):
        pass
    class SSHAuthEception(Exception):
        pass

    def __init__(self, ip, port=22, username='root', password='', logger=None):
        super().__init__()
        self.__ip = ip
        self.__port = port
        self.__username = username
        self.__password = password
        self._logger = logger
        self._logger_class = 'RemoteClient'

        #self.__status = False

        self.__connect(5) #connect

    def __connect(self, timeout=None):
        try:
            self.__trans = paramiko.Transport(self.__ip, self.__port)
            self.__trans.start_client(timeout=timeout)

            self.__trans.auth_password(username=self.__username, password=self.__password)
            self.__channel = self.__trans.open_session()
            self.__channel.get_pty()
            self.__channel.invoke_shell()
            self.__channel.settimeout(0)
            self.__status = True
        except paramiko.ssh_exception.AuthenticationException:
            self._print_error('Auth failed!')
            raise self.SSHAuthEception
        except:
           self._print_error('Connection error!')
           raise self.SSHTimeoutException
           return False

    def get_status(self):
        return self.__trans.is_active()
        #return self.__status

    def disconnect(self):
        self._print_info('disconnect!')
        self.__channel.close()
        self.__trans.close()
        #self.__status = False

    def recv_message(self, callback=None):
        while True:
            readlist, writelist, errlist = select.select([self.__channel], [], [])

            if self.__channel in readlist:
                recv = self.__channel.recv(1024)
                if len(recv) == 0:
                    self._print_info('session disconnect!')
                    break
                result = self._conv_str(recv)
                self._print_debug(result)
                #callback(result)
                self._call_recv_handlers(result)
        self.disconnect()

    def send_message(self, data=''):
        try:
            self.__channel.sendall(data.strip()+'\n')
        except:
            self._print_error('sendall error!')

    def send_break_signal(self):
        self.send_message('\x03')
