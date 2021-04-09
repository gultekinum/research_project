import socket
import threading
import queue
import sys
import time
from random import randint
import uuid

lock = threading.Lock()
PORT_NUMBER = 9964
IP_NUMBER ="127.0.0.1"
class Node(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.id = uuid.uuid4()
        self.node_dict = {}

    def run(self):
        print("node started. listening port:{}".format(self.port))
        self.clientSocket.connect(("127.0.0.1",9090))
        self.bootstrap_socket = socket.socket()
        serverSocket.bind(("127.0.0.1",9090));

        serverSocket.listen();
        while True:
            
            conn_socket, addr = self.server_socket.accept()
            thread_qu = queue.Queue()
            read_thr = ReadThread(conn_socket,addr,thread_qu)
            write_thr = WriteThread(conn_socket,addr,thread_qu)
            read_thr.start()
            write_thr.start()




class ReadThread(threading.Thread):
    def __init__(self,conn,addr,write_qu):
        threading.Thread.__init__(self)
        self.conn = conn
        self.write_qu = write_qu
        self.addr=addr
    def run(self):
        print("Connection established with" + str(self.addr) + ", ReadThread started.")
        while True:
            msg = self.conn.recv(1024).decode()
            if msg=="WEL":
                self.write_qu.put()
            print("added to queue {}".format(msg))

class WriteThread(threading.Thread):
    def __init__(self,conn,addr,write_qu):
        threading.Thread.__init__(self)
        self.conn = conn
        self.write_qu = write_qu
        self.addr=addr
    def run(self):
        while True:
            send_msg = self.write_qu.get()
            send_msg = send_msg.rstrip("\n")
            send_msg = send_msg+"\n"
            
            self.conn.send(send_msg.encode())

if __name__=="__main__":
    for i in range(10):
        n = Node()
        n.start()