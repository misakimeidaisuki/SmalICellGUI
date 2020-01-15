import tkinter as tk
from tkinter import ttk
from tkinter import *

from lib.logger.LoggerPrinter import LoggerPrinter

class UEListFrame(ttk.LabelFrame, LoggerPrinter):
    def __init__(self, logger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._logger = logger
        self._logger_class = 'FunctionFrame'

        self.__UE_list = {}

        self.__listbox = tk.Listbox(self, selectmode=tk.SINGLE)
        self.__listbox.insert(tk.END, [])
        self.__listbox.bind('<<ListboxSelect>>', self.__onselect)
        self.__listbox.grid(row=0, column=0, rowspan=4)

        self.__mmeid_text = StringVar()
        self.__imsi_text = StringVar()
        self.__mtmsi_text = StringVar()
        self.__ueIP_text = StringVar()

        frame1 = ttk.Frame(self)
        label1 = ttk.Label(frame1, text='MME ID:', width=7)
        label1.pack(side='left', padx=50)

        label_mmeid = ttk.Label(frame1, textvariable=self.__mmeid_text, width=15)
        label_mmeid.pack(side='left', fill='x', expand=True)
        frame1.grid(row=0,column=1)

        frame2 = ttk.Frame(self)
        label2 = ttk.Label(frame2, text='IMSI:', width=7)
        label2.pack(side='left', padx=50)
        label_mmeid = ttk.Label(frame2, textvariable=self.__imsi_text, width=15)
        label_mmeid.pack(side='left', fill='x', expand=True)
        frame2.grid(row=1,column=1)

        frame3 = ttk.Frame(self)
        label3 = ttk.Label(frame3, text='M-TMSI:', width=7)
        label3.pack(side='left', padx=50)
        label_mmeid = ttk.Label(frame3, textvariable=self.__mtmsi_text, width=15)
        label_mmeid.pack(side='left', fill='x', expand=True)
        frame3.grid(row=2,column=1)

        frame4 = ttk.Frame(self)
        label4 = ttk.Label(frame4, text='IP:', width=7)
        label4.pack(side='left', padx=50)
        label_mmeid = ttk.Label(frame4, textvariable=self.__ueIP_text, width=15)
        label_mmeid.pack(side='left', fill='x', expand=True)
        frame4.grid(row=3, column=1)

    def add_UE(self, MMEID, IMSI='', MTMSI='', IP=''):
        self.__UE_list[MMEID] = {'IMSI': IMSI, 'MTMSI': MTMSI, 'IP': IP}
        self.__refresh()


    def modify_UE(self, MMEID, IMSI=None, MTMSI=None, IP=None):
        try:
            if IMSI: self.__UE_list[MMEID]['IMSI'] = IMSI
            if MTMSI: self.__UE_list[MMEID]['MTMSI'] = MTMSI
            if IP: self.__UE_list[MMEID]['IP'] = IP
        except KeyError:
            self._print_error('the mmeid is not in the list')
        self.__refresh()

    def del_UE(self, MMEID):
        try:
            del self.__UE_list[MMEID]
        except KeyError:
            self._print_error('the mmeid is not in the list')
        self.__refresh()

    def __refresh(self):
        selection = self.__listbox.curselection()
        current_index = int(selection[0]) if len(selection) else 0

        self.__listbox.delete(0, tk.END)
        for mmeid in self.__UE_list.keys():
            self.__listbox.insert(tk.END, mmeid)

        self.__select(current_index)
        self.__update_info(self.__listbox.get(current_index))


    def __onselect(self, event):
        widget = event.widget
        index = int(widget.curselection()[0])
        value = widget.get(index)
        self.__update_info(value)

    def __update_info(self, mmeid):
        if mmeid in self.__UE_list:
            self.__mmeid_text.set(mmeid)
            self.__imsi_text.set(self.__UE_list[mmeid]['IMSI'])
            self.__mtmsi_text.set(self.__UE_list[mmeid]['MTMSI'])
            self.__ueIP_text.set(self.__UE_list[mmeid]['IP'])

    def __select(self, index):
        self.__listbox.select_clear(0, tk.END)
        self.__listbox.selection_set(index)
        self.__listbox.see(index)
        self.__listbox.activate(index)
        self.__listbox.selection_anchor(index)
