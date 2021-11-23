#import the socket module
import socket
from threading import Thread
import json

def sendMessage():
    #Create a socket instance
    socketObject = socket.socket()

    #Using the socket connect to a server...in this case localhost
    socketObject.connect(("localhost", 31000))
    print("Connected to localhost")
    msg = {"msg" : "hello!"}

    socketObject.send(json.dumps(msg).encode('utf-8'))

clients = []
for i in range(5):
    clients.append(Thread(target=sendMessage))

for client in clients:
    client.start()

for client in clients:
    client.join()


