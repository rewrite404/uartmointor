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
tele_url = 'https://owwxorolda.execute-api.us-west-2.amazonaws.com/alpha'


start = False
end = False
rcount = 0

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
        data = self.zigbee_uart.readline().strip().decode("utf-8", 'ignore')
        return data


def publish_to_line(msg):
    print('is pushing')
    # print('contant is ' + u_read)
    payload = '{\"bot\":\"eti-dev\",\"to_user\":\"aaron\",\"text\":\"' + msg + '\"}'
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


def publish_to_telegram(msg):
    print('is pushing')
    # print('contant is ' + u_read)
    payload = '{\"name\":value}'
    t_payload = '{ '+'}'
    payload = payload.encode("ascii")
    request = urllib.request.Request(
        tele_url,
        data=t_payload,
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



def read_uart():
    while True:
        #print('is reading')
        u_read = sp.read()
        #publish_to_line(u_read)
        #print('this is=='+u_read+'==')
        if u_read:
            output_queue.put(u_read)
            #print(output_queue.get())
            #print(u_read)
            #print('=========')

def write_uart():
    sp.write('\n')
    sp.write('reboot')


def reboot_count():
    while True:
        #print('thread 2')
        #sleep(1)
        if not output_queue.empty():
            line = output_queue.get()
            print('line is'+line)
            word = line.split(' ')
            if line == 'U-Boot 1.1.3 (Dec  6 2016 - 11:20:23)':
                global start
                start = True
                print('start')
            if line == 'Please press Enter to activate this console.':
                global end
                end = True
                print('end')
            if start == True and end == True:
                start = False
                end =False
                sleep(1)
                write_uart()
                global rcount
                rcount += 1
                publish_to_telegram('reboot count is '+str(rcount))
                print('reeboot')
                print('reboot count'+str(rcount))
            #print('line is'+line)




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
            t2 = threading.Thread(target=reboot_count)
            t1 = threading.Thread(target=read_uart)
            print('t2 started')
            print('t1 started')
            t1.start()
            t2.start()
            pause()
        except Exception:
            sp.close()
            raise
        sp.close()
