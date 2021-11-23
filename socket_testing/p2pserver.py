import socket

# Create a server socket
serverSocket = socket.socket()
print("Server socket created")
# Associate the server socket with the IP and Port
ip      = "localhost"
port    = 35491
serverSocket.bind((ip, port))

print("Server socket bound with with ip {} port {}".format(ip, port))

# Make the server listen for incoming connections
serverSocket.listen()

while True:
    (clientConnection, clientAddress) = serverSocket.accept()
    data = clientConnection.recv(1024)
    print(clientAddress, data)
