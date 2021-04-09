import socket
import threading
import queue
import sys
import time
from random import randint
import uuid

lock = threading.Lock()

class Node(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.thread_qu = queue.Queue()
        self.id=uuid.uuid4()
        self.nodes = {}
        self.read_port = -1
        self.bn_port = 9999
        self.bn_ip="127.0.0.1"
    def run(self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((self.bn_ip,self.bn_port))

        r = Reader(thread_qu)
        self.read_port = r.port
        r.start()
        msg = str(self.read_port)+"__"+str(self.id)
        clientSocket.send(msg.encode())
        
            



class Reader(threading.Thread):
    def __init__(self,thread_qu):
        threading.Thread.__init(self):
        self.server_socket = socket.socket()
        self.host = "0.0.0.0"
        self.port = randint(1000,5000)
        self.server_socket.bind((self.host,self.port))
        self.server_socket.listen()
        self.thread_qu = thread_qu
    def run(self):
        while True:
            conn_socket, addr = self.server_socket.accept()
            msg = self.conn.recv(1024).decode()
            print(msg)


