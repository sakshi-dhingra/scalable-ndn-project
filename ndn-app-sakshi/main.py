from ndn import Node
import time
from topology import nodes, running_nodes, gw_node, gw_comm
# from multiprocessing import Process
from threading import Thread
from crypto import CryptoLayer
from pprint import pprint

node_objects = {}

def node_td(nodes, node_id):
    '''
    1. for loop to iterate over peers' ip and ports
    

    this will create and start a single Node object
    '''
    ndn_privatekey = CryptoLayer.loadPrivateKey("ndn.pem")
    gateway_privatekey = CryptoLayer.loadPrivateKey("gateway.pem")

    peer_details = []
    for peer_nodeid in nodes[node_id]["peers"]:
        peer = (nodes[peer_nodeid]["server_IP"], int(nodes[peer_nodeid]["server_port"]))
        peer_details.append(peer)

    if gw_node == node_id:
        node = Node(node_id, nodes[node_id]["server_IP"], nodes[node_id]["server_port"], ndn_privatekey, gateway_privatekey, True, gw_comm)
    else:
        node = Node(node_id, nodes[node_id]["server_IP"], nodes[node_id]["server_port"], ndn_privatekey, gateway_privatekey)
    node_objects[node_id] = node # saving object to access it
    node.start(peer_details)

def menu():
    print("\n**** OPTIONS ****\n\n0. Print Menu")
    print("1. Send Interest Packet")
    print("2. Display FIB")
    print("3. Display PIT")
    print("4. Display PRT")
    print("5. Display Logs")
    print("6. View sensor data generated by node")
    print("7. List Nodes")
    print("8. Stop a node")
    print("9. Start a node")
    print("10. Display keys")
    print("11. Exit\n")


def input_node(node_objects):
    nodeID = ""
    while nodeID not in node_objects:
        nodeID = input("Source nodeID: ")
        try:
            nodeID = int(nodeID)
        except:
            print("Node ID should be an integer!")
        
    return int(nodeID)


def main():
    for node_id in running_nodes:
        td = Thread(target=node_td, args=(nodes, node_id))
        td.daemon = True
        td.start()

    menu()

    while True:
        print()
        user_input = input("Option: ")

        if user_input == '0':
            menu()
        if user_input == "1":
            nodeID = input_node(node_objects)
            dataID = input("DataID: ")
            print(f"\nSending interest packet from node {nodeID}.", flush=True)
            node_objects[int(nodeID)].ndn.send_interest(dataID, 1) # "/data/3/heartrate"
            time.sleep(2)
        elif user_input == "2":
            nodeID = input_node(node_objects)
            print(f"--- FIB ({nodeID}) ---")
            pprint(node_objects[int(nodeID)].ndn.fib)
        elif user_input == "3":
            nodeID = input_node(node_objects)
            print(f"--- PIT ({nodeID}) ---")
            pprint(node_objects[int(nodeID)].ndn.pit)
        elif user_input == "4":
            nodeID = input_node(node_objects)
            print(f"--- PRT ({nodeID}) ---")
            pprint(node_objects[int(nodeID)].ndn.prt)
        elif user_input == "5":
            nodeID = input_node(node_objects)
            print(f"--- LOGS {nodeID} ---")
            print("\n****Displaying Last 10 Hello Packet Logs****\n")
            print(*node_objects[int(nodeID)].ndn.hellologs[-10:], sep="\n")
            print("\n****Displaying Interest packet Logs****\n")
            print(*node_objects[int(nodeID)].ndn.interestlogs,sep="\n")
            print("\n****Displaying Data packet Logs****\n")
            print(*node_objects[int(nodeID)].ndn.datalogs, sep="\n")
        elif user_input == "6":
            nodeID = input_node(node_objects)
            print(f"--- SENSOR {nodeID} ---")
            pprint(node_objects[int(nodeID)].sensor_data.data)
        elif user_input == "7":
            print(running_nodes)
        elif user_input == "8":
            nodeID = input_node(node_objects)
            node_objects[int(nodeID)].ndn.conn.pause = True
            print(f"Paused node {nodeID}")
            # add code to clear fib
        elif user_input == "9":
            nodeID = input_node(node_objects)
            node_objects[int(nodeID)].ndn.conn.pause = False
            print(f"Started node {nodeID}")
        elif user_input == "10":
            nodeID = input_node(node_objects)
            print(f"UNIQUE KEYS {nodeID}")
            privkey, pubkey = CryptoLayer.exportKey(node_objects[int(nodeID)].ndn.privatekey, node_objects[int(nodeID)].ndn.publickey)
            print(privkey)
            print(pubkey)
            print(f"NDN KEYS {nodeID}")
            privkey, pubkey = CryptoLayer.exportKey(node_objects[int(nodeID)].ndn.ndn_privatekey, node_objects[int(nodeID)].ndn.ndn_publickey)
            print(privkey)
            print(pubkey)
        elif user_input == "11":
            exit()


if __name__ == "__main__":
    main()