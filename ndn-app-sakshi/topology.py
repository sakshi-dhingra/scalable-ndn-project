# 1 --- 2 --- 3
# nodes = {
#     1: {
#         "server_IP": "127.0.0.1",
#         "server_port": 12345,
#         "peers": [2]
#     },
#     2: {
#         "server_IP": "127.0.0.1",
#         "server_port": 12346,
#         "peers": [1, 3]
#     },
#     3: {
#         "server_IP": "127.0.0.1",
#         "server_port": 12347,
#         "peers": [2]
#     }
# }

#  / 2 \
# 1  |  4
#  \ 3 /

rpi1_nodes = [1, 2, 3, 4, 5]
rpi2_nodes = [6, 7, 8, 9, 10]
running_nodes = rpi1_nodes + rpi2_nodes

# running_nodes = [1, 2]
# running_nodes = [3, 4]
nodes = {
    1: {
        "server_IP": "127.0.0.1",
        "server_port": 12341,
        "peers": [2, 5, 6]
    },
    2: {
        "server_IP": "127.0.0.1",
        "server_port": 12342,
        "peers": [1, 4, 7]
    },
    3: {
        "server_IP": "127.0.0.1",
        "server_port": 12343,
        "peers": [2, 4]
    },
    4: {
        "server_IP": "127.0.0.1",
        "server_port": 12344,
        "peers": [2, 3, 5, 9]
    },
    5: {
        "server_IP": "127.0.0.1",
        "server_port": 12345,
        "peers": [1, 4, 10]
    },
    6: {
        "server_IP": "127.0.0.1",
        "server_port": 12346,
        "peers": [1, 7, 10]
    },
    7: {
        "server_IP": "127.0.0.1",
        "server_port": 12347,
        "peers": [2, 6, 8, 9]
    },
    8: {
        "server_IP": "127.0.0.1",
        "server_port": 12348,
        "peers": [7, 9]
    },
    9: {
        "server_IP": "127.0.0.1",
        "server_port": 12349,
        "peers": [4, 7, 8, 10]
    },
    10: {
        "server_IP": "127.0.0.1",
        "server_port": 12360,
        "peers": [5, 6, 9]
    }
}
