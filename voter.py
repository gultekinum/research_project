#VOTER NODE
#filename: voter.py

import os
import socket,pickle
import threading
import queue
import sys
import time
from random import randint
import uuid
import hashlib
from block import Block
from datetime import datetime
from packets import EntrancePacket,VotePacket,MessagePacket
from rich.console import Console
from rich.table import Column, Table

BTP_PORT_NUMBER = int(sys.argv[1])
LOCAL_HOST ="127.0.0.1"
DEGREE = 5
BLOCK_SIZE = 10
SEED_INTERVAL = 5000000

class Listener(threading.Thread):
    def __init__(self,port,lqu):
        threading.Thread.__init__(self)
        self.lqu = lqu
        self.port = port
    def run(self):
        while True:
            server_socket = socket.socket()
            server_socket.bind((LOCAL_HOST,self.port))
            server_socket.listen()
            while True:
                conn_socket, addr = server_socket.accept()
                data = conn_socket.recv(4096)
                pack = pickle.loads(data)
                self.lqu.put(data)


class Sender(threading.Thread):
    def __init__(self,port,squ):
        threading.Thread.__init__(self)
        self.entr_pack = EntrancePacket(0,0,0,0)
        self.squ = squ
        self.port = port
        self.votes = []
        self.cycle = 0
    def run(self):
        self.entr_pack = self.join_network()
        self.votes = self.read_file()
        self.bcast_vote()
        while True:
            data = self.squ.get()
            pack = pickle.loads(data)
            if pack.identifier=="NXT":
                if len(self.votes)==0:
                    print("no vote left in repository..")
                else:
                    self.cycle+=1
                    self.bcast_vote()
            if pack.identifier=="LST":
                self.entr_pack.node_list=pack.content

    def join_network(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
            print("\n=========JOINING NETWORK========")
            print("trying to connect bootstrap node.")
            conn.connect((LOCAL_HOST,BTP_PORT_NUMBER))
            
            snd_pack = MessagePacket("RDY",self.port)
            snd_str = pickle.dumps(snd_pack)
            conn.send(snd_str)

            data = conn.recv(4096)
            entr_pack = pickle.loads(data)
            print("joined network. entrance packet received by bootstrap.")
            print("=================================\n")
            return entr_pack

    def bcast_vote(self):
        snd_votes=[]
        if len(self.votes)==0:
            print("no vote left in repo..")
            return False
        else:
            if BLOCK_SIZE>len(self.votes):
                snd_votes=self.votes
                self.votes=[]
            else:
                snd_votes = self.votes[0:BLOCK_SIZE]
                self.votes=self.votes[BLOCK_SIZE:]
            snd_pack = VotePacket(datetime.now(),0,DEGREE,snd_votes,
            self.cycle)
            console = Console()
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Vote Data")
            table.add_row("\n".join(snd_votes))
            print("\n=====BROADCASTING CYCLE[{}]=====".format(self.cycle))
            print("next cycle signal received from bootstrap")
            console.print(table)
            print("=================================\n")
            for port in self.entr_pack.node_list:
                if port!=self.port:
                    snd_str = pickle.dumps(snd_pack)
                    s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                    self.send_packet(snd_str,port)
                    snd_pack.seed += SEED_INTERVAL

    def send_packet(self,pack,port):
        try:
            s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
            s.connect((LOCAL_HOST,int(port)))
            s.send(pack)
        except:
            print("connection to node[{}] failed.".format(port))

    def read_file(self):
        f = open("vote_list.txt","r")
        vote_data = f.read().split("\n")
        return vote_data

if __name__=="__main__":
    lqu = queue.Queue()
    squ = queue.Queue()
    port = randint(1000,5000)
    l = Listener(port,lqu)
    l.start()
    s = Sender(port,squ)
    s.start()
    while True:
        data = lqu.get()
        pack = pickle.loads(data)
        squ.put(data)
        
        
