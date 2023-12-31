import socket
import threading
import time


class Node:
    '''
    Application Layer

    This class links sensor data with NDN.
    '''
    def __init__(self, node_id, node_ip, node_port) -> None:
        conn = CommunicationLayer(node_ip, node_port)
        crypto = CryptoLayer()
        self.ndn = NDNLayer(node_id, conn, crypto)

    def start(self, peers):
        self.ndn.start_receivers()
        self.ndn.keep_alives(peers)


class SensorData:
    '''
    take 8 medical parameters of measurement of human body eg; heartrate, blood pressure, etc. 
    generate random data for those 8 sensors
    
    '''
    def __init__(self):
        ...

    def get_data(self, data_id):
        '''
        return data based on data_id
        data_id will have hierarchy

        eg; 
        /data/wristband/2/sensor/ will give data for all sensors
            {
                "heartrate": "xyz",
                "temperature": "xyz",
                "blood_pressure": "xyz",
            }
        /data/wristband/2/sensor/heart will give
             {
                "heartrate": "xyz"
            }   
        
        Write python code which can flexibly change amount of details as per requirement (see examples above)
        '''
    

class Actuator:
    '''
    change value of data as per command.
    '''



class NDNLayer:

    def __init__(self, id, conn, crypto):
        self.id = id
        self.conn = conn
        self.crypto = crypto
        self.register_callbacks()
        self.fib = {} # FIB
        self.cache = set() # Content store
        self.pit = {} # pending interest table 
        self.prt = [] # Pending request table
    
    def start_receivers(self):
        self.conn.listen()

    def keep_alives(self, peers):
        while True:
            for (destination_address, destination_port) in peers:
                self.send_hello(destination_address, destination_port)
                print("NEIGHBORS:", self.fib)
            time.sleep(5)
    
    def send_hello(self, destination_address, destination_port):
        self.conn.send(destination_address, destination_port, f"|HELLO|{self.id}|{self.conn.port}|{self.conn.address}|")

    def hello_callback(self, data):
        '''
        when hello packet will be received by client, CommunicationLayer will make a callback to this function.

        hello packet = |HELLO|nodeID|server port|serverIP|

        this function will add mapping of node ID: port and IP in FIB table.

        FIB: 
        {
        node1:{ip:<>, port:<>, certificate:<>},
        node2:{ip:<>, port:<>, certificate:<>},...
        }

        '''

        s_data = data.split("|")
        nodeID, server_port, server_IP = s_data[2], s_data[3], s_data[4]

        self.fib[nodeID] = {"serverIP":server_IP}
        self.fib[nodeID]["server_port"] = server_port


    def interest_callback(self, data):
        '''
        when interest packet will be received by client, CommunicationLayer will make a callback to this function.

        interest_packet = |INTEREST|nodeID|dataID|num|

        if dataID exists in cache or owner of data:
            create a data packet and make a function call to send of Communication class.
                data_packet = |DATA|<data>|data_ID|
                (data_packet, DST IP, DST Port) ---> pass to send
        else (Cache Miss):
            check if duplicate request:
                if yes, drop the request
            check if retry:
                update num by 1 and function call to send_data
            check if new request:
                > add to PIT
                    PIT_entry = |data_ID|neighbor node_ID|num|
                > construct interest packet with self node ID and forward to all neighbors except where it came from.
                    interest_packet = |INTEREST|self node ID| data ID|num|
                    construct (interest_packet, DST IP, DST port) ---> pass to send function     
        '''


    def data_callback(self, data):
        '''
        if node is requester:
            then remove entry from PRT and print that data is received.
        if node is not requester and data needs to be forwarded:
            create a for loop to forward the data to all the neighbors except where it came from.
                data_packet = |DATA|<data>|data_ID|
                construct (data_packet, DST IP, DST port) ---> pass to send function
        '''
    

    def register_callbacks(self):
        self.conn.hello_callback = self.hello_callback
        self.conn.data_callback = self.data_callback
        self.conn.interest_callback = self.interest_callback


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
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.hello_callback = None
        self.data_callback = None
        self.interest_callback = None
    
    def listen(self):
        threading.Thread(target=self.t_listen).start()

    def t_listen(self):
        # keep on listening to connections infinitely
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.bind((self.address, self.port))
        peer_socket.listen(1)
        print(f"Peer is listening on {self.address}:{self.port}...")


        while True:
            client_socket, client_address = peer_socket.accept()
            print(f"Connection established with {client_address[0]}:{client_address[1]}")
            
            # call receive thread to extract data
            threading.Thread(target=self.receive, args=(client_socket,)).start()


    def send(self, destination_address, destination_port, message):
        '''
        spawn client thread to form and send data over TCP sessions
        The data packet will be passed from NDNLayer as a function call to CommunicationLayer.
        '''
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            peer_socket.connect((destination_address, destination_port))
            print(f"Sending to peer: '{message}'")
            peer_socket.send(message.encode('utf-8'))
        except Exception:
            print("Failed connection to port", destination_port)
    
    def receive(self, in_socket):
        '''
        start a thread to continuosly listen on self.address and self.port

        if packet has "HELLO":
            execute hello_callback (point to NDNLayer function)
        
        if packet has "DATA":
            execute data_callback
        
        if packet has "INTEREST":
            execute interest_callback

        '''
        data = in_socket.recv(1024).decode('utf-8')
        print(f"Received from peer: '{data}'")

        if "INTEREST" in data:
            self.interest_callback(data)
        
        if "DATA" in data:
            self.data_callback(data)
        
        if "HELLO" in data:
            self.hello_callback(data)
        
        
def main():
    import sys

    print(sys.argv)
    node_id = int(sys.argv[1]) 
    port1 = int(sys.argv[2])
    peers = [("127.0.0.1", int(port)) for port in sys.argv[3:]]

    node = Node(node_id, "127.0.0.1", port1)
    node.start(peers)


"""
Python script to generate topology dictionary for both Raspberry Pis which tells for a given node:
    1. The port to listen on
    2. IP based on RPi
    3. Peers to which node will send hellos
    4. Distribute nodes between both Pis and have equal representation.
Eg:
    topology = {
        1: {
            "ip": "",
            "port": "",
            "peers": []
        },
        2: {
            "ip": "",
            "port": "",
            "peers": []
        },
    }

Figure out how to use multiprocessing to run Nodes in parallel on both RaspberryPi.
    * Currently every Python script acts as single node but needs to be manually executed.
    * For 5 nodes we will need to execute 5 times.
    * Need to run in parallel on same terminal and save logs in separate files.

"""

if __name__ == "__main__":
    main()

