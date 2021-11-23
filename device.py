#import the socket module
import socket
from threading import Thread
import json
import time
from config import *
import argparse

peer_discovery_map = {}

# update peer discovery map for each peer
def updatePeerDiscoveryMap(peer, routingTable):
    if peer not in peer_discovery_map:
        peer_discovery_map[peer] = set()
    peer_discovery_map[peer].update(routingTable.keys())
    print(peer_discovery_map)

# join network
def joinNetwork(port):
    #Create a socket instance
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
        socketObject.connect((base_station_host, base_station_port))
        print("Connected to %s at port %s" % (base_station_host, base_station_port))
        msg = {'port': port}
        socketObject.send(json.dumps(msg).encode('utf-8'))

def recvTopology(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
        print('binding to ' + str(port))
        socketObject.bind(('localhost', port))
        socketObject.listen()
        
        # listen continuously for the topology info as new peers join
        while True:
            conn, _ = socketObject.accept()
            routingTable = json.loads(conn.recv(4096).decode('utf-8'))
            print('%s : New peer joined -> %s' % (str(port),str(routingTable)))
            # update peer discovery
            updatePeerDiscoveryMap(port,routingTable)

def main():
    clients = []
    clients_top_recv = []

    parser = argparse.ArgumentParser()
    parser.add_argument('--port-initial', help='initial port', type=int)
    parser.add_argument('--devices', help='number of devices in this network', type=int)
    args = parser.parse_args()

    if args.port_initial is None:
        print("Please specify the initial port")
        exit(1)
    
    if args.devices is None:
        print("Please specify the number of devices")
        exit(1)
    
    device_port_start = args.port_initial
    num_of_devices = args.devices

    # create clients
    for i in range(num_of_devices):
        clients.append(Thread(target=joinNetwork, args=(device_port_start+i,)))
        clients_top_recv.append(Thread(target=recvTopology, args=(device_port_start+i,)))

    # start listening to topology for all clients
    for client in clients_top_recv:
        client.start()

    # join each client at a delay of 5 seconds
    for client in clients:
        client.start()
        time.sleep(5)

    for i in range(len(clients)):
        clients[i].join()
        clients_top_recv[i].join()

if __name__ == '__main__':
    main()