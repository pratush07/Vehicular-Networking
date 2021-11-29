from device import vehicle
from threading import Thread
from config import *
import os
import shutil
import time

def main():

    if os.path.exists(discovery_dir):
        shutil.rmtree(discovery_dir)
    
    if os.path.exists(messages_dir):
        shutil.rmtree(messages_dir)
    
    if os.path.exists(stability_dir):
        shutil.rmtree(stability_dir)
    
    time.sleep(3)

    os.makedirs(discovery_dir)
    os.makedirs(messages_dir)
    os.makedirs(stability_dir)
    
    vehicles = []
    
    # two cars forming platoon first.. platoon catches up with a car in the front and they form a platoon 
    vehicles.append(Thread(target=vehicle, args=("device_localhost_31002","localhost", 30201, "localhost",31001,31002,80,5)))
    vehicles.append(Thread(target=vehicle, args=("device_localhost_31004","localhost", 30201, "localhost",31003,31004,300,3)))
    vehicles.append(Thread(target=vehicle, args=("device_localhost_31006","localhost", 30201, "localhost",31005,31006,5,7)))


    for v in vehicles:
        v.start()
    
    for v in vehicles:
        v.join()

if __name__ == '__main__':
    main()