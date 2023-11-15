# ---> for main script <---
# rpi1_nodes
running_nodes = [1, 2, 3, 4, 5]

# rpi2_nodes
# running_nodes = [6, 7, 8, 9, 10]
 
# ---> for display script <---
rpi1_nodes = [1, 2, 3, 4, 5]
rpi2_nodes = [6, 7, 8, 9, 10]

gw_node = 10
gw_comm = ("10.35.70.16", 33009) # Group 16 gateway port

nodes = {
    1: {
        "server_IP": "10.35.70.43",
        "server_port": 33001,
        "peers": [2, 5, 6]
    },
    2: {
        "server_IP": "10.35.70.43",
        "server_port": 33002,
        "peers": [1, 4, 7]
    },
    3: {
        "server_IP": "10.35.70.43",
        "server_port": 33003,
        "peers": [2, 4]
    },
    4: {
        "server_IP": "10.35.70.43",
        "server_port": 33004,
        "peers": [2, 3, 5, 9]
    },
    5: {
        "server_IP": "10.35.70.43",
        "server_port": 33005,
        "peers": [1, 4, 10]
    },
    6: {
        "server_IP": "10.35.70.10",
        "server_port": 33001,
        "peers": [1, 7, 10]
    },
    7: {
        "server_IP": "10.35.70.10",
        "server_port": 33002,
        "peers": [2, 6, 8, 9]
    },
    8: {
        "server_IP": "10.35.70.10",
        "server_port": 33003,
        "peers": [7, 9]
    },
    9: {
        "server_IP": "10.35.70.10",
        "server_port": 33004,
        "peers": [4, 7, 8, 10]
    },
    10: {
        "server_IP": "10.35.70.10",
        "server_port": 33005,
        "peers": [5, 6, 9]
    }
}
