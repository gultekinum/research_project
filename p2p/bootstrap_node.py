import socket
import threading
import queue
import sys
import time
from random import randint

lock = threading.Lock()
LOCAL_HOST ="127.0.0.1"
PORT_NUMBER = 9942
class BootstrapNode(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.port_list = set()
        self.server_socket = socket.socket()
        self.host = "0.0.0.0"
        self.port = PORT_NUMBER
        self.server_socket.bind((self.host,self.port))
        self.server_socket.listen()
        print("bootstrap node started. listening port:{}".format(self.port))
    def run(self):
        while True:
            try:
                conn_socket, addr = self.server_socket.accept()
                data = conn_socket.recv(1024).decode()
                msg = data.split()
                if msg[0] =="RDY":
                    print("connection request received by node, {}".format(addr))
                    self.port_list.add(msg[1])
                    print("accepting new node working on port, {}".format(msg[1]))
                    conn_socket.send("WEL".encode())
                    ports = " ".join(self.port_list)
                    for port in self.port_list:
                        msg = "LST {}".format(ports)
                        print("sending updated list to all nodes")
                        print(msg)
                        s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                        s.connect((LOCAL_HOST,int(port)))
                        s.send(msg.encode())
            except:
                pass
                
                

            


if __name__=="__main__":
        n = BootstrapNode()
        n.start()