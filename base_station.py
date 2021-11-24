import socket
from config import *
from threading import Thread
import json
import time
import argparse

network_participants = {}

base_station_host = 'localhost'
base_station_port = 30201

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='host to run the base station', type=str)
    parser.add_argument('--port', help='port for the base station', type=int)
    args = parser.parse_args()

    if args.host is not None:
        global base_station_host
        base_station_host = args.host
        
    if args.port is not None:
        global base_station_port
        base_station_port = args.port
    
    print('Starting base station at %s on port %s' % (base_station_host, base_station_port))
    t = Thread(target=listen_for_topology)
    t.start()
    t.join()

if __name__ == '__main__':
    main()