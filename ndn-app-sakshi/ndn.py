import base64
import random
import socket
import threading
import time
from crypto import CryptoLayer
from sensorData import SensorData

class Node: 
    '''
    Application Layer

    This class links sensor data with NDN.
    this layer tells NDNlayer what to do.
    '''
    def __init__(self, node_id, node_ip, node_port, ndn_privatekey, gateway_privatekey, designated_gateway=False, gateway_comm=None) -> None:
        self.id = node_id
        self.network_prefix = "/wristband/"
        self.supportedDataID = f"{self.network_prefix}{self.id}"
        self.sensor_data = SensorData()
        conn = CommunicationLayer(node_ip, node_port)
        crypto = CryptoLayer()
        self.ndn = NDNLayer(node_id, conn, crypto, ndn_privatekey, gateway_privatekey, designated_gateway, gateway_comm)
        self.ndn.get_sensor_data = self.get_sensor_data
        self.ndn.network_prefix = self.network_prefix

    def get_sensor_data(self, dataID):
        if self.supportedDataID in dataID:
            return self.sensor_data.get_data(dataID.replace(self.supportedDataID + "/", ""))

    def start(self, peers):
        self.ndn.start_receivers() # application layer tells NDNlayer to keep listening
        while True:
            time.sleep(2)
            self.ndn.keep_alives(peers) # application layer tells NDNLayer to send keepalives


class NDNLayer:

    def __init__(self, id, conn, crypto, ndn_privatekey, gateway_privatekey, designated_gateway, gateway_comm):
        self.id = id
        self.conn = conn
        self.crypto = crypto
        self.ndn_privatekey, self.ndn_publickey = ndn_privatekey, ndn_privatekey.public_key()
        self.gateway_privatekey, self.gateway_publickey = gateway_privatekey, gateway_privatekey.public_key()
        self.network_prefix = None
        self.designated_gateway = designated_gateway
        self.gateway_comm = gateway_comm
        self.privatekey, self.publickey = CryptoLayer.rsaKeypair()
        self.get_sensor_data = None
        self.register_callbacks()
        self.fib = {} # FIB
        self.cache = set() # Content store
        self.pit = {} # pending interest table  {data_id:num_id)}
        self.gpit = {}
        self.prt = {} # Pending request table   (dataid, req_id)
        self.gprt = set() # Pending request table for gateway forwards
        self.reply_tracker = set() # on each node to track the data reply of their sensor data
        
        self.hellologs = []
        self.interestlogs = []
        self.datalogs = []
        self.gatewaylogs = []
    
    def start_receivers(self):
        self.conn.listen()

    def keep_alives(self, peers):
        for (destination_address, destination_port) in peers:
            self.send_hello(destination_address, destination_port)
    
    def send_hello(self, destination_address, destination_port):
        self.hellologs.append(f"Sending HELLO from Node ID: {self.id} to {destination_address} {destination_port}")
        hello = f"|HELLO|{self.id}|{self.conn.port}|{self.conn.address}|"
        # Generate signature and encode it in base64 format then decode the resultant byte array
        # string ---(sign)---> byte array ---(base64 encode)---> byte array ---(decode)---> string
        signature = CryptoLayer.sign(hello.encode("utf-8"), self.ndn_privatekey).decode("utf-8")

        _, publickey_str = CryptoLayer.exportKey(self.privatekey, self.publickey)
        publickey_str = base64.b64encode(publickey_str.encode("utf-8")).decode("utf-8")
        self.hellologs.append(f"Signing HELLO packet with Node {self.id}'s private key and sending to {destination_address} {destination_port}")
        self.conn.send(destination_address, destination_port, hello + f"{publickey_str}|{signature}|")

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
        nodeID, server_port, server_IP, publickey_str, signature  = int(s_data[2]), int(s_data[3]), s_data[4], s_data[5], s_data[6]

        publickey = CryptoLayer.loadPublicKey(base64.b64decode(publickey_str))

        # Verify signature using public key, add neighbor to FIB if successful
        if CryptoLayer.verify(f"|HELLO|{nodeID}|{server_port}|{server_IP}|".encode("utf-8"), signature, self.ndn_publickey):
            # updating fib to add server port and IP.
            self.fib[nodeID] = {"serverIP":server_IP, "server_port": server_port, "publickey": publickey}
            #print("NEIGHBORS: ", self.fib)


    def interest_callback(self, interest):
        '''
        when interest packet will be received by client, CommunicationLayer will make a callback to this function.

        interest_packet = "|INTEREST|{self.id}|{dataID}|{requestID}|{num}|"

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

        s_interest = interest.split("|")
        # decrypt interest
        nodeID, encrypted = int(s_interest[2]), s_interest[3]
        
        try:
            decrypted = CryptoLayer.decrypt(encrypted, self.privatekey).split("|")
        except Exception:
            self.interestlogs.append(f"Failed to decrypt INTEREST from Node ID: {nodeID} on Node ID: {self.id}")
            return
        
        dataID, request_id, num = decrypted[0], int(decrypted[1]), int(decrypted[2])

        # check if I am the gateway and this is a foreign packet
        if self.designated_gateway and (self.network_prefix not in dataID) and (dataID not in self.gpit):
            self.gpit[dataID] = (request_id, num, nodeID)
            self.gatewaylogs.append(f"Received INTEREST from Node ID: {nodeID} on Node ID: {self.id}")
            self.gatewaylogs.append(f"Decrypting INTEREST from Node ID: {nodeID} on Node ID: {self.id}")
            self.send_gateway_packet(dataID)
        else:
            self.interestlogs.append(f"Received INTEREST from Node ID: {nodeID} on Node ID: {self.id}")
            self.interestlogs.append(f"Decrypting INTEREST from Node ID: {nodeID} on Node ID: {self.id}")
            sensor_data = self.get_sensor_data(dataID)
            if sensor_data:
                if ((dataID, request_id, num) not in self.reply_tracker): # some value came from node's sensor
                    if sensor_data and ((dataID, request_id, num) not in self.reply_tracker):
                        self.reply_tracker.add((dataID, request_id, num))
                        self.send_data(dataID, request_id, sensor_data, nodeID, num)
            else:
                # Add entry to PIT and forward if request not already received
                if (dataID, request_id, num) not in self.pit:
                    self.pit[(dataID, request_id, num)] = nodeID
                    self.forward_interest(nodeID, dataID, request_id, num)
                    #print("Current state of PIT:", self.pit)

    def send_gateway_packet(self, dataID, data=None):
        """
        sends gateway packet to gateway peer

        1. Send EG packet if data is None
        2. Else send EG packet
        """
        
        if data:
            header = f"EG_REPLY"
            to_encrypt = f"{dataID}|{data}"
            encrypted = CryptoLayer.encrypt(to_encrypt.encode("utf-8"), self.gateway_publickey)
            eg_reply_packet = f"{header}|{encrypted}"
            print(f"Sending EG_REPLY from Node ID: {self.id} to gateway peer")
            self.gatewaylogs.append(f"Encrypting EG_REPLY from Node ID: {self.id} to gateway peer")
            self.gatewaylogs.append(f"Sending EG_REPLY from Node ID: {self.id} to gateway peer")
            self.conn.send(self.gateway_comm[0], self.gateway_comm[1], eg_reply_packet)
        else:
            header = f"EG"
            to_encrypt = f"{dataID}"
            encrypted = CryptoLayer.encrypt(to_encrypt.encode("utf-8"), self.gateway_publickey)
            eg_packet = f"{header}|{encrypted}"
            print(f"Sending EG from Node ID: {self.id} to gateway peer")
            self.gatewaylogs.append(f"Encrypting EG from Node ID: {self.id} to gateway peer")
            self.gatewaylogs.append(f"Sending EG from Node ID: {self.id} to gateway peer")
            self.conn.send(self.gateway_comm[0], self.gateway_comm[1], eg_packet)
    
    def gateway_callback(self, gwdata):
        if not self.designated_gateway:
            return
        
        print("GW RECV")
        s_gwdata = gwdata.split("|")

        # decrypt data
        eg_type, encrypted = s_gwdata[0], s_gwdata[1]
        
        # Do nothing if decryption failed
        try:
            decrypted = CryptoLayer.decrypt(encrypted, self.gateway_privatekey)
        except Exception:
            print("GW Decryption failed!")
            self.gatewaylogs("Decryption failed")
            return
        
        if eg_type == "EG":
            dataID = decrypted
            self.gatewaylogs.append(f"Received EG from gateway peer")
            print("Received EG from gateway peer")
            self.send_interest(dataID, 0, gateway_interest=True)
        
        elif eg_type == "EG_REPLY":
            dataID, sensor_data = decrypted.split("|")

            if dataID in self.gpit:
                # self.gpit[dataID] = (request_id, num, nodeID)
                request_id, num, nodeID = int(self.gpit[dataID][0]), int(self.gpit[dataID][1]), int(self.gpit[dataID][2])
                print("Received EG reply from gateway peer")
                self.gatewaylogs.append(f"Received EG_REPLY from gateway peer")
                self.gatewaylogs.append(f"Sending DATA from Node ID: {self.id} to Node ID: {nodeID}")
                self.send_data(dataID, request_id, sensor_data, nodeID, num)
                del self.gpit[dataID]

    def forward_interest(self, source_nodeID, dataID, requestID, num):
        '''
        forwards interest to neighbors except where it came from
 
        1. change the interest packet to put self node ID in place of source_nodeID, rest remains same.
        2. forward to all neighbors (check FIB) for mapping except where it came from.
        3. PIT is updated to by taking node id and data id.
           PIT_entry = |data_ID|neighbor-node-ID|
        '''
        # pit = {(data_id, request_id, num) :node_id}
        # fib: {'1': {'serverIP': '127.0.0.1', 'server_port': '12345'},'2': {'serverIP': '127.0.0.1', 'server_port': '12346'}}

        # interest_packet = f"|INTEREST|{self.id}|{dataID}|{requestID}|{num}|"
        header = f"|INTEREST|{self.id}"
        to_encrypt = f"{dataID}|{requestID}|{num}"
        for nodeid in self.fib:
            if nodeid != source_nodeID:
                encrypted = CryptoLayer.encrypt(to_encrypt.encode("utf-8"), self.fib[nodeid]['publickey'])
                interest_packet = f"{header}|{encrypted}|"
                self.interestlogs.append(f"Encrypting INTEREST from Node ID: {self.id} to Node ID: {nodeid}")
                self.interestlogs.append(f"Forwarding INTEREST from Node ID: {self.id} to Node ID: {nodeid}")
                self.conn.send(self.fib[nodeid]['serverIP'], self.fib[nodeid]['server_port'], interest_packet)

    def send_interest(self, dataID, num, gateway_interest=False):
        '''
        initiate interest packets to neighbors

        1. create a interest packet ---> interest_packet = |INTEREST|nodeID|dataID|num|
        2. for loop to forward to neighbors and check in FIB for neighbors and corresponding nodeID.
        '''
        # prt = (dataid, req_id)

        requestID = random.randint(1, 99999)
        header = f"|INTEREST|{self.id}"
        to_encrypt = f"{dataID}|{requestID}|{num}"
        # fib: {'1': {'serverIP': '127.0.0.1', 'server_port':'12345'},'2': {'serverIP': '127.0.0.1', 'server_port': '12346'}}
        if gateway_interest:
            self.gprt.add((dataID,requestID))
        else:
            self.prt[(dataID,requestID)] = time.time()
        for nodeid in self.fib:
            encrypted = CryptoLayer.encrypt(to_encrypt.encode("utf-8"), self.fib[nodeid]['publickey'])
            interest_packet = f"{header}|{encrypted}|"
            self.interestlogs.append(f"Encrypting INTEREST from Node ID: {self.id} to Node ID: {nodeid}")
            self.interestlogs.append(f"Sending INTEREST from Node ID: {self.id} to Node ID: {nodeid}")
            self.conn.send(self.fib[nodeid]['serverIP'], self.fib[nodeid]['server_port'], interest_packet)

    def data_callback(self, data):
        '''
        if node is requester:
            then remove entry from PRT and print that data is received.
        if node is not requester and data needs to be forwarded:
            create a for loop to forward the data to all the neighbors except where it came from.
                data_packet = |DATA|<data>|data_ID|
                construct (data_packet, DST IP, DST port) ---> pass to send function
        '''

        # data_callback is used to receive callback from Comm Layer. Once received, data_callback will split it and send to forward_data.
        s_data = data.split("|")

        # decrypt data
        nodeID, encrypted = int(s_data[2]), s_data[3]
        try:
            decrypted = CryptoLayer.decrypt(encrypted, self.privatekey).split("|") 
        except Exception:
            return
        
        dataID, requestID, num, sensor_data = decrypted[0], int(decrypted[1]), int(decrypted[2]), decrypted[3]
        
        if self.designated_gateway and (dataID, requestID) in self.gprt:
           self.gatewaylogs.append(f"Received DATA ({dataID}) from Node ID: {nodeID} on Node ID: {self.id}")
           self.gatewaylogs.append(f"Decrypting DATA ({dataID}) = ({sensor_data}) from Node ID: {nodeID} on Node ID: {self.id}")
           self.send_gateway_packet(dataID, sensor_data)
           self.gprt.remove((dataID, requestID))
        
        else:
            if (dataID, requestID) in self.prt:
                self.datalogs.append(f"Received DATA ({dataID}) from Node ID: {nodeID} on Node ID: {self.id}")
                self.datalogs.append(f"Decrypting DATA ({dataID}) = ({sensor_data}) from Node ID: {nodeID} on Node ID: {self.id}")
                print(f"DATA : {decrypted[0]} is received with value: {sensor_data}")
                print(f"TOTAL TIME TAKEN : {(time.time() - self.prt[(dataID, requestID)])} seconds.")
                del self.prt[(dataID, requestID)]
            else:
                self.forward_data(dataID, requestID, sensor_data, num)

    def forward_data(self, dataID, requestID, sensor_data, num):
        '''
        1. forward to required node
        '''
        # pit = {(dataID, requestID, num):destination node_id}
        # fib: {'1': {'serverIP': '127.0.0.1', 'server_port': '12345'},'2': {'serverIP': '127.0.0.1', 'server_port': '12346'}}
        
        if (dataID, requestID, num) in self.pit:
            nodeID = self.pit[(dataID, requestID, num)]

            header = f"|DATA|{self.id}"
            to_encrypt = f"{dataID}|{requestID}|{num}|{sensor_data}"
            encrypted = CryptoLayer.encrypt(to_encrypt.encode("utf-8"), self.fib[nodeID]['publickey'])
            data_packet = f"{header}|{encrypted}|"
            # data_packet = f"|DATA|{self.id}|{dataID}|{requestID}|{num}|{sensor_data}|"
            self.datalogs.append(f"Encrypting DATA from Node ID: {self.id} to Node ID: {nodeID}")
            self.datalogs.append(f"Forwarding DATA from Node ID: {self.id} to Node ID: {nodeID}")
            self.conn.send(self.fib[nodeID]['serverIP'], self.fib[nodeID]['server_port'], data_packet)
            del self.pit[(dataID, requestID, num)]

    def send_data(self, dataID, requestID, actual_data, nodeid, num): # this will be called when any node has data requested.
        # creating a data packet and sending to the node which asked for data.
        # data_packet = f"|DATA|{self.id}|{dataID}|{requestID}|{num}|{actual_data}|"
        
        header = f"|DATA|{self.id}"
        to_encrypt = f"{dataID}|{requestID}|{num}|{actual_data}"
        encrypted = CryptoLayer.encrypt(to_encrypt.encode("utf-8"), self.fib[nodeid]['publickey'])
        data_packet = f"{header}|{encrypted}|"
        self.datalogs.append(f"Encrypting DATA from Node ID: {self.id} to Node ID: {nodeid}")
        self.datalogs.append(f"Sending DATA from Node {self.id} to Node ID: {nodeid}")
        self.conn.send(self.fib[nodeid]['serverIP'], self.fib[nodeid]['server_port'], data_packet)

    def register_callbacks(self):
        self.conn.hello_callback = self.hello_callback
        self.conn.data_callback = self.data_callback
        self.conn.interest_callback = self.interest_callback
        self.conn.gateway_callback = self.gateway_callback


class CommunicationLayer:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.hello_callback = None
        self.data_callback = None
        self.interest_callback = None
        self.gateway_callback = None
        self.pause = False
    
    def listen(self):
        threading.Thread(target=self.t_listen).start()

    def t_listen(self):
        # keep on listening to connections infinitely
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.bind((self.address, self.port))
        peer_socket.listen(1)
        #print(f"Peer is listening on {self.address}:{self.port}...")


        while True:
            client_socket, client_address = peer_socket.accept()
            #print(f"Connection established with {client_address[0]}:{client_address[1]}")
            
            # call receive thread to extract data
            threading.Thread(target=self.receive, args=(client_socket,)).start()


    def send(self, destination_address, destination_port, message):
        '''
        spawn client thread to form and send data over TCP sessions
        The data packet will be passed from NDNLayer as a function call to CommunicationLayer.
        '''
        if self.pause:
            return
        
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            peer_socket.connect((destination_address, destination_port))
            #print(f"Sending to peer: '{message}'")
            peer_socket.send(message.encode('utf-8'))
        except Exception:
            pass
            #print("Failed connection to port", destination_port)
    
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
        if self.pause:
            return
        
        data = in_socket.recv(1024).decode('utf-8')
        #print(f"Received from peer: '{data}'")

        if "INTEREST" in data:
            self.interest_callback(data)
        
        if "DATA" in data:
            self.data_callback(data)
        
        if "HELLO" in data:
            self.hello_callback(data)
        
        if "EG" == data[:2]:
            self.gateway_callback(data)
        
        

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



