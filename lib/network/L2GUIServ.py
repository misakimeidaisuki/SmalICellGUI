import socket
import time

from lib.logger.LoggerPrinter import LoggerPrinter

class L2GUIServ(LoggerPrinter):
    def __init__(self, ip='::', port=1451, type=socket.AF_INET6, size=8192, logger=None):
        self.__ip = ip
        self.__port = port
        self.__type = type
        self.__size = size

        self._logger = logger
        self._logger_class = 'L2GUIServ'

        self.__socket = socket.socket(self.__type, socket.SOCK_DGRAM)

    def run_server(self, callback=None):
        if callback is None:
            self._print_error('No callback handler, exit')
            return

        self.__socket.bind((self.__ip, self.__port))
        self.__socket.settimeout(1)

        base_time = time.time()

        while True:
            delay = time.time() - base_time
            try:
                data, addr = self.__socket.recvfrom(self.__size)
                par_data = self.__parser_data(bytearray(data), delay)
                self._print_debug(bytearray(data))
                self._print_debug(par_data)
                callback(par_data)
            except socket.timeout:
                self._print_debug('Timeout 1s, not data recv')
                callback(None)
            except:
                self._print_error('UDP Server error!')
                break;

    def __parser_data(self, data, delay):
        parser_data = {}
        parser_data['status'] = data[0]
        parser_data['delay'] = delay

        if parser_data['status'] == 132:
            info_length = self.__unsigned_short(int.from_bytes([data[5], data[4]], byteorder='big'))
            parser_data['info_length'] = info_length

            message = bytearray(data[6:]).decode()
            #new String(this.packet.getData(), 6, systeminformationlength.intValue());
            parser_data['message'] = message

        if parser_data['status'] == 135:
            RTLTE = int.from_bytes([data[7], data[6], data[5], data[4]], byteorder='big')
            RTLTE = self.__unsigned_int(RTLTE)

            RTWIFI = int.from_bytes([data[11], data[10], data[9], data[8]], byteorder='big')
            RTWIFI = self.__unsigned_int(RTWIFI)
            LTE_traffic = RTLTE/125
            WIFI_traffic = RTWIFI/125
            Total_traffic = LTE_traffic+WIFI_traffic

            parser_data['LTE_traffic'] = LTE_traffic
            parser_data['WIFI_traffic'] = WIFI_traffic
            parser_data['Total_traffic'] = Total_traffic
            parser_data['LTE_percent'] = round(LTE_traffic/Total_traffic*100) if Total_traffic != 0 else 0
            parser_data['WIFI_percent'] = round(WIFI_traffic/Total_traffic*100) if Total_traffic != 0 else 0

            parser_data['RRLTE'] = self.__unsigned_byte(data[12])
            parser_data['RRWIFI'] = self.__unsigned_byte(data[13])
            parser_data['RSSI'] = data[14]
            parser_data['RSRP'] = self.__unsigned_byte(data[15])
            parser_data['RSRQ']= self.__unsigned_byte(data[16])

        return parser_data

    def __unsigned_int(self, integer):
        return integer & 0xffffffff

    def __unsigned_byte(self, bytes):
        return bytes & 0xff

    def __unsigned_short(self, short_integer):
        return short_integer & 0xffff
