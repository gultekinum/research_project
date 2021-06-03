#COMMUNICATION PACKETS
#filename: packets.py

import datetime
import hashlib
import random
from time import time


class EntrancePacket:
    def __init__(self,timestamp,node_id,node_list,chain):
        self.identifier = "WEL"
        self.timestamp = timestamp
        self.node_id = node_id
        self.node_list = node_list
        self.chain = chain

class VotePacket:
    def __init__(self,timestamp,seed,degree,votes,cycle):
        self.identifier = "VTS"
        self.timestamp = timestamp
        self.degree=degree
        self.votes = votes
        self.cycle = cycle
        self.seed = seed
class ValPacket:
    def __init__(self,timestamp,founder_id,nonce,cycle):
        self.identifier="VAL"
        self.timestamp = timestamp
        self.founder_id = founder_id
        self.nonce = nonce
        self.cycle = cycle
class MessagePacket:
    def __init__(self,identifier,content):
        self.identifier = identifier
        self.content = content

    