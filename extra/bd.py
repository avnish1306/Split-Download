import argparse, socket, struct

BUFSIZE = 65535

def server(interface, port):
	print("server")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((interface, port))
	print('Listening for datagrams at {}'.format(sock.getsockname()))
	while True:
		data, address = sock.recvfrom(BUFSIZE)
		text = data.decode('ascii')
		print('The client at {} says: {!r}'.format(address, text))

def client(network, port):
	print("client")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	text = 'Broadcast datagram!'
	sock.sendto(text.encode('ascii'), (network, port))

if __name__ == '__main__':
	interface1 = "0.0.0.0"
	interface2 = "192.168.1.255"
	port =2300
	ch = input()
	if(ch=="s"):
		server(interface1,port)
	else:
		client(interface2,port)