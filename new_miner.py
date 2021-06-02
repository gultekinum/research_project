from datetime import datetime
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
from packets import EntrancePacket,VotePacket,MessagePacket,ValPacket


BTP_PORT_NUMBER = int(sys.argv[1])
LOCAL_HOST ="127.0.0.1"
STOP_FLAG = False
NODE_ID = -1
BLOCK_CHAIN = []


class Listener(threading.Thread):
    def __init__(self,port,lqu):
        threading.Thread.__init__(self)
        self.lqu = lqu
        self.port = port
    def run(self):
        global STOP_FLAG
        while True:
            server_socket = socket.socket()
            server_socket.bind((LOCAL_HOST,self.port))
            server_socket.listen()
            while True:
                conn_socket, addr = server_socket.accept()
                data = conn_socket.recv(4096)
                pack = pickle.loads(data)
                print("Packet[{}] received.".format(pack.identifier))
                if pack.identifier=="VAL":
                    print("Cycle[{}] block generated and nonce[{}] found by node[{}] at {} . starting validation..".format(pack.cycle,pack.nonce,pack.founder_id,pack.timestamp))
                    STOP_FLAG = True
                if pack.identifier=="VTS":
                    STOP_FLAG=False

                snd_str = pickle.dumps(pack)
                self.lqu.put(snd_str)


class Sender(threading.Thread):
    def __init__(self,port,wqu):
        threading.Thread.__init__(self)
        self.entr_pack = EntrancePacket(0,0,0,0)
        self.wqu = wqu
        self.port = port
    def run(self):
        global NODE_ID,BLOCK_CHAIN
        self.entr_pack= self.join_network()
        NODE_ID = self.entr_pack.node_id
        BLOCK_CHAIN = self.entr_pack.chain
        while True:
            data = squ.get()
            pack = pickle.loads(data)
            if pack.identifier=="LST":
                self.entr_pack.node_list = pack.content
                print("port list updated:{}".format(self.entr_pack.node_list))
            if pack.identifier=="VAL":
                self.bcast_packet(data)
            if pack.identifier=="OKK":
                self.bcast_packet(data)

    def join_network(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
            print("trying to connect bootstrap node.")
            conn.connect((LOCAL_HOST,BTP_PORT_NUMBER))
            
            snd_pack = MessagePacket("RDY",self.port)
            snd_str = pickle.dumps(snd_pack)
            conn.send(snd_str)

            data = conn.recv(4096)
            entr_pack = pickle.loads(data)
            print("joined network. entrance packet received by bootstrap.")
            return entr_pack

    def bcast_packet(self,pack):
        for port in self.entr_pack.node_list:
            if port != self.port:
                self.send_packet(pack,port)

    def send_packet(self,pack,port):
        try:
            s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
            s.connect((LOCAL_HOST,int(port)))
            s.send(pack)
        except:
            print("connection to node[{}] failed.".format(port))

def generate_block(vote_packet):
    global STOP_FLAG
    rule = "0"*vote_packet.degree
    vote_string = "".join(vote_packet.votes)
    nonce=vote_packet.seed
    temp_string = vote_string+str(nonce)
    new_hash = hashlib.sha256(temp_string.encode()).hexdigest()
    while new_hash[0:vote_packet.degree]!=rule:
        if STOP_FLAG==True:
            return 0
        nonce+=1
        temp_string = vote_string+str(nonce)
        new_hash = hashlib.sha256(temp_string.encode()).hexdigest()
    new_block = Block(0,new_hash,vote_packet.votes,nonce)
    return new_block

def validate(nonce,vote_pack):
        rule = "0"*vote_pack.degree
        vote_string = "".join(vote_pack.votes)
        temp_string = vote_string+str(nonce)
        new_hash = hashlib.sha256(temp_string.encode()).hexdigest()
        if new_hash[0:vote_pack.degree]==rule:
            return True
        else:
            return False

def save_chain():
    file_name = "node{}_chain_file.txt".format(NODE_ID)
    f = open(file_name,"w")
    block_data=""
    for block in BLOCK_CHAIN:
        block_data += block.get_data()
    f.write(block_data)
    f.close()

def add_chain(vote_pack,nonce):
    vote_string = "".join(vote_pack.votes)
    temp_string = vote_string+str(nonce)
    block_hash = hashlib.sha256(temp_string.encode()).hexdigest()
    block = Block(BLOCK_CHAIN[len(BLOCK_CHAIN)-1].block_hash,block_hash,vote_pack.votes,nonce)
    BLOCK_CHAIN.append(block)
    save_chain()


if __name__=="__main__":
    lqu = queue.Queue()
    squ = queue.Queue()
    port = randint(1000,5000)
    l = Listener(port,lqu)
    l.start()
    s = Sender(port,squ)
    s.start()
    vote_pack = VotePacket(0,0,0,0,0)
    val_dict = {}
    active_node_count = 0
    nonce = -1
    wait_next_cycle = True

    while True:
        data = lqu.get()
        pack = pickle.loads(data)
        if pack.identifier=="LST":
            active_node_count=len(pack.content)
            squ.put(data)
        if pack.identifier=="VTS":
            wait_next_cycle = False
            vote_pack = pack
            cycle = pack.cycle
            seed = pack.seed
            t0_start = time.process_time()
            result = generate_block(pack)
            t0_stop = time.process_time()
            if result!=0:
                block=result
                print("============cycle:{} block generated ============\ngenerated by node:{}\nstart seed value:{}, block generated in {} seconds".format(cycle,NODE_ID,seed,t0_stop-t0_start))
                block.one_display()
                print("\n=======================================\n\nsending other nodes for validation.\n")
                val_pack = ValPacket(datetime.now(),NODE_ID,block.nonce,cycle)
                val_str = pickle.dumps(val_pack)
                squ.put(val_str)
        if wait_next_cycle==False:
            if pack.identifier=="VAL":
                if validate(pack.nonce,vote_pack):
                    print("nonce value[{}] validated by node[{}]".format(pack.nonce,NODE_ID))
                    snd_pack = MessagePacket("OKK",pack.nonce)
                    snd_str = pickle.dumps(snd_pack)
                    squ.put(snd_str)
                else:
                    snd_pack = MessagePacket("REJ",pack.nonce)
                    snd_str = pickle.dumps(snd_pack)
                    squ.put(snd_str)
            if pack.identifier=="OKK":
                nonce = pack.content
                print(val_dict)
                if nonce not in val_dict:
                    val_dict[nonce]=1
                else:
                    val_dict[nonce]+=1
                if val_dict[nonce]>=1:
                    add_chain(vote_pack,nonce)
                    val_dict[nonce]=-99999
        else:
            print("waiting next cycle for vote data.")

            

        



