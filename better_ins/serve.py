'''
WARNING: Running this may open vulnerabilities for your computer. 
Don't run this if you don't know what you are doing. 
Only run this if you are in a safe network, or inside a firewall. 
I am not responsible if someone attacks your computer through this server. 
'''
print('Loading...')
from interactive import listen
import sys
from myhttp import *
import os
from time import sleep
import qrcode
from threading import Thread
from local_ip import getLocalIP
from osc4py3.as_eventloop import osc_startup, \
    osc_terminate, osc_udp_client, osc_send, osc_process
from osc4py3 import oscbuildparse

PORT = 2349
OSC_PORT = 2333
CLIENT = 'vhwog'

trusted_ip = None

def main():
    osc_startup()
    osc_udp_client('127.0.0.1', OSC_PORT, CLIENT)
    server = MyServer(MyOneServer, PORT, listen = 8)
    server.start()
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    potential_ip = getLocalIP()
    imgs = []
    class ShowImgThread(Thread):
        def __init__(self, img):
            Thread.__init__(self)
            self.img = img
        
        def run(self):
            self.img.show()
    
    potential_ip = {*potential_ip} - {'192.168.56.1'}
    # Cisco Anyconnect shit
    for ip in potential_ip:
        addr = 'http://%s:%d' % (ip, PORT)
        try:
            imgs.append(qrcode.make(addr))
        except Exception as e:
            print('Error 198456', e)
        print(addr)
    print('Ctrl+C to stop.')
    print('Q to display QR code for phone scan.')
    try:
        while True:
            op = listen(timeout = 1)
            if op == b'\x03':
                raise KeyboardInterrupt
            elif op == b'q':
                [ShowImgThread(x).start() for x in imgs]
                print('Loading image.')
            elif op == b'\r':
                print()
    except KeyboardInterrupt:
        print('Received ^C. ')
    finally:
        server.close()
        server.join()
        osc_terminate()

class MyOneServer(OneServer):
    def handle(self, request):
        if request.target == '/':
            with open('index.html', 'rb') as f:
                respond(self.socket, f.read())
        elif request.target == '/style.css':
            with open('style.css', 'rb') as f:
                respond(self.socket, f.read())
        elif request.target == '/main.js':
            with open('main.js', 'rb') as f:
                respond(self.socket, f.read())
        elif request.target in ['/favicon.ico']:
            pass
        else:
            msg = request.target.lstrip('/')
            try:
                _, alpha, beta, gamma = msg.split(',')
                # print(absolute, alpha, beta, gamma)
                msg = oscbuildparse.OSCMessage("/", ",fff", [alpha, beta, gamma])
                osc_send(msg, CLIENT)
                osc_process()
                respond(self.socket, b'Yup')
            except ValueError:
                print('Invalid request:', msg)
                respond(self.socket, b'dirty hacker')

class MyServer(Server):
    def onConnect(self, addr):
        global trusted_ip
        if trusted_ip is None:
            trusted_ip = addr[0]
        elif addr[0] != trusted_ip:
            print('A second IP requested connection! Potential ATTACKER!!!', addr)
            self.close()

if __name__ == '__main__':
    main()
    sys.exit(0)
