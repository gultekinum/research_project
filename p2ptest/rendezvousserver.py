from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from random import randint

SERVER_PORT=9997
class Server(DatagramProtocol):
    def __init__(self):
        self.clients=set()
    def datagramReceived(self,datagram,addr):
        datagram = datagram.decode("utf-8")
        if datagram=="ready":
            self.clients.add(addr)
            addresses = "\n".join([str(x) for x in self.clients])
            self.transport.write(addresses.encode("utf-8"),addr)
        else:
            print(datagram)
if __name__=="__main__":
    reactor.listenUDP(SERVER_PORT,Server())
    reactor.run()