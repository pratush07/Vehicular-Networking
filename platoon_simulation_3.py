from device import vehicle
from threading import Thread
from config import *
import os
import shutil
import time

def main():

    # check for discover and message folders
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
    

    # two cars forming platoon first.. platoon catches up with a car in the front and they form a platoon. 
    # platoon catches with 4th car ahead
    vehicles.append(Thread(target=vehicle, args=("device_localhost_31002","localhost", 30201, "localhost",31001,31002,80,7)))
    vehicles.append(Thread(target=vehicle, args=("device_localhost_31004","localhost", 30201, "localhost",31003,31004,300,5)))
    vehicles.append(Thread(target=vehicle, args=("device_localhost_31006","localhost", 30201, "localhost",31005,31006,5,9)))
    vehicles.append(Thread(target=vehicle, args=("device_localhost_31008","localhost", 30201, "localhost",31007,31008,500,3)))


    for v in vehicles:
        v.start()
    
    for v in vehicles:
        v.join()

if __name__ == '__main__':
    main()