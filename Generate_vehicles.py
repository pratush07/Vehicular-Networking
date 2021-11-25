from device import vehicle
from threading import Thread
from config import *
import os
import argparse


def main():
    # check for discover and message folders
    if not os.path.exists(discovery_dir):
        os.makedirs(discovery_dir)

    if not os.path.exists(messages_dir):
        os.makedirs(messages_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument('--base-host', help='base station host', type=str)
    parser.add_argument('--base-port', help='base station port', type=int)
    parser.add_argument('--car-host', help='car host for topology', type=str)
    parser.add_argument('--top-port', help='initial port for topology', type=int)
    parser.add_argument('--car-port', help='initial port for cars', type=int)
    parser.add_argument('--devices', help='number of devices in this network', type=int)

    args = parser.parse_args()

    base_station_host = 'localhost'
    base_station_port = 30201
    car_host = 'localhost'

    if args.base_host is not None:
        base_station_host = args.base_host
        
    if args.base_port is not None:
        base_station_port = args.base_port

    if args.top_port is None:
        print("Please specify the initial topology port")
        exit(1)

    if args.car_port is None:
        print("Please specify the initial car port")
        exit(1)

    if args.car_host is not None:
        car_host = args.car_host

    if args.devices is None:
        print("Please specify the number of devices")
        exit(1)

    one = Thread(target=vehicle, args=("device one","localhost", 30201, "localhost",31001,31005,))
    two = Thread(target=vehicle, args=("device two","localhost", 30201, "localhost",31011,31015,))

    vehicle_threads = []



    for i in range(args.devices):
        device_id = car_host + "_" + str(args.car_port+i)
        vehicle_threads.append(
            Thread(target=vehicle, args=("device_" + device_id,base_station_host, 
            base_station_port, car_host, args.top_port+i,args.car_port+i,)))

    for vehicle_thread in vehicle_threads:
        vehicle_thread.start()

    for vehicle_thread in vehicle_threads:
        vehicle_thread.join()

if __name__ == '__main__':
    main()