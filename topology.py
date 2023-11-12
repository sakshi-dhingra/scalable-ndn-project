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
nodes = {
    1: {
        "server_IP": "127.0.0.1",
        "server_port": 12345,
        "peers": [2, 3]
    },
    2: {
        "server_IP": "127.0.0.1",
        "server_port": 12346,
        "peers": [1, 4, 3]
    },
    3: {
        "server_IP": "127.0.0.1",
        "server_port": 12347,
        "peers": [1, 4, 2]
    },
    4: {
        "server_IP": "127.0.0.1",
        "server_port": 12348,
        "peers": [2, 3]
    }
}
