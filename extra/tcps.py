import socket
import sys
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('', 1703)
print('Starting up on %s port %s' % server_address)
sock.bind(server_address)
sock.listen(3)

print('Waiting for connection')
num=3
abc = []
bcd=[]
while(num!=0):
	num = num-1
	connection, client_address = sock.accept()
	abc.append(connection)
	bcd.append(client_address)
	print(client_address,connection)

print("abc")