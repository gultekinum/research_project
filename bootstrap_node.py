import socket,pickle
import threading
import queue
import sys
import time
from random import randint
from block import Block
from packets import EntrancePacket,VotePacket,MessagePacket
from datetime import datetime

lock = threading.Lock()
LOCAL_HOST ="127.0.0.1"
PORT_NUMBER = int(sys.argv[1])
DEGREE = 5

class BootstrapNode(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.port_list = set()
        self.server_socket = socket.socket()
        self.host = "0.0.0.0"
        self.port = PORT_NUMBER
        self.server_socket.bind((self.host,self.port))
        self.server_socket.listen()
        self.chain = []
        print("bootstrap node started. listening port:{}".format(self.port))
    def run(self):
        while True:
            conn_socket, addr = self.server_socket.accept()
            data = conn_socket.recv(4096)
            pack = pickle.loads(data)

            if pack.identifier=="RDY":
                print("connection request received by node, {}".format(addr))
                print("accepting new node working on port, {}".format(pack.content))
                
                self.port_list.add(pack.content)
                node_id = (len(self.port_list)-1)
                card = EntrancePacket(datetime.now(),node_id,self.port_list,self.chain)
                snd = pickle.dumps(card)
                conn_socket.send(snd)
                print("identity card sent to node[{}]".format(node_id))
                print("sending updated list to all miner nodes")
                snd_pack = MessagePacket("LST",self.port_list)
                snd_str = pickle.dumps(snd_pack)
                for port in self.port_list:
                    try:
                        s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                        s.connect((LOCAL_HOST,int(port)))
                        s.send(snd_str)
                    except:
                        print("connection to node[{}] failed.".format(port))
if __name__=="__main__":
        n = BootstrapNode()
        n.start()