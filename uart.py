import serial as serial
import threading
import queue
from time import sleep, time


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
        self.zigbee_uart = serial.Serial(port='/dev/ttyS1',
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
        data = self.zigbee_uart.readline().strip().decode('utf8')
        return data


if __name__ == '__main__':

    # sudo service pigpiod start
    # sudo service pigpiod stop

    time()
    input_queue = queue.Queue()
    output_queue = queue.Queue()

    sp = SerialProcess()

    while True:
        while not sp.is_open():
            print('port is open')

        try:
            print('Hekko world')
            #t = threading.Thread(target=io_jobs)
            #t.start()
            #pause()
        except Exception:
            sp.close()
            raise
        sp.close()
