import serial as serial
import threading
import queue as queue
import Queue
from time import sleep, time
from signal import pause
import urllib
import requests
import json
import paho.mqtt.client as paho
import ssl
import sys

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



def on_connect(client, userdata, flags, rc):
    global connflag
    connflag = True
    print("Connection returned result: " + str(rc) )

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message

awshost = "a3vq3t01rvglnj-ats.iot.us-west-2.amazonaws.com"
awsport = 8883
clientId = "sensorData"
thingName = "sensorData"
caPath = "./AmazonRootCA1.pem.crt"
certPath = "./ca50e7965e-certificate.pem.crt"
keyPath = "./ca50e7965e-private.pem.key"

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqttc.connect(awshost, awsport, keepalive=60)
mqttc.loop_start()


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
    print('msg is ' + msg)
    payload = '{\"text\":\"' + msg + '\"}'
    payload = payload.encode("ascii")
    request = urllib.request.Request(
        tele_url,
        data=payload,
        method="POST"
    )
    request.add_header(
        "Content-Type",
        "application/json"
    )
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
    output_queue.queue.clear()


def send_MQTT():
    mqttc.publish("cmj/F87AEF00000025C3/rpc",
                  '{"rpc_cmd":"zigbee_zcl_ha_ON_OFF_On","rpc_id":1564029017300,"rpc_param":{"euinwk_endpoint_list":[{"endpoint":1,"euinwk":"000D6F000AF1A964"}],"sequence":15}}',
                  qos=1)
    sleep(5)
    mqttc.publish("cmj/F87AEF00000025C3/rpc",
                  '{"rpc_cmd":"zigbee_zcl_ha_ON_OFF_On","rpc_id":1564029017300,"rpc_param":{"euinwk_endpoint_list":[{"endpoint":1,"euinwk":"000D6F000AF1A964"}],"sequence":15}}',
                  qos=1)
    output_queue.queue.clear()

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
                sleep(60)
                #write_uart()
                send_MQTT()
                global rcount
                rcount += 1
                publish_to_telegram('Reboot count is '+str(rcount))
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
