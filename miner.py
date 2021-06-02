from os import stat
import socket,pickle
import threading
import queue
import sys
import time
from random import randint
import uuid
import hashlib
from block import Block
from idcard import IdentityCard

lock = threading.Lock()
BTP_PORT_NUMBER = int(sys.argv[1])
LOCAL_HOST ="127.0.0.1"
SEED_INTERVAL = 1000000
DEGREE=5
BLOCK_CHAIN = []


class Miner:
    global BTP_PORT_NUMBER,LOCAL_HOST,DEGREE
    def __init__(self):
        self.node_port = randint(1000,5000)
        self.list = []
        self.m_queue = queue.Queue()
        self.v_queue = queue.Queue()
        self.id = -1
        self.valid_dict={}
        self.chain = []
        if self.connect_bootstrap():
            print("accepted by bootstrap node. starting to listening port {}".format(self.node_port))
            self.mining = MiningOp(self.m_queue,self.id)
            self.mining.start()
            self.validating = ValidatingOp(self.v_queue,self.id)
            self.validating.start()
            genesis_block = Block("genesis",["genesis block"],"0",0)
            self.chain.append(genesis_block)
            self.run()
            
            
    def run(self):
        global STOP_FLAG
        server_socket = socket.socket()
        server_socket.bind((LOCAL_HOST,self.node_port))
        server_socket.listen()
        while True:
            conn_socket, addr = server_socket.accept()
            raw_msg = conn_socket.recv(1024).decode()
            msg = raw_msg.split()
            if msg[0]=="LST":
                self.list = []
                parsed = msg[1].split(":")
                for port in parsed:
                    self.list.append(port)
                
                print("node list received by bootstrap node, node list updated.\n{}".format(self.list))
                response = "LST "+":".join(self.list)
                self.m_queue.put(response)
                self.v_queue.put(response)
            if msg[0]=="VTS":
                self.m_queue.put(raw_msg)
            if msg[0]=="VAL":
                self.mining.stop_flag=True
                self.v_queue.put(raw_msg)
            if msg[0]=="OKK":
                parsed = raw_msg.split("\n")
                cycle = parsed[0].split()[1]
                nonce = parsed[1]
                founder_id = parsed[2]
                vote_data = parsed[3:]
                if cycle not in self.valid_dict:
                    self.valid_dict[cycle]=1
                else:
                     self.valid_dict[cycle]+=1
                if self.valid_dict[cycle]>(len(self.list)/2):
                    print("=====> at least 51 percent of miners confirmed block. adding to chain.")
                    vote_string = "".join(vote_data)
                    temp_string = vote_string+str(nonce)
                    block_hash = hashlib.sha256(temp_string.encode()).hexdigest()
                    block = Block(self.chain[len(self.chain)-1].block_hash,block_hash,vote_data,nonce)
                    self.chain.append(block)
                    self.valid_dict[cycle]=-99999999999999999999
                    file_name = "node{}_chain_file.txt".format(self.id)
                    f = open(file_name,"w")
                    block_data=""
                    for block in self.chain:
                        block_data += block.get_data()
                    f.write(block_data)
                    f.close()

    def connect_bootstrap(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("trying to connect bootstrap node.")
            s.connect((LOCAL_HOST,BTP_PORT_NUMBER))
            msg = "RDY {}".format(self.node_port)
            s.send(msg.encode())
            state = False
            while True:
                data = s.recv(1024).decode().split()
                if data[0]=="REJ":
                    state = False
                elif data[0]=="WEL":
                    state = True
                    self.id = int(data[1])
                 
                    return True

class MiningOp(threading.Thread):
    def __init__(self,queue,id):
        threading.Thread.__init__(self)
        self.m_queue = queue
        self.id = id
        self.list = []
        self.stop_flag = False
        self.chain = []
    def run(self):
        while True:
            raw_msg = self.m_queue.get()
            if raw_msg[0:3]=="LST":
                self.list = raw_msg[4:].split(":")
            if raw_msg[0:3]=="VTS":
                self.stop_flag = False
                parsed = raw_msg.split("\n")
                cycle = parsed[0].split()[1]
                vote_data = parsed[1:]
                print("cycle:{} node:{} received vote data. starting mining process.\n".format(cycle,self.id))
                t0_start = time.process_time()
                result = self.generate_block(vote_data)
                t0_stop = time.process_time()
                if result!=0:
                    block=result
                    print("============cycle:{} block generated ============\ngenerated by node:{}\nstart seed value:{}, block generated in {} seconds".format(cycle,self.id,self.id*SEED_INTERVAL,t0_stop-t0_start))
                    block.one_display()
                    msg = "VAL {}\n{}\n{}\n{}".format(cycle,self.id,block.nonce,"\n".join(block.transactions))
                    self.broadcast(msg)
                    print("\n=======================================\n\nsending other nodes for validation.\n")

    def generate_block(self,vote_data):
        rule = "0"*DEGREE
        vote_string = "".join(vote_data)
        nonce=self.id*SEED_INTERVAL
        temp_string = vote_string+str(nonce)
        new_hash = hashlib.sha256(temp_string.encode()).hexdigest()
        while new_hash[0:DEGREE]!=rule:
            if self.stop_flag==True:
                return 0
            nonce+=1
            temp_string = vote_string+str(nonce)
            new_hash = hashlib.sha256(temp_string.encode()).hexdigest()
        new_block = Block(0,new_hash,vote_data,nonce)
        return new_block
    def broadcast(self,msg):
        for port in self.list:
            s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
            s.connect((LOCAL_HOST,int(port)))
            s.send(msg.encode())

class ValidatingOp(threading.Thread):
    def __init__(self,queue,id):
        threading.Thread.__init__(self)
        self.v_queue = queue
        self.id = id
        self.list = []
    def run(self):
        while True:
            raw_msg = self.v_queue.get()
            if raw_msg[0:3]=="LST":
                self.list = raw_msg[4:].split(":")
            if raw_msg[0:3]=="VAL":
                parsed = raw_msg.split("\n")
                cycle = parsed[0].split()[1]
                founder_id = parsed[1]
                nonce = parsed[2]
                vote_data = parsed[3:]
                print("cycle:{} block found by node:{}. mining ended, validation starting.\n".format(cycle,founder_id))
                if self.validate(nonce,vote_data):
                    print("cycle:{} block validated by node:{}\n".format(cycle,self.id))
                    print("broadcasting confirmation. validation ended\n")
                    response="OKK {}\n{}\n{}\n{}".format(cycle,nonce,self.id,vote_data)
                    self.broadcast(response)
                else:
                    print("cycle:{} block validation rejected by node:{}\n".format(cycle,self.id))
                    print("broadcasting rejection. validation ended.\n")
                    response="NOK {}\n{}".format(cycle,self.id)
                    self.broadcast(response)
    def validate(self,nonce,vote_data):
        rule = "0"*DEGREE
        vote_string = "".join(vote_data)
        temp_string = vote_string+str(nonce)
        new_hash = hashlib.sha256(temp_string.encode()).hexdigest()
        if new_hash[0:DEGREE]==rule:
            return True
        else:
            return False
    def broadcast(self,msg):
        for port in self.list:
            s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
            s.connect((LOCAL_HOST,int(port)))
            s.send(msg.encode())
if __name__=="__main__":
    miner = Miner()