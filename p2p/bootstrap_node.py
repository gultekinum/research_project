import socket
import threading
import queue
import sys
import time
from random import randint

lock = threading.Lock()
PORT_NUMBER = 9994
class BootstrapNode(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.conn_list = set()
        self.server_socket = socket.socket()
        self.host = "0.0.0.0"
        self.port = PORT_NUMBER
        self.server_socket.bind((self.host,self.port))
        self.server_socket.listen()
        print("bootstrap node started. listening port:{}".format(self.port))
    def run(self):
        while True:
            conn_socket, addr = self.server_socket.accept()
            conn_socket.send("WEL".encode())
            for conn in self.conn_list:
                msg = "UPDATE:{} joined to network.\n".format(addr)
                conn.send(msg.encode())
            self.conn_list.add(conn_socket)


if __name__=="__main__":
        n = BootstrapNode()
        n.start()