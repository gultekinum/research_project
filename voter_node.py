import socket,pickle
import threading
import queue
import sys
import time
from random import randint
import uuid
import time
from packets import VotePacket,IdentityPacket,MessagePacket

lock = threading.Lock()
BTP_PORT_NUMBER = int(sys.argv[1])
LOCAL_HOST ="127.0.0.1"
class Node(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.id = uuid.uuid4()
        self.node_dict = {}
        self.port = randint(1000,5000)
        self.list = []
        self.broadcast_size = 10
    def run(self):
        data = ""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("node started. sending RDY message to bootstrap node.")
        s.connect((LOCAL_HOST,BTP_PORT_NUMBER))
        snd_pack = MessagePacket("RDY",self.port)
        snd_str = pickle.dumps(snd_pack)
        s.send(snd_str)
        
        data = s.recv(4096)
        pack = pickle.loads(data)

        
        if data=="WEL":
            msg = s.recv(1024).decode().split()
            if msg[0]=="LST":
                parsed = msg[1].split(":")
                print("accepted by bootstrap node. getting list of miner nodes.")
                self.list=[]
                print("node list received by bootstrap node.")
                for port in parsed:
                    self.list.append(port)
                f = open("vote_list.txt","r")
                vote_data = f.read().split("\n")
                cycle = 0
                for i in range(0,len(vote_data)-self.broadcast_size,self.broadcast_size):
                    time.sleep(5)
                    vote_partial = vote_data[i:i+self.broadcast_size]
                    votes = "\n".join(vote_partial)
                    msg = "VTS {}\n{}".format(cycle,votes)
                    print("Broadcasting {} votes to all miners.".format(self.broadcast_size))
                    print(msg)
                    self.broadcast(msg)
                    cycle+=1
                self.broadcast("FIN")
                        
    def broadcast(self,msg):
        for port in self.list:
            s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
            s.connect((LOCAL_HOST,int(port)))
            s.send(msg.encode())          

            

if __name__=="__main__":
    for i in range(1):
        n = Node()
        n.start()