import socket
import threading
import queue
import sys
import time
from random import randint
from block import Block

lock = threading.Lock()
LOCAL_HOST ="127.0.0.1"
PORT_NUMBER = int(sys.argv[1])


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
            conn_socket, addr = self.server_socket.accept()
            data = conn_socket.recv(1024).decode()
            msg = data.split()
            if msg[0] =="RDY":
                print("connection request received by node, {}".format(addr))
                self.port_list.add(msg[1])
                print("accepting new node working on port, {}".format(msg[1]))
                node_id = (len(self.port_list)-1)
                response = "WEL {}".format(node_id)
                conn_socket.send(response.encode())
                #conn_socket.send("CHN".encode())

                ports = ":".join(self.port_list)
                for port in self.port_list:
                    msg = "LST {}".format(ports)
                    print("sending updated list to all miner nodes")
                    s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                    s.connect((LOCAL_HOST,int(port)))
                    s.send(msg.encode())
            if msg[0]=="RDY(V)":
                print("connection request received by voter node, {}".format(addr))
                conn_socket.send("WEL".encode())
                ports = ":".join(self.port_list)
                print("sending miner list to voter node")
                msg = "LST {}".format(ports)
                conn_socket.send(msg.encode())

                    
                
                

            


if __name__=="__main__":
        n = BootstrapNode()
        n.start()