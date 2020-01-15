#!/usr/bin/env python
#coding:utf-8
import os
import datetime
import threading
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from lib.logger.LoggerPrinter import LoggerPrinter

class TrafficFig(LoggerPrinter):
    def __init__(self, logger=None):
        self._logger = logger
        self._logger_class = 'TrafficFig'

        self.__main_fig = plt.figure()
        self.__main_fig.suptitle('Traffic Chart')

        self.__ax_LTE = self.__main_fig.add_subplot(3,1,2)#中
        self.__ax_WLAN = self.__main_fig.add_subplot(3,1,3)#下
        self.__ax_Total = self.__main_fig.add_subplot(3,1,1)#上

        self.__ax_LTE.grid(True)
        self.__ax_WLAN.grid(True)
        self.__ax_Total.grid(True)

        self.__ax_LTE.set_xlabel('time')
        self.__ax_LTE.set_ylabel('MB/s')
        self.__ax_LTE.set_title('LTE DL')


        self.__ax_WLAN.set_xlabel('time')
        self.__ax_WLAN.set_ylabel('MB/s')
        self.__ax_WLAN.set_title('WLAN DL')

        self.__ax_Total.set_xlabel('time')
        self.__ax_Total.set_ylabel('MB/s')
        self.__ax_Total.set_title('Total DL')

        self.__time = np.array([])
        self.__LTE = np.array([])
        self.__WLAN = np.array([])

        self.__line_LTE, = self.__ax_LTE.plot(self.__time, self.__LTE)
        self.__line_WLAN, = self.__ax_WLAN.plot(self.__time, self.__WLAN )
        self.__line_Total, = self.__ax_Total.plot(self.__time, self.__LTE+self.__WLAN )

        self.init_figure()

    @property
    def figure(self):
        return self.__main_fig

    @property
    def time_data(self):
        return self.__time
    @time_data.setter
    def time_data(self, src):
        self.__time = src

    @property
    def LTE_data(self):
        return self.__LTE
    @LTE_data.setter
    def LTE_data(self, src):
        self.__LTE = src

    @property
    def WLAN_data(self):
        return self.__WLAN
    @WLAN_data.setter
    def WLAN_data(self, src):
        self.__WLAN = src


    #for anime
    def update_figure(self, frame):
        if len(self.__time) == 0:
            return

        self.__line_LTE.set_data(self.__time, self.__LTE)
        self.__line_WLAN.set_data(self.__time, self.__WLAN )
        self.__line_Total.set_data(self.__time, self.__LTE+self.__WLAN )
        self.__ax_LTE.set_xlim(self.__time[0], self.__time[-1]+1)
        self.__ax_LTE.set_ylim(0, np.max(self.__LTE)+5)

        self.__ax_WLAN.set_xlim(self.__time[0], self.__time[-1]+1)
        self.__ax_WLAN.set_ylim(0, np.max(self.__WLAN )+5)

        self.__ax_Total.set_xlim(self.__time[0], self.__time[-1]+1)
        self.__ax_Total.set_ylim(0, np.max(self.__LTE+self.__WLAN )+5)

        print(frame)
        if self.__time[-1] and int(self.__time[-1])%30 == 0:
            self.__save_figre()

    #for anime
    def init_figure(self):
        plt.tight_layout(rect=[0, 0, 1, 0.965])

    def __save_figre(self):
        self._print_info('traffic chart image saving')
        path = ''
        if self._logger is None:
            path = os.path.join(self._logger.root_path, 'traffic')
            self._print_debug('save path is logger root path')
        path = 'logs/traffic'
        filename = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

        if not os.path.exists(path):
            os.makedirs(path)

        plt.savefig('%s/%s-%s.png' % (path, filename, self.__time[-1]))
        self._print_info('traffic chart image saved: %s-%.2f.png' % (filename, self.__time[-1]))

class TrafficChart(ttk.Frame, LoggerPrinter):
    def __init__(self, logger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._logger = logger
        self._logger_class = 'TrafficChart'
        self.__tfg = TrafficFig(logger)

        #ttk init
        #self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.__canvas = FigureCanvasTkAgg(self.__tfg.figure , master=self)
        self.__canvas.get_tk_widget().grid(row=0, column=0, sticky='NSEW')

    def update_data(self, LTE = 0, WLAN = 0, delay=0):
        #確認frame
        self.__tfg.LTE_data = np.append(self.__tfg.LTE_data, LTE)
        self.__tfg.WLAN_data = np.append(self.__tfg.WLAN_data , WLAN)

        # if len(self.__tfg.time_data) == 0:
        #     self.__tfg.time_data = np.append(self.__tfg.time_data , delay)
        # else:
        self.__tfg.time_data = np.append(self.__tfg.time_data , delay)

        if len(self.__tfg.time_data) >= 30:
            self.__tfg.time_data = self.__tfg.time_data[1:]
            self.__tfg.LTE_data = self.__tfg.LTE_data[1:]
            self.__tfg.WLAN_data = self.__tfg.WLAN_data [1:]

        self._print_debug('traffic chart data update %s' % self.__tfg.time_data[-1])

    #start anime
    def start_anime(self):
        self._print_debug('traffic chart start anime')
        self.__animation = animation.FuncAnimation(self.__tfg.figure, self.__tfg.update_figure, init_func=self.__tfg.init_figure, interval=1000, frames=30, blit=False)

    def clear_chart(self):
        self.__tfg.time_data = np.array([])
        self.__tfg.LTE_data = np.array([])
        self.__tfg.WLAN_data = np.array([])

    def __parser_data(self, data):
        if data is None:
            self._print_info('no new data recv')
            #self.update_data()
            return

        if data['status'] == 132:
            #self.update_data()
            self._print_error('msg 132 recv')
            self._print_error(parser_data['message'])
            return

        if data['status'] == 135:
            self._print_info('data recv push')
            self.update_data(data['LTE_traffic']/1024, data['WIFI_traffic']/1024, data['delay'])

    def attach_L2GUIServ(self, l2guiserv):
        self.__l2guiserv = l2guiserv
        try:
            self.__l2guiserv_thread = threading.Thread(target=self.__l2guiserv.run_server,args=(self.__parser_data,))
            self.__l2guiserv_thread.setDaemon(True)
            self.__l2guiserv_thread.start()
            self._print_info('L2GUI thread started!')
        except:
            self._print_error('L2GUI thread start failed!')
