import re
import time
import threading

from lib.logger.LoggerPrinter import LoggerPrinter

class AnalysisUEInfo(LoggerPrinter):
    def __init__(self, terminal, logger=None):
        self._logger = logger
        self._logger_class = 'AnalysisUEInfo'

        self.__terminal = terminal

        self.__notice_add_callback = []
        self.__notice_del_callback = []

    def register_notice_add(self, callback=None):
        if callable(callback):
            self.__notice_add_callback.append(callback)
            self._print_debug('notice add call back registered!')
            return True
        self._print_error('the arg is not callable')
        return False

    def register_notice_del(self, callback=None):
        if callable(callback):
            self.__notice_del_callback.append(callback)
            self._print_debug('notice del call back registered!')
            return True
        self._print_error('the arg is not callable')
        return False

    def __notice_add(self, *args, **kwargs):
        for callback in self.__notice_add_callback:
            try:
                callback(*args, **kwargs)
            except:
                self._print_error('run add callback %s error' % callback.__name__)

    def __notice_del(self, *args, **kwargs):
        for callback in self.__notice_del_callback:
            try:
                callback(*args, **kwargs)
            except:
                self._print_error('run del callback %s error' % callback.__name__)


    def analysis_ue(self, message):
        if self.__ue_attach(message): return
        if self.__ue_deatch(message): return
        if self.__ue_add(message): return

    def send_show(self, delay=10):
        time.sleep(delay)
        self.__terminal.send_message('show')

    def __ue_attach(self, message):
        regex = r"\(MME ID, ENB ID\) = \((\d{5},\s\d{1})\)"
        match = re.search(regex, message)
        if match is None:
            return False

        if len(match.groups()) == 1:
            mmeid = match.group(1)
            self.__shutdown_thread = threading.Thread(target=self.send_show, args=(5,))
            self.__shutdown_thread.setDaemon(True)
            self.__shutdown_thread.start()
            self._print_debug('UE %s attach' % mmeid)
            return True
        return False

    def __ue_deatch(self, message):
        regex = r"s1ap_ctx_release\s\(enb_id=\d{1,3},\smme_id=(\d{5})\)"
        match = match = re.search(regex, message)
        if match is None:
            return False
        if len(match.groups()) == 1:
            mmeid = match.group(1)
            self._print_debug('UE %s deatch' % mmeid)
            self.__notice_del(mmeid)
            return True
        return False

    def __ue_add(self, message):
        regex = r"\((\d{5}),\s+\d{1,3},\s+\d{1,3},\s+\d{1,3}\)\s+(\d{15})\s+([a-h0-9]{8})\s+\d+:\d+:\d+\s+\d+\/\d\s+(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})"
        match = re.search(regex, message)
        if match is None:
            return False
        if len(match.groups()) == 4:
            mmeid = match.group(1)
            imsi = match.group(2)
            mtmsi = match.group(3)
            ip = match.group(4)

            self._print_debug('match UE %s, %s, %s, %s' % (mmeid, imsi, mtmsi, ip))
            self.__notice_add(mmeid, imsi, mtmsi, ip)
            return True
        return False
