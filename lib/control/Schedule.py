import time
import threading

from lib.logger.LoggerPrinter import LoggerPrinter

class Schedule(LoggerPrinter):
    def __init__(self, terminal, config, logger=None):
        self.__config = config
        self._logger = logger
        self._logger_class = 'Schedule'
        self.__terminal = terminal

        self.__task_running = False

    def _check_task(func):
        def wrapper( *args, **kwargs):
            self = args[0]
            def busy():
                return False

            if self.__task_running:
                self._print_error('cannot running %s task, other task is still running...' % func.__name__)
                return busy()

            self.__task_running = True
            self._print_info('run task')
            return func(*args, **kwargs)

        return wrapper

    @_check_task
    def start_up_cell(self):
        self._print_info('startup cell')
        try:
            self.__start_up_thread = threading.Thread(target=self.__start_up_cell)
            self.__start_up_thread.setDaemon(True)
            self.__start_up_thread.start()
        except:
            self._print_error('Cannot running start_up_cell thread')
            self.__task_running = False
            return False
        return True

    def __start_up_cell(self):

        commands = self.__get_startup_command()
        for cmd in commands.values():
            console = self.__terminal[cmd['target']]
            if cmd['dir']:
                cmd_dir = 'cd %s' % cmd['dir']
                self._print_debug('sned dir command %s' % cmd_dir)
                console.send_message(cmd_dir)
                time.sleep(1)
            self._print_debug('send run command %s' % cmd['run'])
            console.send_message(cmd['run'])
            time.sleep(self.__config.get_command_delay_time())
        self._print_info('cell started!')
        self.__task_running = False

    def __get_startup_command(self):
        commands = {}
        order = 1
        cmd = self.__config.get_command(order)
        while cmd:
            self._print_info(cmd)
            commands[order] = cmd
            order+=1
            cmd = self.__config.get_command(order)
        return commands

    @_check_task
    def stop_cell(self):
        self._print_info('stop cell')
        try:
            self.__stop_thread = threading.Thread(target=self.__stop_cell)
            self.__stop_thread.setDaemon(True)
            self.__stop_thread.start()
        except:
            self._print_error('Cannot running stop thread')
            self.__task_running = False
            return False
        return True

    def __stop_cell(self):
        self._print_info('cell halting')
        for terminal in self.__terminal.values():
            terminal.send_break_signal()
            time.sleep(1)
        self._print_info('cell stop!')
        self.__task_running = False

    @_check_task
    def shutdown_cell(self):
        self._print_info('shutdown cell')
        try:
            self.__shutdown_thread = threading.Thread(target=self.__shutdown_cell)
            self.__shutdown_thread.setDaemon(True)
            self.__shutdown_thread.start()
        except:
            self._print_error('Cannot running shutdown thread')
            self.__task_running = False
            return False
        return True

    def __shutdown_cell(self):
        self.__stop_cell()
        self.__task_running = True#fix state

        for i in range(1,self.__config.get_screen_number()+1):
            screen = self.__config.get_screen_conf(i)
            if screen['type'] == 'ssh':
                self.__terminal[screen['name']].send_message('poweroff')
                time.sleep(5)
                for times in range(0, 5):
                    if self.__terminal[screen['name']].get_status():
                        self.__terminal[screen['name']].send_message('poweroff')
                    else:
                        break
                    time.sleep(10)
                continue
        self._print_info('cell shutdown!')
        self.__task_running = False

    @_check_task
    def upload_image(self, layer=None):
        if layer is None:
            self._print_info('upload image layer does not specify')
            return False
        self._print_info('upload image to cell')
        try:
            self.__shutdown_thread = threading.Thread(target=self.__upload_image, args=(layer,))
            self.__shutdown_thread.setDaemon(True)
            self.__shutdown_thread.start()
        except:
            self._print_error('Cannot running upload image thread')
        return True

    def __upload_image(self, layer=None):
        cmd = self.__config.get_tools_command(layer)
        targer = ''
        if cmd['target'] in self.__terminal.keys():
            targer = cmd['target']
        if cmd['target'] == 'sys_ssh':
            targer = self.__config.get_sys_ssh()
        if cmd['target'] == 'sys_bash':
            targer = self.__config.get_sys_bash()

        console = self.__terminal[targer]
        if cmd['dir']:
            cmd_dir = 'cd %s' % cmd['dir']
            self._print_debug('sned dir command %s' % cmd_dir)
            console.send_message(cmd_dir)
            time.sleep(1)
        self._print_debug('send run command %s' % cmd['run'])
        console.send_message(cmd['run'])
        time.sleep(1)
        console.send_message('')
        console.send_message('')
        self.__task_running = False
