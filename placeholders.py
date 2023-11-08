class Node:
    ...

class SensorData:
    ...
    # generate data from 8 sensors

class NDNLayer:
    def __init__(self, id, comm, crypto):
        self.id = id
        self.comm = comm
        self.crypto = crypto
        self.register_callbacks()
        self.neighbor_table = set() # FIB
        self.cache = set() # Content store
        self.pit = {}

    def send_hellos(self):
        self.comm.send(add, port, "hello from {id}")

    def callback_rx_hello(self, data):
        # parse data to get neighbor details
        # self.neighbor_table.add(neighbor_details)
        ...

    def callback_rx_data(self):
        ...

    def register_callbacks(self):
        self.comm.hello_callback = self.callback_rx_hello
        self.comm.data_callback = self.callback_rx_data


class CryptoLayer:
    def encrypt(self):
        ...
    
    def decrypt(self):
        ...
    
    def sign(self):
        ...

    def verify(self):
        ...


class CommunicationLayer:
    def __init__(self, address, port) -> None:
        self.address = address
        self.port = port
        self.hello_callback = None
        self.data_callback = None

    def send(self, destination_address, destination_port, message):
        # spawn client thread to form and send data over TCP sessions
        ...
    
    def recieve(self):
        # start a thread to continuosly listen on self.address and self.port
        
        # handle_client - spawn thread for incoming requests
        #    * check the type of data and execute the relevant callback
        #    * eg: if recv data is hello then execute self.hello_callback(data)
        ...


def main():
    crypto = CryptoLayer()
    comm = CommunicationLayer()

    ndn = NDNLayer(comm, crypto)

    node = Node(ndn)
    node.start()


