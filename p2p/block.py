import hashlib

class Block:
    def __init__(self,prev_hash,block_hash,transactions,nonce):
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.block_hash = block_hash 
        self.nonce = nonce
    def display(self):
        print("\nNonce:{}\nPrev hash:{}\nBlock hash:{}".format(self.nonce,self.prev_hash,self.block_hash))
        print("Transaction record:")
        print("\n".join(self.transactions))