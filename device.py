# import the socket module

import socket
from threading import Thread, Lock
import json
import time
from Sensors.SpeedSensor import Speedsensor
from config import *
import os
import random

from Sensors.FuelSensor import Fuelsensor
from Sensors.DirectionSensor import Directionsensor
from Sensors.LightSensor import Lightsensor
from Sensors.PositionSensor import Positionsensor
from Sensors.SpeedSensor import Speedsensor


class vehicle:

    def flushPeerDiscoveryMap(self):
        print('saving peer discovery to file..')
        file_path = os.path.join(discovery_dir, self.peer_map_file)
        with open(file_path, 'w') as f:
            json.dump(self.peer_discovery_map, f)

    
    def flushMessages(self, message):  
        print('saving peer messages to file..')
        file_path = os.path.join(messages_dir,self.peer_messages_file)    
        try:    
            with open(file_path,'r') as f:
                lines = f.readlines()
                for line in lines:
                    temp = json.loads(line)
                    if (temp['sender'] == message['sender']):
                        lines[int(message['sender'])] = message + "\n"
     
            with open(file_path,'w') as f:
                f.writelines(lines)
                f.close()
        except:
            with open(file_path,'w+') as f:
                json.dump(message, f)
                f.write('\n')


    # update peer discovery map for each peer
    def updatePeerDiscoveryMap(self, peer, routingTable):
        car_ports = []
        for key, data in routingTable.items():
            if self.header != key and self.header != data['header']:
                car_ports.append((data['address'],data['car_port'],data['header']))

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

    def recvPeerMessages(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
            print('listening to car messages')
            print('binding to ' + str(port))
            socketObject.bind((self.car_host, port))
            socketObject.listen()

            # listen continuously for the topology info as new peers join
            while True:
                conn, _ = socketObject.accept()
                message = json.loads(conn.recv(4096).decode('utf-8'))
  

                
                if message['message'] == 'gossip':
                    print('%s (%s:%s) Incoming Message -> %s (sent by %s)' 
                    % (self.header, self.car_host,str(port),str(message), message['sender']))
                    self.flushMessages(message)
                
                if (self.Status == "Looking for platoon"):
                    Thread(target = self.lookforPrevcar()).start()
                    
                if message['message'] == 'Join Platoon' and self.Status == "Looking for Platoon":
                    print("Joining platoon")
                    Thread(target=self.joinnewPlatoon(message)).start()
    
    
    def lookforPrevcar(self):
        file_path = os.path.join(messages_dir,self.peer_messages_file)
        current_pos = self.Ps.get_data()['X']
        tempPrevCar = ""
        tempClosest = 999999
        tempData = ""
        timetojoin = 0
        StableSpeed = 0
        
        print("check")
        with open(file_path,'r') as f:
            lines = f.readlines()
            for line in lines:
                line = json.loads(line)
                if (current_pos - line['position']['X'] < tempClosest and current_pos - line['position']['X'] > 0) :
                    tempClosest = current_pos - line['position']['X']
                    tempPrevCar = line['sender']
                    tempData = line
                    
        if tempPrevCar != "" :
            self.Status = "Joining Platoon"
            StableSpeed = int(abs(tempData['speed']['speed'] + self.Ss.get_data()['speed'])/2)
            
            if tempData['speed']['speed'] - self.Ss.get_data()['speed'] < 0 or (current_pos - line['position']['X'] - distance_threshold)/(tempData['speed']['speed'] - self.Ss.get_data()['speed']) > timetojoin_threshold:
                if (current_pos - line['position']['X'] - distance_threshold)/timetojoin_threshold > maxSpeed:
                    newSpeed = maxSpeed
                    timetojoin = (current_pos - line['position']['X'] - distance_threshold)/newSpeed
                else:
                    newSpeed = (current_pos - line['position']['X'] - distance_threshold)/timetojoin_threshold + self.Ss.get_data()['speed']
                    timetojoin = timetojoin_threshold
            else:
                newSpeed = tempData['speed']['speed']
                timetojoin = (current_pos - line['position']['X'] - distance_threshold)/(tempData['speed']['speed'] - self.Ss.get_data()['speed'])

            messageID = random.randrange(10000)
            
            for _, dests in self.peer_discovery_map.items():
                for dest in dests:
                    if dest[2] == tempPrevCar :
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((dest[0], dest[1]))  
                            payload = {}
                            payload['message'] = 'Join Platoon'
                            payload['StableSpeed'] = StableSpeed
                            payload['newSpeed'] = newSpeed
                            payload['timetojoin'] = timetojoin
                            payload['messageID'] = messageID
                            s.send(json.dumps(payload).encode('utf-8'))
            #print('timetojoin: ' + timetojoin )            
            time.sleep(timetojoin)
            self.Ss.set_data(StableSpeed)
            self.Status = "Stable Platoon formed"
            print("Stable front")
        

    def joinnewPlatoon(self, message):
        self.Status == "Join Platoon"
        self.Ss.set_data(message['newSpeed'])
        time.sleep(message['timetojoin'])
        self.Ss.set_data(message['StableSpeed'])
        self.Status = "Stable Platoon formed"
        print("Stable rear")
    

    def gossip(self):
        print('%s (%s:%s) is sending messages to peers' %
              (self.header, self.car_host, self.device_car_port))
        if len(self.peer_discovery_map) != 0:
            for _, dests in self.peer_discovery_map.items():
                for dest in dests:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((dest[0], dest[1]))
                        payload = {}
                        payload['message'] = 'gossip'
                        payload['fuel'] = self.Fs.get_data()
                        payload['direction'] = self.Ds.get_data()
                        payload['light'] = self.Ls.get_data()
                        payload['position'] = self.Ps.get_data()
                        payload['speed'] = self.Ss.get_data()
                        payload['status'] = self.Status
                        payload['sender'] = self.header
                        s.send(json.dumps(payload).encode('utf-8'))
                        time.sleep(2)

        else:
            print('no device active..')
        #print('going to sleep..')
        time.sleep(5)
        self.gossip()

    def changePosition(self):
        #print("Position change thread running")
        x = self.Ps.get_data()
        speed = self.Ss.get_data()
        dist = speed['speed'] * 2  # 2 is the time interval, same for thread sleep
        self.Ps.set_data(x['X']+dist)
        time.sleep(2)
        self.changePosition()

    def __init__(self, header, base_station_host, base_station_port, car_host, top_port, car_port, X, speed):

        self.peer_discovery_map = {}
        self.Fs = Fuelsensor("FuelSensor")
        self.Ds = Directionsensor("Directionsensor")
        self.Ls = Lightsensor("Lightsensor")
        self.Ps = Positionsensor("Positionsensor")
        self.Ss = Speedsensor("Speedsensor")
        
        self.Ps.set_data(X)
        self.Ss.set_data(speed)
        
        self.header = header
        self.Status = "Looking for platoon"
        self.base_station_port = base_station_port
        self.base_station_host = base_station_host

        self.car_host = car_host
        self.device_top_port = top_port
        self.device_car_port = car_port

        self.peer_map_file = discovery_map_file_name + \
            "_" + self.header + "." + discovery_map_file_ext
        self.peer_messages_file = messages_file_name + \
            "_" + self.header + "." + messages_file_ext

        client_receiveTopology = Thread(target=self.recvTopology, args=(
            self.device_top_port, self.device_car_port,))
        client_receivePeer = Thread(
            target=self.recvPeerMessages, args=(self.device_car_port,))
        client_joinNetwork = Thread(target=self.joinNetwork, args=(
            self.device_top_port, self.device_car_port,))
        client_gossip = Thread(target=self.gossip)
        client_changePosition = Thread(target=self.changePosition)

        client_receiveTopology.start()
        client_receivePeer.start()
        client_joinNetwork.start()
        client_gossip.start()
        client_changePosition.start()

        client_receiveTopology.join()
        client_receivePeer.join()
        client_joinNetwork.join()
        client_gossip.join()
        client_changePosition.join()
