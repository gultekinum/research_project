#BOOTSTRAP NODE
#filename: bootstrap.py

import socket,pickle
import threading
import queue
import sys
import time
from random import randint
from block import Block
from packets import EntrancePacket,VotePacket,MessagePacket
from datetime import datetime
import hashlib

lock = threading.Lock()
LOCAL_HOST ="127.0.0.1"
PORT_NUMBER = int(sys.argv[1])
DEGREE = 5
BLOCK_CHAIN = []
genesis_block = Block("genesis",["genesis block"],"0",0)
BLOCK_CHAIN.append(genesis_block)

class BootstrapNode(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.port_list = set()
        self.port_list.add(PORT_NUMBER)
        self.server_socket = socket.socket()
        self.host = "0.0.0.0"
        self.port = PORT_NUMBER
        self.server_socket.bind((self.host,self.port))
        self.server_socket.listen()
        self.chain = []
        print("bootstrap node started.listening port:{}".format(self.port))
    def run(self):
        vote_pack = VotePacket(0,0,0,0,0)
        val_dict = {}
        active_node_count = 0
        while True:
            conn_socket, addr = self.server_socket.accept()
            data = conn_socket.recv(4096)
            pack = pickle.loads(data)
            if pack.identifier=="RDY":
                print("\n==========JOIN REQUEST==========")
                print("connection request received by"
                 " node, {}".format(addr))
                print("accepting new node working on"
                " port, {}".format(pack.content))
                self.port_list.add(pack.content)
                active_node_count = len(self.port_list)
                node_id = (len(self.port_list)-1)
                card = EntrancePacket(datetime.now(),node_id,
                self.port_list,BLOCK_CHAIN)
                snd = pickle.dumps(card)
                conn_socket.send(snd)
                print("entrance packet sent to node[{}]".format(node_id))
                print("sending updated list to all miner nodes")
                print("=================================\n")
                snd_pack = MessagePacket("LST",self.port_list)
                snd_str = pickle.dumps(snd_pack)
                self.bcast_packet(snd_str)
            if pack.identifier=="VTS":
                vote_pack = pack
            if pack.identifier=="OKK":
                nonce = pack.content
                if nonce not in val_dict:
                    val_dict[nonce]=1
                else:
                    val_dict[nonce]+=1
                if val_dict[nonce]>=1:
                    self.add_chain(vote_pack,nonce)
                    val_dict[nonce]=-99999
                    snd_pack = MessagePacket("NXT",vote_pack.cycle)
                    snd_str = pickle.dumps(snd_pack)
                    self.bcast_packet(snd_str)
                    

    def bcast_packet(self,pack):
        for port in self.port_list:
            if port != self.port:
                self.send_packet(pack,port)

    def send_packet(self,pack,port):
        try:
            s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
            s.connect((LOCAL_HOST,int(port)))
            s.send(pack)
        except:
            print("\n==============ERROR==============")
            print("connection to node[{}] failed.".format(port))
            print("=================================\n")
        


    def save_chain(self):
        file_name = "bootstrap_chain_file.txt"
        f = open(file_name,"w")
        block_data=""
        for block in BLOCK_CHAIN:
            block_data += block.get_data()
        f.write(block_data)
        f.close()

    def add_chain(self,vote_pack,nonce):
        vote_string = "".join(vote_pack.votes)
        temp_string = vote_string+str(nonce)
        block_hash = hashlib.sha256(temp_string.encode()).hexdigest()
        block = Block(BLOCK_CHAIN[len(BLOCK_CHAIN)-1].block_hash,
        block_hash,vote_pack.votes,nonce)
        BLOCK_CHAIN.append(block)
        self.save_chain()


if __name__=="__main__":
        n = BootstrapNode()
        n.start()