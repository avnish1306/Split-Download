import socket
import sys
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.101.177', 1703)
print('Connecting to %s port %s' % server_address)
sock.connect(server_address)
print("connection req sent")