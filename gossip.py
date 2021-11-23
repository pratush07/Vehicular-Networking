import os
from config import *
import json
import socket
import time

peer_discovery_global = {}

def gossip_init():
    for file in os.listdir(discovery_dir):
        file_path = os.path.join(discovery_dir, file)
        with open(file_path, 'r') as f:
            data = json.load(f)
            for src, dests in data.items():
                for dest in dests:
                    if int(src) != dest:
                        print(src, dest)
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect(('localhost', dest))
                            s.send(json.dumps({'msg': 'hello from car port ' + str(src)}).encode('utf-8'))
    time.sleep(5)
    gossip_init()

def main():
    gossip_init()

if __name__ == '__main__':
    main()