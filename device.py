#import the socket module
import socket
from threading import Thread, Lock
import json
import time
from config import *
import argparse
import os

peer_discovery_map = {}

def flushPeerDiscoveryMap(port):
    print('saving peer discovery to file..')
    file_path = os.path.join(discovery_dir,discovery_map_file_name + '_' + str(port) + "." + discovery_map_file_ext)
    with open(file_path, 'w') as f:
        json.dump(peer_discovery_map, f)
    time.sleep(10)
    flushPeerDiscoveryMap(port)

# update peer discovery map for each peer
def updatePeerDiscoveryMap(peer, routingTable):
    car_ports = []
    for _, data in routingTable.items():
        car_ports.append(data['car_port'])
    peer_discovery_map[peer] = car_ports
    print(peer_discovery_map)

# join network
def joinNetwork(top_port, car_port):
    #Create a socket instance
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
        socketObject.connect((base_station_host, base_station_port))
        print("Connected to %s at port %s" % (base_station_host, base_station_port))
        msg = {'top_port': top_port, 'car_port': car_port}
        socketObject.send(json.dumps(msg).encode('utf-8'))

def recvTopology(top_port, car_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
        print('listening to topology messages')
        print('binding to ' + str(top_port))
        socketObject.bind(('localhost', top_port))
        socketObject.listen()
        
        # listen continuously for the topology info as new peers join
        while True:
            conn, _ = socketObject.accept()
            routingTable = json.loads(conn.recv(4096).decode('utf-8'))
            print('%s : New peer joined -> %s' % (str(top_port),str(routingTable)))
            # update peer discovery
            updatePeerDiscoveryMap(car_port,routingTable)

def recvPeerMessages(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
        print('listening to car messages')
        print('binding to ' + str(port))
        socketObject.bind(('localhost', port))
        socketObject.listen()
        
        # listen continuously for the topology info as new peers join
        while True:
            conn, _ = socketObject.accept()
            message = json.loads(conn.recv(4096).decode('utf-8'))
            print('%s : Incoming Message -> %s' % (str(port),str(message)))

def main():
    clients = []
    clients_top_recv = []
    clients_msg_recv = []

    parser = argparse.ArgumentParser()
    parser.add_argument('--port-top', help='initial port for topology', type=int)
    parser.add_argument('--port-car', help='initial port for cars', type=int)
    parser.add_argument('--devices', help='number of devices in this network', type=int)
    args = parser.parse_args()

    if args.port_top is None:
        print("Please specify the initial topology port")
        exit(1)
    
    if args.port_car is None:
        print("Please specify the initial car port")
        exit(1)
    
    if args.devices is None:
        print("Please specify the number of devices")
        exit(1)
    
    device_top_port_start = args.port_top
    device_car_port_start = args.port_car
    num_of_devices = args.devices

    # create clients
    for i in range(num_of_devices):
        clients.append(Thread(target=joinNetwork, args=(device_top_port_start+i,device_car_port_start+i,)))
        clients_top_recv.append(Thread(target=recvTopology, args=(device_top_port_start+i,device_car_port_start+i,)))
        clients_msg_recv.append(Thread(target=recvPeerMessages, args=(device_car_port_start+i,)))

    # start listening to topology for all clients
    for client in clients_top_recv:
        client.start()
    
    # start listening to peer messages for all clients
    for client in clients_msg_recv:
        client.start()

    # join each client at a delay of 5 seconds
    for client in clients:
        client.start()
        time.sleep(5)
    
    # every 5 seconds flush peer discovery map of a network to a file
    Thread(target=flushPeerDiscoveryMap, args=(device_top_port_start,)).start()

    for i in range(len(clients)):
        clients[i].join()
        clients_top_recv[i].join()
        clients_msg_recv[i].join()


if __name__ == '__main__':
    main()