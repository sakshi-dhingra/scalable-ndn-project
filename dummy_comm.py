import socket
import threading
import time

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        print(f"Received from peer: '{data}'")
        time.sleep(10)
    client_socket.close()

def start_server(port): # server is listening for clients

    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.bind(('127.0.0.1', port))
    peer_socket.listen(1)
    print(f"Peer is listening on 127.0.0.1:{port}...")

    # keep on listening to connections infinitely
    while True:
        client_socket, client_address = peer_socket.accept()
        print(f"Connection established with {client_address[0]}:{client_address[1]}")

        threading.Thread(target=handle_client, args=(client_socket,)).start()

def start_client(src_port, dest_port): # client is initiating connection
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # retry mechanism 
    while True:
        try:
            peer_socket.connect(('127.0.0.1', dest_port))
            break
        except Exception:
            print("retrying connection to port", dest_port)
            time.sleep(1)

# send hellos to all connected and close the session
    hello_msg = f"Hello to port {dest_port} from {src_port}"
    while True:
        print(f"Sending to peer: '{hello_msg}'")
        peer_socket.send(hello_msg.encode('utf-8'))
        time.sleep(10)
    peer_socket.close()

if __name__ == "__main__":
    import sys

    print(sys.argv)

    # if len(sys.argv) != 3 or (not sys.argv[1].isdigit() or not sys.argv[2].isdigit()):
    #     print("Usage: python bidirectional_tcp_peer.py <port1> <port2>")
    #     sys.exit(1)

    port1 = int(sys.argv[1])
    threading.Thread(target=start_server, args=(port1,)).start()
    time.sleep(2)

    for port in sys.argv[2:]:
        port = int(port)
        threading.Thread(target=start_client, args=(port1, port,)).start()
        
    
    # time.sleep(2)
    # print("Starting client")
    # threading.Thread(target=start_client, args=(port2,)).start()





