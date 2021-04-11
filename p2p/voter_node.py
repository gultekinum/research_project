import socket
import threading
import queue
import sys
import time
from random import randint
import uuid
import time

lock = threading.Lock()
BTP_PORT_NUMBER = 9937
LOCAL_HOST ="127.0.0.1"
class Node(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.id = uuid.uuid4()
        self.node_dict = {}
        self.node_port = randint(1000,5000)
        self.list = []
        self.broadcast_size = 10
    def run(self):
        data = ""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("node started. sending RDY message to bootstrap node.")
        s.connect((LOCAL_HOST,BTP_PORT_NUMBER))
        msg = "RDY(V) {}".format(self.node_port)
        s.send(msg.encode())
        data = s.recv(1024).decode()
        if data=="REJ":
            print("rejected by bootstrap node.")
        elif data=="WEL":
            msg = s.recv(1024).decode().split()
            if msg[0]=="LST":
                print("accepted by bootstrap node. getting list of miner nodes.")
                self.list=[]
                print("node list received by bootstrap node.")
                for port in msg[1:]:
                    self.list.append(port)
                f = open("vote_list.txt","r")
                vote_data = f.read().split("\n")
                
                for i in range(0,len(vote_data)-self.broadcast_size,self.broadcast_size):
                    time.sleep(5)
                    vote_partial = vote_data[i:i+self.broadcast_size]
                    votes = "\n".join(vote_partial)
                    for port in self.list:
                        msg = "VTS \n{}".format(votes)
                        print("Broadcasting {} votes to all miners.".format(self.broadcast_size))
                        s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                        s.connect((LOCAL_HOST,int(port)))
                        s.send(msg.encode())
                        
                        

            

if __name__=="__main__":
    for i in range(1):
        n = Node()
        n.start()