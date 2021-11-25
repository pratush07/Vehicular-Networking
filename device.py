#import the socket module
import socket
from threading import Thread, Lock
import json
import time
from config import *
import argparse
import os

from Sensors.FuelSensor import Fuelsensor
from Sensors.DirectionSensor import Directionsensor
from Sensors.LightSensor import Lightsensor
from Sensors.PositionSensor import Positionsensor


class vehicle:

    peer_discovery_map = {}
    
    base_station_host = 'localhost'
    base_station_port = 30201
    car_host = 'localhost'
    device_top_port_start = 0
    device_car_port_start = 0
    Fs = Fuelsensor("FuelSensor")
    Ds = Directionsensor("Directionsensor")
    Ls = Lightsensor("Lightsensor")
    Ps = Positionsensor("Positionsensor")
    peer_map_file = ""
    
    def flushPeerDiscoveryMap(self):
        print('saving peer discovery to file..')
        file_path = os.path.join(discovery_dir,self.peer_map_file)
        with open(file_path, 'w') as f:
            json.dump(self.peer_discovery_map, f)
        #time.sleep(10)
        #self.flushPeerDiscoveryMap(port)

    # update peer discovery map for each peer
    def updatePeerDiscoveryMap(self, peer, routingTable):
        car_ports = []
        for _, data in routingTable.items():
            car_addr = self.car_host+":"+str(peer)
            peer_addr = data['address'] + ":" + str(data['car_port'])
            if car_addr != peer_addr:
                car_ports.append((data['address'],data['car_port']))
        self.peer_discovery_map[car_addr] = car_ports
        print(self.peer_discovery_map)

    # join network
    def joinNetwork(self, top_port, car_port):
        #Create a socket instance
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
            socketObject.connect((self.base_station_host, self.base_station_port))
            print("Connected to %s at port %s" % (self.base_station_host, self.base_station_port))
            msg = {'top_port': top_port, 'car_port': car_port}
            socketObject.send(json.dumps(msg).encode('utf-8'))

    def recvTopology(self, top_port, car_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
            print('listening to topology messages')
            print('binding to ' + str(top_port))
            socketObject.bind((self.car_host, top_port))
            socketObject.listen()
            
            # listen continuously for the topology info as new peers join
            while True:
                conn, _ = socketObject.accept()
                routingTable = json.loads(conn.recv(4096).decode('utf-8'))
                print('%s : New peer joined -> %s' % (str(top_port),str(routingTable)))
                # update peer discovery
                self.updatePeerDiscoveryMap(car_port,routingTable)
                self.flushPeerDiscoveryMap()

    def recvPeerMessages(self,port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
            print('listening to car messages')
            print('binding to ' + str(port))
            socketObject.bind((self.car_host, port))
            socketObject.listen()
            
            # listen continuously for the topology info as new peers join
            while True:
                conn, _ = socketObject.accept()
                message = json.loads(conn.recv(4096).decode('utf-8'))
                print('%s:%s Incoming Message -> %s' % (str(port), self.car_host,str(message)))
                
    def gossip(self):
        print('sending peer to peer messages..')
        if os.path.exists(discovery_dir):
            #for file in os.listdir(discovery_dir):
                file_path = os.path.join(discovery_dir, self.peer_map_file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    for src, dests in data.items():
                        for dest in dests:
                            if (dest[1] != self.device_car_port_start):
                                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                                    #try:
                                        print('sending msg to ' + str(dest))
                                        #print(str(dests))
                                        #print(str(src))
                                        s.connect((dest[0], dest[1]))
                                        #s.send(json.dumps({'msg': 'hello from car port ' + str(src)}).encode('utf-8'))
                                        s.send(self.Fs.get_data().encode('utf-8'))
                                        #s.send(self.Ds.get_data().encode('utf-8'))
                                        #s.send(self.Ls.get_data().encode('utf-8'))
                                        #s.send(self.Ps.get_data().encode('utf-8'))
                                        time.sleep(2)
                                    #except:
                                        #continue
        else:
            print('no device active..')
        print('going to sleep..')
        time.sleep(5)
        #self.gossip()
    
    
    def __init__(self, header, port_top, port_car):
        #clients = []
        #clients_top_recv = []
        #clients_msg_recv = []

        #parser = argparse.ArgumentParser()
        #parser.add_argument('--host-car', help='car host for topology', type=str)
        #parser.add_argument('--port-top', help='initial port for topology', type=int)
        #parser.add_argument('--port-car', help='initial port for cars', type=int)
        #parser.add_argument('--devices', help='number of devices in this network', type=int)
        #parser.add_argument('--base-host', help='base station host', type=str)
        #parser.add_argument('--base-port', help='base station port', type=int)
        #args = parser.parse_args()

        #if args.host_car is not None:
        #    global car_host
        
        self.header = header    
        #self.car_host = host_car
        #self.base_station_host = base_host
        #self.base_station_port = base_port
        self.device_top_port_start = port_top
        self.device_car_port_start = port_car 
        self.peer_map_file = "peer_discovery_map_" + self.car_host + str(port_car) + ".json"
        #if args.base_host is not None:
        #    global base_station_host
        #    base_station_host = args.base_host
            
        #if args.base_port is not None:
        #    global base_station_port
        #    base_station_port = args.base_port

        #if args.port_top is None:
        #    print("Please specify the initial topology port")
        #    exit(1)
        
        #if args.port_car is None:
        #    print("Please specify the initial car port")
        #    exit(1)
        
        #if args.devices is None:
        #    print("Please specify the number of devices")
        #    exit(1)
        
        #device_top_port_start = port_top
        #device_car_port_start = port_car
        #num_of_devices = args.devices

        #if not os.path.exists(discovery_dir):
        
        # Create a new directory because it does not exist 
        #    os.makedirs(discovery_dir)

        # create clients
        #for i in range(num_of_devices):
        client_receiveTopology = Thread(target=self.recvTopology, args=(self.device_top_port_start,self.device_car_port_start,))
        client_receivePeer = Thread(target=self.recvPeerMessages, args=(self.device_car_port_start,))
        client_joinNetwork = Thread(target=self.joinNetwork, args=(self.device_top_port_start,self.device_car_port_start,))
        client_gossip = Thread(target=self.gossip)
        
        client_receiveTopology.start()
        client_receivePeer.start()
        client_joinNetwork.start()
        time.sleep(10)
        client_gossip.start()
        # start listening to topology for all clients
        #for client in clients_top_recv:
        #client.start()
        
        # start listening to peer messages for all clients
        #for client in clients_msg_recv:
        #client.start()

        # join each client at a delay of 5 seconds
        #for client in clients:
        #client.start()
        #time.sleep(5)
        
        # every 5 seconds flush peer discovery map of a network to a file
        #Thread(target=flushPeerDiscoveryMap, args=(device_top_port_start,)).start()

        #for i in range(len(clients)):
        client_receiveTopology.join()
        client_receivePeer.join()
        client_joinNetwork.join()
        
        
        client_gossip.join()
