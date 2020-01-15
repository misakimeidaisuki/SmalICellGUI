import tkinter as tk
from tkinter import ttk
from tkinter import *
import threading

from lib.logger.LoggerPrinter import LoggerPrinter

class TerminalFrame(ttk.Frame, LoggerPrinter):
    def __init__(self, logger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__send_func = None
        self.__break_func = None
        self._logger = logger
        self._logger_class = 'TerminalFrame'

        self.grid_propagate(False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.__text = Text(self)
        self.__text.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)

        scrollbar = ttk.Scrollbar(self, command=self.__text.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        self.__text['yscrollcommand'] = scrollbar.set

        self.__text['state'] = tk.DISABLED
        #self.__text.bind("<Key>", lambda e: "break")

        self.__entry = Entry(self)
        self.__entry.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.__entry.bind('<Return>', self.txt_send)
        self.__entry.bind('<Control-c>', self.txt_break)
        self.__entry['state'] = tk.DISABLED

    def set_send_callback(self, callback):
        self.__send_func = callback

    def set_break_callback(self, callback):
        self.__break_func = callback

    def txt_insert(self, text):
        self.__text['state'] = tk.NORMAL
        self.__text.insert(tk.END, text)
        self.__text['state'] = tk.DISABLED
        self.__text.see(tk.END)

    def txt_send(self, event):
        if self.__send_func is None:
            return
        if self.__terminal.get_status() is False:
            self._print_error('(TerminalFrame) terminal process no alive!')
            self.detach_terminal()
            return

        self.__send_func(self.__entry.get())
        self.__entry.delete(0, tk.END)

    def txt_break(self, event):
        self._print_debug('(TerminalFrame) push ctrl+c')
        if self.__break_func is None:
            return
        self.__break_func()
        self.__entry.delete(0, tk.END)

    def attach_terminal(self, terminal):
        self._print_info('attach terminal')
        try:
            self.__terminal = terminal
            self.set_send_callback(self.__terminal.send_message)
            self.set_break_callback(self.__terminal.send_break_signal)

            if not self.__terminal.register_recv_handler(self.txt_insert):
                self._print_error('attach terminal process handler register failed!')

            self.__thread = threading.Thread(target=self.__terminal.recv_message,args=())
            self.__thread.setDaemon(True)
            self.__thread.start()
        except:
            self._print_error('cannot attach terminal process!')
        self.__entry['state'] = tk.NORMAL
        self._print_info('attached terminal process!')

    def detach_terminal(self):
        self.__entry.delete(0, tk.END)
        self.__entry['state'] = tk.DISABLED
        self.__send_func = None
        self.__break_func = None
        self._print_info('detach terminal process!')
