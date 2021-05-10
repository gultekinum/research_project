import hashlib

class Block:
    def __init__(self,prev_hash,block_hash,transactions,nonce):
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.block_hash = block_hash 
        self.nonce = nonce
    def one_display(self):
        data = "\nNonce:{}\nBlock hash:{}\nTransaction record:\n{}\n".format(self.nonce,self.block_hash,"\n".join(self.transactions))
        print(data)
    def get_data(self):
        data = "\nNonce:{}\nPrev hash:{}\nBlock hash:{}\nTransaction record:\n{}\n".format(self.nonce,self.prev_hash,self.block_hash,"\n".join(self.transactions))
        return data
