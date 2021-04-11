import socket
import threading
import queue
import sys
import time
from random import randint
import uuid

lock = threading.Lock()
BTP_PORT_NUMBER = 9937
LOCAL_HOST ="127.0.0.1"
class Node(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.id = uuid.uuid4()
        self.node_dict = {}
        self.node_port = randint(1000,5000)

    def run(self):
        data = ""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("node started. sending RDY message to bootstrap node.")
            s.connect((LOCAL_HOST,BTP_PORT_NUMBER))
            msg = "RDY {}".format(self.node_port)
            s.send(msg.encode())
            data = s.recv(1024).decode()
        if data=="REJ":
            print("rejected by bootstrap node.")
        elif data=="WEL":
            print("accepted by bootstrap node. starting to listening port {}".format(self.node_port))
            server_socket = socket.socket()
            server_socket.bind((LOCAL_HOST,self.node_port))
            server_socket.listen()
            while True:
                conn_socket, addr = server_socket.accept()
                msg = conn_socket.recv(1024).decode().split()
                if msg[0]=="LST":
                    self.list=[]
                    print("node list received by bootstrap node.")
                    for port in msg[1:]:
                        self.list.append(port)
                    lst = " ".join(self.list)
                    
                    print("read thread list updated.\n{}".format(self.list))
                if msg[0]=="VTS":
                    print(msg[1:])

if __name__=="__main__":
    for i in range(1):
        n = Node()
        n.start()