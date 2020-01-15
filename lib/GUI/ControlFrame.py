import tkinter as tk
from tkinter import ttk
from tkinter import *
from enum import Enum
from lib.logger.LoggerPrinter import LoggerPrinter

class ControlFrame(ttk.LabelFrame, LoggerPrinter):

    class BtnId(str, Enum):
        CONNECT = 'connect'
        STARTUP = 'startup'
        STOP = 'stop'
        SHUTDOWN = 'shutdown'
        UPDATE_L1 = 'update_l1'
        UPDATE_L3 = 'update_l3'
        L2GUI = 'l2gui'

    def __init__(self, logger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._logger = logger
        self._logger_class = 'ControlFrame'

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.__buttons = {}
        self.__buttons[self.BtnId.CONNECT] = ttk.Button(self,text='連接終端', width=15, command=self.__btn_connect)
        self.__buttons[self.BtnId.STARTUP] = ttk.Button(self,text='啟動eNB程式', width=15, command=self.__btn_startup)
        self.__buttons[self.BtnId.STOP] = ttk.Button(self, text='關閉eNB程式', width=15, command=self.__btn_stop)
        self.__buttons[self.BtnId.SHUTDOWN] = ttk.Button(self, text='eNB關機', width=15, command=self.__btn_shutdown)
        self.__buttons[self.BtnId.UPDATE_L1] = ttk.Button(self, text='上傳L1/L2 Images', width=15, command=self.__btn_update_l1)
        self.__buttons[self.BtnId.UPDATE_L3] = ttk.Button(self, text='上傳L3 Images', width=15, command=self.__btn_update_l3)
        self.__buttons[self.BtnId.L2GUI] = ttk.Button(self,text='啟用流量圖表', width=15, command=self.__btn_L2GUI)

        self.__set_btn_state([1,0,0,0,0,0,0])

        self.__buttons[self.BtnId.CONNECT].grid(row=0, column=0, rowspan=2, sticky='ns')
        self.__buttons[self.BtnId.STARTUP].grid(row=0, column=1, rowspan=2, sticky='ns')
        self.__buttons[self.BtnId.STOP].grid(row=0, column=2, rowspan=2, sticky='ns')
        self.__buttons[self.BtnId.SHUTDOWN].grid(row=0, column=3, rowspan=2, sticky='ns')
        self.__buttons[self.BtnId.UPDATE_L1].grid(row=0, column=4, sticky='ne')
        self.__buttons[self.BtnId.UPDATE_L3].grid(row=1, column=4, sticky='se')
        self.__buttons[self.BtnId.L2GUI].grid(row=0, column=5, rowspan=2, sticky='ns')

        self.__btn_callback = {}

    def __btn_connect(self):
        self.__ask_operation(btn_id=self.BtnId.CONNECT,
                             state=[0,1,0,0,1,1,1],
                             ask_title='連接終端機',
                             ask_content='連接ITRI Small Cell前，請先確定連線正常！',
                             ask_type=tk.messagebox.WARNING,
                             fail_content='連線失敗，無法連接終端機')

    def __btn_startup(self):
        self.__ask_operation(btn_id=self.BtnId.STARTUP,
                             state=[0,0,1,1,0,0,0],
                             ask_title='啟動eNB',
                             ask_content='自動執行設定檔上開機指令，以啟動eNB',
                             ask_type=tk.messagebox.WARNING)

    def __btn_stop(self):
        self.__ask_operation(btn_id=self.BtnId.STOP,
                             state=[0,1,0,1,1,1,-1],
                             ask_title='關閉eNB',
                             ask_content='自動中斷目前eNB執行與本機執行程式',
                             ask_type=tk.messagebox.WARNING)

    def __btn_shutdown(self):
        self.__ask_operation(btn_id=self.BtnId.SHUTDOWN,
                             state=[0,0,0,0,0,0,0],
                             ask_title='eNB關機',
                             ask_content='對ITRI Small Cell下達poweroff',
                             ask_type=tk.messagebox.WARNING)

    def __btn_L2GUI(self):
        self.__ask_operation(btn_id=self.BtnId.L2GUI,
                             state=[-1, -1, -1, -1, -1, -1, 0],
                             ask_title='啟用流量圖表',
                             ask_content='僅用於手動連接、手動輸入指令時，圖表無自動啟用時使用',
                             ask_type=tk.messagebox.WARNING,
                             fail_content='無法啟用圖表')

    def __btn_update_l1(self):
        self.__ask_operation(btn_id=self.BtnId.UPDATE_L1,
                             state=[-1, -1, -1, -1, -1, -1, -1],
                             ask_title='上傳Image',
                             ask_content='上傳L1 Image, 執行結果於Bash中顯示',
                             ask_type=tk.messagebox.WARNING,
                             fail_content='無法執行命令')

    def __btn_update_l3(self):
        self.__ask_operation(btn_id=self.BtnId.UPDATE_L3,
                             state=[-1, -1, -1, -1, -1, -1, -1],
                             ask_title='上傳Image',
                             ask_content='上傳L3 Image, 執行結果於Bash中顯示',
                             ask_type=tk.messagebox.WARNING,
                             fail_content='無法執行命令')

    def __btn_click(self, btn_id, state):
        callback = self.__btn_callback.get(btn_id)
        if callback is None:
            self._print_error('button %s id callback is not exist' % btn_id)
            return
        self.__set_btn_state(state)
        return callback()

    def __ask_operation(self, btn_id, state, ask_title, ask_content, ask_type, fail_title='錯誤', fail_content='其他任務目前正在執行或任務中斷'):
        reset_state = self.__get_btn_state()
        reply = tk.messagebox.askquestion(ask_title, ask_content, icon = ask_type)
        if reply == tk.messagebox.YES:
            result = self.__btn_click(btn_id, state)
        else:
            return

        if result is False:
            tk.messagebox.showerror(fail_title, fail_content)
            self._print_error(reset_state)
            if reset_state:
                self.__set_btn_state(reset_state)

    """
    1 = NORMAL
    0 = DISABLED
    -1 = DNOT CARE
    """
    def __set_btn_state(self, state):
        id = 0
        for btn_name in self.BtnId:
            if state[id] == 0:
                self.__buttons[btn_name]['state'] = tk.DISABLED
            if state[id] == 1:
                self.__buttons[btn_name]['state'] = tk.NORMAL
            id+=1

    def __get_btn_state(self):
        state = []
        for btn_name in self.BtnId:
            if str(self.__buttons[btn_name]['state']) == 'disabled':
                state.append(0)
            if str(self.__buttons[btn_name]['state']) == 'normal':
                state.append(1)
        return state

    def set_callback(self, btn_id, callback):
        if btn_id not in self.BtnId:
            self._print_error('button %s id is not exist' % btn_id)
            return
        self.__btn_callback[btn_id] = callback
        self._print_debug('button %s callback is set' % btn_id)

if __name__ == '__main__':
    r = tk.Tk()
    b = ControlFrame(master=r, text='系統功能')
    b.grid()

    def func():
        print('hello!')

    b.set_callback('startup', func)
    b.set_callback('stop', func)
    b.set_callback('shutdown', func)
    b.set_callback('update_l1', func)
    b.set_callback('update_l3', func)
    r.mainloop()
