from device import vehicle
from threading import Thread
from config import *
import os
import shutil
import time
import argparse
from platoon_config import *
from secure_comm import generate_keys

def main():
    if os.path.exists(discovery_dir):
        shutil.rmtree(discovery_dir)
    
    if os.path.exists(messages_dir):
        shutil.rmtree(messages_dir)
    
    if os.path.exists(stability_dir):
        shutil.rmtree(stability_dir) 
    
    if os.path.exists(car_info_dir):
        shutil.rmtree(car_info_dir)
    
    if os.path.exists(security_dir):
        shutil.rmtree(security_dir) 
    
    time.sleep(3)

    os.makedirs(discovery_dir)
    os.makedirs(messages_dir)
    os.makedirs(stability_dir)
    os.makedirs(car_info_dir)

    generate_keys()


    parser = argparse.ArgumentParser()
    parser.add_argument('--base-host', help='base station host', type=str)
    parser.add_argument('--base-port', help='base station port', type=int)
    parser.add_argument('--car-host', help='car host', type=str)
    parser.add_argument('--simulation', help='allowed values are [1,2,3]', type=int)

    
    args = parser.parse_args()
    
    base_station_host = 'localhost'
    base_station_port = 30201
    car_host = 'localhost'

    if args.base_host is not None:
        base_station_host = args.base_host
        
    if args.base_port is not None:
        base_station_port = args.base_port
    
    if args.car_host is not None:
        car_host = args.car_host
    
    if args.simulation is None or args.simulation not in [1,2,3]:
        print('provide simulation config number from [1,2,3]')
        exit(1)

    
    vehicles = []

    if args.simulation == 1:
        cars_config = cars_config_1
    elif args.simulation == 2:
        cars_config = cars_config_2
    elif args.simulation == 3:
        cars_config = cars_config_3
    

    for car in cars_config:
        vehicles.append(Thread(target=vehicle, args=("device_" + car_host + "_" + str(car['car_port']),
        base_station_host, base_station_port, car_host,car['top_port'],car['car_port'],
        car['position'],car['speed'])))

    for v in vehicles:
        v.start()
    
    for v in vehicles:
        v.join()

if __name__ == '__main__':
    main()