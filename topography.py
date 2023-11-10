import json

def crete_topo():

    Addresses = ["10.35.70.14", "10.35.70.45"]
    Nodes=["Node1","Node2","Node3","Node4","Node5","Node6","Node7","Node8","Node9","Node0"]
    Nodes_rasp1=["Node1","Node2","Node3","Node4","Node5"]
    Nodes_rasp2=["Node6","Node7","Node8","Node9","Node0"]



    DiverNeighborList=[
                       ["Node1","Node6","Node7"],
                       ["Node2","Node3","Node8"],
                       ["Node4","Node5","Node9","Node0"]
                       ]
    
    json_array = {}

    listen_port = 33001
    send_port = 33002

    for node in Nodes:
        if node in Nodes_rasp1:
            rasp_no=1
        else:
            rasp_no=2
        peer_list=[]
        for j in DiverNeighborList:
            if node in j:
                peer_list=j.copy()
                peer_list.remove(node)
                break;

        json_array[node]={"ip":Addresses[rasp_no-1],"send_port":send_port,"listen_port":listen_port,"peer":peer_list}
        send_port+=2
        listen_port+=2

    with open('topograph.json', 'w') as f:
        json.dump(json_array, f, indent=4)

if __name__ == "__main__":
    crete_topo()