#import the socket module
import socket
from threading import Thread
import json

def sendMessage():
    #Create a socket instance
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObject:
        socketObject = socket.socket()

        #Using the socket connect to a server...in this case localhost
        socketObject.connect(("localhost", 31000))
        print("Connected to localhost")
        msg = {"msg" : "hello!"}

        socketObject.send(json.dumps(msg).encode('utf-8'))

sendMessage()