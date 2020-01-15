import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import *
import threading

from lib.GUI.TerminalFrame import TerminalFrame
from lib.network.RemoteClient import RemoteClient
from lib.network.LocalBash import LocalBash

from lib.GUI.TrafficChart import TrafficChart
from lib.network.L2GUIServ import L2GUIServ
from lib.GUI.ControlFrame import ControlFrame
from lib.GUI.FunctionFrame import FunctionFrame
from lib.GUI.UEListFrame import UEListFrame

from lib.logger.Logger import Logger
from lib.logger.LoggerPrinter import LoggerPrinter

from lib.config.ConfigLoader import ConfigLoader

from lib.control.Schedule import Schedule
from lib.control.AnalysisUEInfo import AnalysisUEInfo


import threading
import time

class SmallCellGUI(LoggerPrinter):
    def __init__(self, path, config, logger):

        self.__config = config
        self._logger = logger
        self._logger_class = 'SmallCellGUI'

        self.__root = tk.Tk()

        self.__root.title('ITRI Small Cell GUI')
        self.__root.resizable(width=False, height=False)
        self.__root.geometry("1280x720")
        self.__root.grid_rowconfigure(0, weight=1)
        self.__root.grid_columnconfigure(0, weight=1)
        self.__root.protocol('WM_DELETE_WINDOW', self.__on_exit)

        self.__notebook = ttk.Notebook(self.__root)

        self.__terminal_tab = {}
        self.__terminal_tab['frame'] = {}
        self.__terminal_tab['terminal'] = {}

        self.__control_tab = {}
        self.__control_tab['frame'] = None
        self.__control_tab['chart'] = None
        self.__control_tab['l2guiserv'] = None

        self.__notebook.grid(row=0, column=0, sticky='nsew')

        self.__schedule = Schedule(self.__terminal_tab['terminal'], config=self.__config, logger=self._logger)

        self.__create_control_plane()
        self.__create_terminal()

    def __create_control_plane(self):
        control_logger =  Logger(os.path.join(path, 'logs'), 'TrafficChart')

        self.__control_tab['frame'] = ttk.Frame(self.__notebook)

        self.__control_tab['chart'] = TrafficChart(logger=control_logger, master=self.__control_tab['frame'])
        self.__control_tab['chart'].pack(side='left', fill='y', expand=True)
        self.__control_tab['chart'].start_anime()

        self.__control_tab['control_btn'] = ControlFrame(logger=control_logger, master=self.__control_tab['frame'], text='系統功能')
        self.__control_tab['control_btn'].pack(side='top', fill='x', expand=True, padx=10)

        self.__control_tab['control_btn'].set_callback(ControlFrame.BtnId.CONNECT, self.connect_terminal)
        self.__control_tab['control_btn'].set_callback(ControlFrame.BtnId.STARTUP, self.start_terminal)
        self.__control_tab['control_btn'].set_callback(ControlFrame.BtnId.STOP, self.stop_terminal)
        self.__control_tab['control_btn'].set_callback(ControlFrame.BtnId.SHUTDOWN, self.shutdown_cell)
        self.__control_tab['control_btn'].set_callback(ControlFrame.BtnId.L2GUI, self.start_chart)
        self.__control_tab['control_btn'].set_callback(ControlFrame.BtnId.UPDATE_L1, lambda: self.__schedule.upload_image('uploadL1'))
        self.__control_tab['control_btn'].set_callback(ControlFrame.BtnId.UPDATE_L3, lambda: self.__schedule.upload_image('uploadL3'))

        self.__control_tab['function_btn'] = FunctionFrame(logger=control_logger, config=self.__config, master=self.__control_tab['frame'], text='設定參數')
        self.__control_tab['function_btn'].pack(side='top', fill='x', expand=True, padx=10)

        self.__control_tab['ue_list'] = UEListFrame(logger=control_logger, master=self.__control_tab['frame'], text='UE清單')
        self.__control_tab['ue_list'].pack(side='top', fill='x', expand=True, padx=10)

        self.__notebook.add(self.__control_tab['frame'], text='Control')


    def __create_terminal(self):
        for screen_id in range(1,self.__config.get_screen_number()+1):
            screen_conf = self.__config.get_screen_conf(screen_id)
            screen_logger = Logger(os.path.join(path, 'logs'), screen_conf['name'])

            frame = TerminalFrame(screen_logger, self.__notebook)
            frame.grid()
            self.__notebook.add(frame, text=screen_conf['name'])
            self.__terminal_tab['frame'][screen_conf['name']] = frame


    def connect_terminal(self):
        #start terminal
        for screen_id in range(1,self.__config.get_screen_number()+1):
            screen_conf = self.__config.get_screen_conf(screen_id)
            screen_logger = self.__terminal_tab['frame'][screen_conf['name']].get_logger()

            terminal = None
            try:
                if screen_conf['type'] == 'ssh':
                    params = self.__config.get_connect_params()
                    terminal = RemoteClient(*params, screen_logger)
                    if screen_conf['name'] == self.__config.get_sys_ssh():
                        terminal.send_message('cd %s' % self.__config.get_SmallCell_basedir())

                if screen_conf['type'] == 'bash':
                    terminal = LocalBash(logger=screen_logger)
                    if screen_conf['name'] == self.__config.get_sys_bash():
                        terminal.send_message('cd %s' % self.__config.get_UDcell_basedir())

                if terminal is None:
                    self._print_error('screen %s attach error, not type terminal' % (screen_conf['name'], screen_conf['type']))
                    continue

            except RemoteClient.SSHTimeoutException:
                self._print_error('screen %s attach error, SSH connect TIMEOUT' % screen_conf['name'])
                return False

            except RemoteClient.SSHAuthEception:
                self._print_error('screen %s attach error, SSH auth failed' % screen_conf['name'])
                return False

            except LocalBash.SpawnExpection:
                self._print_error('screen %s attach error, Bash process create failed' % screen_conf['name'])
                return False

            self.__terminal_tab['frame'][screen_conf['name']].attach_terminal(terminal)
            self.__terminal_tab['terminal'][screen_conf['name']] = terminal

        self.__control_tab['function_btn'].attach_sys_ssh(self.__terminal_tab['terminal'][self.__config.get_sys_ssh()])
        self.register_analysis()
        return True

    def start_terminal(self):
        self.start_chart()
        return self.__schedule.start_up_cell()

    def stop_terminal(self):
        return self.__schedule.stop_cell()

    def shutdown_cell(self):
        return self.__schedule.shutdown_cell()

    def register_analysis(self):
        terminal = self.__terminal_tab['terminal']['S3']
        self.__s3_analysis = AnalysisUEInfo(terminal=terminal, logger=self._logger)

        self.__s3_analysis.register_notice_add(self.__control_tab['ue_list'].add_UE)
        self.__s3_analysis.register_notice_del(self.__control_tab['ue_list'].del_UE)
        terminal.register_recv_handler(self.__s3_analysis.analysis_ue)

    def start_chart(self):
        #start L2GUIServ
        try:
            if self.__control_tab['l2guiserv']:
                self.__control_tab['chart'].clear_chart()
                return
            self.__control_tab['l2guiserv'] = L2GUIServ(logger=self.__control_tab['chart'].get_logger())
            self.__control_tab['chart'].attach_L2GUIServ(self.__control_tab['l2guiserv'])
        except:
            self._print_error('cannot start chart/L2GUI')
            return False
        return True

    def get_terminal_tab(self):
        return self.__terminal_tab;

    def __on_exit(self):
        self.__root.destroy()
        sys.exit()

    def mainloop(self):
        while True:
            try:
                self.__root.mainloop()
                break
            except UnicodeDecodeError:
                pass

if __name__ == '__main__':

    path = os.path.dirname(os.path.realpath(__file__))

    logger = Logger(os.path.join(path, 'logs'), 'Main_thread')
    config = ConfigLoader(os.path.join(path, 'config'), logger=logger)

    scg = SmallCellGUI(path, config, logger)
    scg.mainloop()
