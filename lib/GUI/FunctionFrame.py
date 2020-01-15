import tkinter as tk
from tkinter import ttk
from tkinter import *

from lib.logger.LoggerPrinter import LoggerPrinter

class FunctionFrame(ttk.LabelFrame, LoggerPrinter):
    def __init__(self, logger=None, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._logger = logger
        self._logger_class = 'FunctionFrame'
        self.__config = config

        self.__ssh = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #LWA Ratio
        self.__lwaratio = {}
        lwa_ratio_frame = ttk.Frame(self)
        label_title_LWA = ttk.Label(lwa_ratio_frame, text='LWA Ratio 設定')
        label_title_LWA.pack(side='top',  fill='both', expand=True)

        label_wifi_ratio = ttk.Label(lwa_ratio_frame, text='Wi-Fi比例 (>=0)')
        label_wifi_ratio.pack(side='left', padx=5)

        self.__lwaratio['wifi_var'] = tk.StringVar()
        self.__lwaratio['wifi_entry'] = ttk.Entry(lwa_ratio_frame, width=2, text=self.__lwaratio['wifi_var'])
        self.__lwaratio['wifi_var'].set(1)
        self.__lwaratio['wifi_entry'].pack(side='left', padx=5)

        label_lte_ratio = ttk.Label(lwa_ratio_frame, text='LTE比例 (>=0)')
        label_lte_ratio.pack(side='left', expand=True, padx=5)

        self.__lwaratio['lte_var'] = tk.StringVar()
        self.__lwaratio['lte_entry'] = ttk.Entry(lwa_ratio_frame, width=2, text=self.__lwaratio['lte_var'])
        self.__lwaratio['lte_var'].set(0)
        self.__lwaratio['lte_entry'].pack(side='left', padx=5)

        self.__lwaratio['send_btn'] = ttk.Button(lwa_ratio_frame, width=10, text='修改設定', command=self.__change_lwaratio)
        self.__lwaratio['send_btn']['state'] = tk.DISABLED
        self.__lwaratio['send_btn'].pack(side='left', padx=5)

        lwa_ratio_frame.grid(row=0, column=0, pady=5)

        #MCS
        self.__mcs = {}
        mcs_frame = ttk.Frame(self)
        label_title_CMS = ttk.Label(mcs_frame, text='LTE MCS 設定')
        label_title_CMS.pack(side='top', fill='both', expand=True)

        label_cms_mratio = ttk.Label(mcs_frame, text='-m (2/3)')
        label_cms_mratio.pack(side='left', padx=5)


        self.__mcs['m_var'] = tk.StringVar()
        self.__mcs['m_entry'] = ttk.Entry(mcs_frame, width=2, text=self.__mcs['m_var'])
        self.__mcs['m_var'].set(2)
        self.__mcs['m_entry'].pack(side='left', padx=5)

        label_cms_dratio = ttk.Label(mcs_frame, text='DL (9~28)')
        label_cms_dratio.pack(side='left', padx=5)

        self.__mcs['d_var'] = tk.StringVar()
        self.__mcs['d_entry'] = ttk.Entry(mcs_frame, width=2, text=self.__mcs['d_var'])
        self.__mcs['d_var'].set(9)
        self.__mcs['d_entry'].pack(side='left', padx=5)

        label_cms_uratio = ttk.Label(mcs_frame, text='UL (9~20)')
        label_cms_uratio.pack(side='left', padx=5)

        self.__mcs['u_var'] = tk.StringVar()
        self.__mcs['u_entry'] = ttk.Entry(mcs_frame, width=2, text=self.__mcs['u_var'])
        self.__mcs['u_var'].set(9)
        self.__mcs['u_entry'].pack(side='left', padx=5)

        self.__mcs['send_btn'] = ttk.Button(mcs_frame, width=10, text='修改設定', command=self.__change_mcs)
        self.__mcs['send_btn']['state'] = tk.DISABLED
        self.__mcs['send_btn'].pack(side='left', padx=5)

        mcs_frame.grid(row=1, column=0, pady=5)

    def attach_sys_ssh(self, ssh=None):
        self.__ssh = ssh
        self.__lwaratio['send_btn']['state'] = tk.NORMAL
        self.__mcs['send_btn']['state'] = tk.NORMAL

    def __is_ssh_attach(self):
        if self.__ssh is None:
            self._print_error('The sys ssh terminal is not specify')
            return False
        return True

    def __run_command(self, command, *args):
        cmd = self.__config.get_tools_command(command)
        if cmd:
            if cmd['dir']:
                cmd_dir = 'cd %s' % cmd['dir']
                self._print_debug('sned dir command %s' % cmd_dir)
                self.__ssh.send_message(cmd_dir)
            if cmd['run']:

                cmd_dir =cmd['run'] % args
                self._print_debug('sned dir command %s' % cmd_dir)
                self.__ssh.send_message(cmd_dir)
            return True
        return False

    def __change_lwaratio(self):
        if not self.__is_ssh_attach():
            tk.messagebox.showerror('錯誤', '尚未指定 SSH 終端, 無法設定 LWA Ratio')
            return

        try:
            wifi_ratio = int(self.__lwaratio['wifi_var'].get())
            lte_ratio = int(self.__lwaratio['lte_var'].get())
        except:
            self._print_error('LWARatio value is not INT')
            tk.messagebox.showerror('錯誤', '只能輸入數字')
            return

        if wifi_ratio < 0 or lte_ratio < 0:
            self._print_error('LWARatio value is not a positive number')
            tk.messagebox.showerror('錯誤', '只能輸入>0數值')
            return

        if (wifi_ratio - lte_ratio) == 0:
            self._print_error('LWARatio value are all 0')
            tk.messagebox.showerror('錯誤', '數值不能都為0')
            return

        self.__run_command('lwaratio', lte_ratio, wifi_ratio)

    def __change_mcs(self):
        if not self.__is_ssh_attach():
            tk.messagebox.showerror('錯誤', '尚未指定 SSH 終端, 無法設定 MCS')
            return

        try:
            mcs_m = int(self.__mcs['m_var'].get())
            mcs_d = int(self.__mcs['d_var'].get())
            mcs_u = int(self.__mcs['u_var'].get())
        except:
            self._print_error('MCS value is not INT')
            tk.messagebox.showerror('錯誤', '只能輸入數字')
            return

        if mcs_m < 2 or mcs_m > 3:
            self._print_error('MCS m value must be 2 or 3')
            tk.messagebox.showerror('錯誤', 'M值需要為2或3')
            return

        if mcs_d < 9 or mcs_d > 28:
            self._print_error('MCS DL value must be between 9 and 28')
            tk.messagebox.showerror('錯誤', 'DL值需要為9~28')
            return

        if mcs_u < 9 or mcs_u > 20:
            self._print_error('MCS UL value must be between 9 and 20')
            tk.messagebox.showerror('錯誤', 'DL值需要為9~20')
            return

        self.__run_command('chmgs', mcs_m, mcs_d, mcs_u)
