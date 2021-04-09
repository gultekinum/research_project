from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from random import randint

SERVER_PORT = 9997

class Client(DatagramProtocol):
    def __init__(self,host,port):
        #self.id = uuid4()
        if host =="localhost":
            host = "127.0.0.1"
        self.id = host,port
        self.address=None
        self.server='127.0.0.1',SERVER_PORT
        print("working on id:,",self.id)

    def startProtocol(self):
        self.transport.write("ready".encode("utf-8"),self.server)
        
    def datagramReceived(self,datagram,addr):
        datagram = datagram.decode("utf-8")
        
        if addr==self.server:
            print("Choose a client from these \n",datagram)
            self.address = input("write address:"),int(input("write port:"))
            reactor.callInThread(self.send_message)
        else:
            print(addr,":",datagram)
    
    def send_message(self):
        print("sending message to {}".format(self.address))
        self.transport.write(input(":::").encode("utf-8"),self.address)
if __name__=="__main__":
    port = randint(1000,5000)
    reactor.listenUDP(port,Client('localhost',port))
    reactor.run()