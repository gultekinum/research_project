import hashlib

class Block:
    def __init__(self,prev_hash,transac,nonce):
        self.transactions = transac
        self.prev_hash = prev_hash
        temp_string = prev_hash+"".join(transac)+nonce
        self.block_hash = hashlib.sha256(temp_string.encode()).hexdigest()
    def get_block_data(self):
        print("===========================")
        print("Prev hash:{} , Block hash:{}".format(self.prev_hash,self.block_hash))
        print("Transaction record:")
        print("\n".join(self.transactions))