import hashlib
from block import Block
import random

block_size = 10
blockchain = []
degree=5

f = open("vote_list.txt","r")
vote_data = f.read().split("\n")

def compute_nonce(hash_code):
    global block_size,degree
    rule = "0"*degree
    nonce=0
    temp_string = hash_code+str(nonce)
    new_hash = hashlib.sha256(temp_string.encode()).hexdigest()
    while new_hash[0:degree]!=rule:
        nonce+=1
        temp_string = hash_code+str(nonce)
        new_hash = hashlib.sha256(temp_string.encode()).hexdigest()
    return str(nonce)


genesis_block = Block("genesis",["genesis block"],"0000000")
blockchain.append(genesis_block)

block_count = 0

for i in range(0,len(vote_data)-block_size+1,block_size):
    current_hash = blockchain[len(blockchain)-1].block_hash+"".join(vote_data[i:i+block_size])
    validation_nonce = compute_nonce(current_hash)
    block = Block(blockchain[len(blockchain)-1].block_hash,vote_data[i:i+block_size],validation_nonce)
    blockchain.append(block)
    block.get_block_data()
    block_count+=1



