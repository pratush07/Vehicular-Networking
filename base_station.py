import socket
from config import *
from threading import Thread
import json
import time

network_participants = {}

# control plane to return topology
def return_topolgy():
    print('sending new routing table to all peers')
    print(network_participants)

    for _, data in network_participants.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((data['address'], data['top_port']))
            s.send(json.dumps(network_participants).encode('utf-8'))

def add_to_network(addr, data):
    address = addr[0]
    data['address'] = address
    network_participants[data['top_port']] = data

# if new peers join, they will a send a message here
def listen_for_topology():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((base_station_host, base_station_port))
        s.listen()
        print('Started. Accepting Connections..')
        while True:
            conn, addr = s.accept()
            data = json.loads(conn.recv(4096).decode('utf-8'))
            
            # add this information to network participants
            add_to_network(addr, data)
            
            # return topology information to all devices in the network
            Thread(target=return_topolgy).start()


print('Starting base station ...')
t = Thread(target=listen_for_topology)
t.start()
t.join()