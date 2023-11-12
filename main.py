from ndn import Node
import time
from topology import nodes
# from multiprocessing import Process
from threading import Thread

node_objects = {}

def node_proc(nodes, node_id):
    '''
    1. for loop to iterate over peers' ip and ports
    

    this will create and start a single Node object
    '''
    peer_details = []
    for peer_nodeid in nodes[node_id]["peers"]:
        peer = (nodes[peer_nodeid]["server_IP"], int(nodes[peer_nodeid]["server_port"]))
        peer_details.append(peer)

    node = Node(node_id, nodes[node_id]["server_IP"], nodes[node_id]["server_port"])
    node_objects[node_id] = node
    node.start(peer_details)

def main():
    for node_id in nodes:
        proc = Thread(target=node_proc, args=(nodes, node_id))
        proc.start()

    while True:
        print("OPTIONS\n1. Send Interest Packet")
        user_input = input("Enter: ")

        if user_input == "1":
            nodeID = input("Source nodeID: ")
            dataID = input("DataID: ")

            node_objects[int(nodeID)].ndn.send_interest(dataID, 1) # "/data/3/heartrate"
            time.sleep(2)

if __name__ == "__main__":
    main()