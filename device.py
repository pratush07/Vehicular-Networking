# import the socket module
import socket
from threading import Thread, Lock
import json
import time
from Sensors.LaneWidthSensor import Lanewidthsensor
from Sensors.PowerLevelIndicator import Powerlevelindicator
from Sensors.ProximitySensors import Proximitysensor
from Sensors.SpeedSensor import Speedsensor
from config import *
import os

from Sensors.FuelSensor import Fuelsensor
from Sensors.DirectionSensor import Directionsensor
from Sensors.LightSensor import Lightsensor
from Sensors.PositionSensor import Positionsensor
from secure_comm import encrypt_public_key, decrypt_private_key


class vehicle:

    def flushPeerDiscoveryMap(self):
        print('saving peer discovery to file..')
        file_path = os.path.join(discovery_dir, self.peer_map_file)
        with open(file_path, 'w') as f:
            json.dump(self.peer_discovery_map, f)

    def flushMessages(self, message):
        print('saving peer messages to file..')
        file_path = os.path.join(messages_dir, self.peer_messages_file)
        with open(file_path, 'a+') as f:
            json.dump(message, f)
            f.write("\n")
    
    def flushPosAndSpeed(self):
        print('logging speed and position')
        file_path = os.path.join(car_info_dir, self.car_info_file)
        with open(file_path, 'a+') as f:
            json.dump({'X': self.Ps.get_data()['X'], 'Speed': self.Ss.get_data() }, f)
            f.write("\n")

    # update peer discovery map for each peer
    def updatePeerDiscoveryMap(self, peer, routingTable):
        car_ports = []
        for key, data in routingTable.items():
            if self.header != key and self.header != data['header']:
                car_ports.append((data['address'], data['car_port']))
        self.peer_discovery_map[self.header] = car_ports
        print(self.peer_discovery_map)

    # join network
    def joinNetwork(self, top_port, car_port):
        # Create a socket instance
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
            socketObject.connect(
                (self.base_station_host, self.base_station_port))
            print("Connected to %s at port %s" %
                  (self.base_station_host, self.base_station_port))
            msg = {'header': self.header,
                   'top_port': top_port, 'car_port': car_port}
            socketObject.send(json.dumps(msg).encode('utf-8'))

    def recvTopology(self, top_port, car_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
            print('listening to topology messages')
            print('binding to ' + str(top_port))
            socketObject.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socketObject.bind((self.car_host, top_port))
            socketObject.listen()

            # listen continuously for the topology info as new peers join
            while True:
                conn, _ = socketObject.accept()
                routingTable = json.loads(conn.recv(4096).decode('utf-8'))
                print('%s : New peer joined -> %s' %
                      (str(self.header), str(routingTable)))
                # update peer discovery
                self.updatePeerDiscoveryMap(car_port, routingTable)
                self.flushPeerDiscoveryMap()

    def detect_car_proximity(self, message):
        # check if we are processing gossiping information
        if message['type'] != 'Gossip':
            return

        pos_incom_car = message['position']
        speed_incom_car = message['speed']
        relative_dist = self.Ps.get_data()['X'] - pos_incom_car['X']
        sender_host = message['sender'].split("_")[1]
        sender_port = int(message['sender'].split("_")[2])

        # it is a car moving in the rear..assuming speed of the font car will be less than the one behind
        if relative_dist > 0 and relative_dist <= car_distance_threshold:
            # check if the car enters the threshold region
            print('Proximity detected with car %s' % (message['sender']))

            # log in a file
            file_path = os.path.join(stability_dir, stability_log_file_name + "_"
                                     + self.car_host + "_" + str(self.device_car_port)) + "." + stability_log_file_ext
            with open(file_path, 'a+') as f:
                f.write('%s at location %s m and speed %s (m/s) detected proximity with car %s at location %s m and speed %s (m/s)' %
                        (self.header, self.Ps.get_data()['X'], self.Ss.get_data()['speed'], message['sender'],
                         pos_incom_car['X'], speed_incom_car['speed']))
                f.write("\n")

            # send the new speed to the car
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((sender_host, sender_port))
                payload = {}
                payload['speed'] = self.Ss.get_data()['speed']
                payload['type'] = 'Stable Speed'
                payload['sender'] = self.header
                s.send(encrypt_public_key(bytes(json.dumps(payload),'utf-8')))

    def recvPeerMessages(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
            print('listening to car messages')
            print('binding to ' + str(port))
            socketObject.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socketObject.bind((self.car_host, port))
            socketObject.listen()

            # listen continuously for the topology info as new peers join
            while True:
                conn, _ = socketObject.accept()
                message = json.loads(decrypt_private_key(conn.recv(4096).decode('utf-8')))

                print('%s (%s:%s) Incoming Message -> %s (sent by %s)'
                      % (self.header, self.car_host, str(port), str(message), message['sender']))

                self.flushMessages(message)

                self.detect_car_proximity(message)

                self.stabalize_speed_if_applicable(message)

    def stabalize_speed_if_applicable(self, message):
        if message['type'] != 'Stable Speed':
            return

        # reduce the car speed temporarily to get out of detection zone
        self.Ss.set_data(message['speed']-2)
        time.sleep(3)

        # now stabalize
        self.Ss.set_data(message['speed'])

    def gossip(self):
        print('%s (%s:%s) is sending messages to peers' %
              (self.header, self.car_host, self.device_car_port))
        if len(self.peer_discovery_map) != 0:
            for _, dests in self.peer_discovery_map.items():
                for dest in dests:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((dest[0], dest[1]))
                        payload = {}
                        payload['fuel'] = self.Fs.get_data()
                        payload['direction'] = self.Ds.get_data()
                        payload['light'] = self.Ls.get_data()
                        payload['position'] = self.Ps.get_data()
                        payload['speed'] = self.Ss.get_data()
                        payload['lane_width'] = self.Lw.get_data()
                        payload['power_level'] = self.Pl.get_data()
                        payload['obstacle_detected'] = self.Pr.get_data()
                        payload['type'] = 'Gossip'
                        payload['sender'] = self.header
                        s.send(encrypt_public_key(bytes(json.dumps(payload),'utf-8')))
                        time.sleep(2)

        else:
            print('no device active..')
        print('going to sleep..')
        time.sleep(2)
        self.gossip()

    def changePosition(self):
        print("Position change thread running")
        x = self.Ps.get_data_X()
        speed = self.Ss.get_speed()
        dist = speed * 2  # 2 is the time interval, same for thread sleep
        self.Ps.set_data(x+dist)
        self.flushPosAndSpeed()
        time.sleep(2)
        self.changePosition()

    def changePowerLevel(self):
        print("Power level change thread running")
        self.Pl.set_data(self.Pl.get_power_level() - 0.5)
        time.sleep(10)
        self.changePowerLevel()

    def __init__(self, header, base_station_host, base_station_port, car_host, top_port,
                 car_port, vehicle_pos=None, vehicle_speed=None):

        self.peer_discovery_map = {}
        self.Fs = Fuelsensor("FuelSensor")
        self.Ds = Directionsensor("Directionsensor")
        self.Ls = Lightsensor("Lightsensor")
        self.Ps = Positionsensor("Positionsensor")
        self.Ss = Speedsensor("Speedsensor")
        self.Pl = Powerlevelindicator("Powerlevelindicator")
        self.Lw = Lanewidthsensor("Lanewidthsensor")
        self.Pr = Proximitysensor("Proximitysensor")

        # for running simulation. Positioning vehicles
        if vehicle_pos:
            self.Ps.set_data(vehicle_pos)
        if vehicle_speed:
            self.Ss.set_data(vehicle_speed)

        self.header = header

        self.base_station_port = base_station_port
        self.base_station_host = base_station_host

        self.car_host = car_host
        self.device_top_port = top_port
        self.device_car_port = car_port

        self.peer_map_file = discovery_map_file_name + \
            "_" + self.header + "." + discovery_map_file_ext
        self.peer_messages_file = messages_file_name + \
            "_" + self.header + "." + messages_file_ext

        self.car_info_file = car_info_file_name + \
            "_" + self.header + "." + car_info_file_ext

        client_receiveTopology = Thread(target=self.recvTopology, args=(
            self.device_top_port, self.device_car_port,))
        client_receivePeer = Thread(
            target=self.recvPeerMessages, args=(self.device_car_port,))
        client_joinNetwork = Thread(target=self.joinNetwork, args=(
            self.device_top_port, self.device_car_port,))
        client_gossip = Thread(target=self.gossip)
        client_changePosition = Thread(target=self.changePosition)
        client_changePowerLevel = Thread(target=self.changePowerLevel)

        client_receiveTopology.start()
        client_receivePeer.start()
        client_joinNetwork.start()
        client_gossip.start()
        client_changePosition.start()
        client_changePowerLevel.start()

        client_receiveTopology.join()
        client_receivePeer.join()
        client_joinNetwork.join()
        client_gossip.join()
        client_changePosition.join()
        client_changePowerLevel.join()
