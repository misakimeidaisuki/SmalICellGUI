import os
import sys
import configparser

from lib.logger.LoggerPrinter import LoggerPrinter

class ConfigLoader(LoggerPrinter):
    def __init__(self, path,  filename='config.conf', logger=None):
        self.__config = configparser.ConfigParser()
        self.__config.optionxform = str

        self.__config_fullpath = os.path.join(path,filename)
        self.__config_filename = filename

        self._logger = logger
        self._logger_class = 'ConfigLoader'
        self.__load()

    def __load(self):
        try:
            if not self.__config.read(self.__config_fullpath):
                self._print_error('cannot read conf file')
                sys.exit(0)
            self._print_info('config file is loaded!')
        except configparser.Error:
            self._print_error('conf file parser error.')
            sys.exit(2)

    """
    default
    """
    def get_command_delay_time(self):
        delay = 0
        try:
            delay = int(self.__config['Setting'].get('command_delay'))
        except:
            delay = 15#default 15s
        return  delay

    def get_log_dir(self):
        return self.__config['Setting'].get('log_dir', './log')

    def get_UDcell_basedir(self):
        return self.__config['Setting'].get('UDcell_basedir')

    def get_SmallCell_basedir(self):
        return self.__config['Setting'].get('SmallCell_basedir')

    def get_cell_shutdown_command(self):
        return self.__config['Setting'].get('cell_shutdown_command')

    def get_screen_number(self):
        return self.__config['Setting'].getint('screen_number', 6)

    def get_sys_bash(self):
        return self.__config['Setting'].get('sys_bash', 'Bash')

    def get_sys_ssh(self):
        return self.__config['Setting'].get('sys_ssh', 'SSH')

    """
    bash
    """
    def get_bash_location(self):
        return self.__config['Bash'].get('bash', '/bin/bash')

    """
    SSH
    """
    def get_connect_params(self):
        result = (self.get_ip(), self.get_port(), self.get_account(), self.get_password())
        return result

    def get_ip(self):
        return self.__config['SSHClient'].get('ip', '127.0.0.1')

    def get_port(self):
        return self.__config['SSHClient'].getint('port', 22)

    def get_account(self):
        return self.__config['SSHClient'].get('username', 'root')

    def get_password(self):
        return self.__config['SSHClient'].get('password', '')

    """
    get screen config
    """
    def get_screen_conf(self, id):
        if id < 0 or id > self.get_screen_number():
            self._print_error('screen config only S1~S6')
            return False
        result = dict(self.__config[('S%s' % id)])
        return result

    """
    get command list
    """
    def get_command(self, order):
        try:
            result = dict(self.__config[('Command_%d' % order)])
        except:
            self._print_error('Command_%d not exist in the config file' % order)
            result = None
        return result

    def get_tools_command(self, name):
        try:
            result = dict(self.__config[('tools_command_%s' % name)])
        except:
            self._print_error('tools_command_%s not exist in the config file' % name)
            result = None
        return result
