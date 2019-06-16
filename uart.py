import serial as serial
import threading
import queue as queue
from time import sleep, time
from signal import pause
import urllib
import requests
import json

url = 'https://admin.eti.sysop.app/messages/push'
headers = {'Content-Type': 'application/json'}

class SerialProcess:
    def in_waiting(self):
        return self.zigbee_uart.inWaiting()

    def flush_input(self):
        self.zigbee_uart.flushInput()
        return

    def flush_output(self):
        self.zigbee_uart.flushOutput()
        return

    def __init__(self):
        self.zigbee_uart = serial.Serial(port='/dev/ttyS0',
                                         baudrate=57600,
                                         parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_ONE,
                                         bytesize=serial.EIGHTBITS,
                                         writeTimeout=5,
                                         rtscts=False,
                                         timeout=5)

    def is_open(self):
        return self.zigbee_uart.isOpen()

    def close(self):
        self.zigbee_uart.close()

    def write(self, data):
        data += '\r\n'
        self.zigbee_uart.write(data.encode())

    def read(self):
        data = self.zigbee_uart.readline().strip()
        return data


def read_uart():
    while True:
        print('is reading')
        u_read = sp.read()
        print('is pushing')
        contant = u_read.decode("utf-8") 
        #print('contant is ' + u_read)
        payload = '{\"bot\":\"eti-dev\",\"to_user\":\"aaron\",\"text\":\"' + u_read + '\"}'
        payload = payload.encode("ascii")
        request = urllib.request.Request(
            url,
            data=payload,
            method="POST"
        )
        print('request with out header')
        request.add_header(
            "Content-Type",
            "application/json"
        )
        print('request qith header')
        urllib.request.urlopen(request)
        print('pushed to aaron line')
        output_queue.put(u_read)
        if not output_queue.empty():
            print(output_queue.get())
            print('=========')

def write_uart():
    while True:
        data = sp.read()
        output_queue.put(data)
        if not output_queue.empty():
            print(output_queue.get())
            print('=========')


if __name__ == '__main__':
    time()
    input_queue = queue.Queue()
    output_queue = queue.Queue()

    sp = SerialProcess()

    while True:
        while not sp.is_open():
            print('port is not open')
            sleep(5)

        try:
            print('Hello world')
            t = threading.Thread(target=read_uart())
            t.start()
            pause()
        except Exception:
            sp.close()
            raise
        sp.close()
