import threading
import time
import socket
import struct,json
from services.portServices import get_free_tcp_port
isMaster=False
isBusy=False  #Tell weather the this system is already busy in some download or not
PORT=5200
BUFSIZE = 655350
broadcastPort = 2100
clientsIp=[] #list to store clients
broadcastInterface = "192.168.1.255"
broadcastListenInterface = "0.0.0.0"
multicastInterface = '224.1.1.1'
multicastPort = 1306
basePort = 6000
isAnnouncementOn = True
ipSockMap={}
ipThreadMap={}
ipPortMap={}
OWNPORT = get_free_tcp_port()
OWNIP = '192.168.1.118'# socket.gethostbyname(socket.gethostname())
tcpPort = 5500
class MSG:
	master = None
	msg = None
	data = None
	def __init__(self,data,msg="", master = False):
		self.master = master
		self.msg = msg
		self.data = data
	def view(self):
		print("\nMaster: ",self.master,"\nMessage: ",self.msg,"\nData: ",self.data)
	def getJson(self):
		return {'master':self.master,'msg':self.msg,'data':self.data}
	def loadJson(self,rawData):
		decodedData = rawData.decode('ASCII')
		obj = json.loads(decodedData)
		self.master = obj['master']
		self.msg = obj['msg']
		self.data = obj['data']
	def dumpJson(self):
		rawData = json.dumps(self.getJson())
		return rawData.encode('ASCII')

def listenBroadcast(arg): #client
	print("listening broadcast started")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((broadcastListenInterface, broadcastPort))
	res = MSG({})
	print('Listening for master at {}'.format(sock.getsockname()))
	while True:
		#receive broadcast message
		#if the message is from master exit the while loop else continue listening
		data, address = sock.recvfrom(BUFSIZE)
		res.loadJson(data)
		if(res.master==True or res.master=="True"):
			break
		#print('The client at {} says: {!r}'.format(address, text))
	hostname = socket.gethostname()
	ownIp = socket.gethostbyname(hostname)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	res = MSG({'ip':OWNIP,'port':OWNPORT})
	sock.sendto(res.dumpJson(), (broadcastInterface, broadcastPort))#sock.sendto(res.dumpJson(), (multicastInterface, multicastPort))
	#broadcast own ip
	print("listening to master ended")
	
	
	

def announceBroadcast(arg): #master
	global isAnnouncementOn
	print("announcing broadcast started")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	while(True):
		res = MSG({},"Add request",isMaster)
		sock.sendto(res.dumpJson(), (broadcastInterface, broadcastPort))
		time.sleep(1)
		for i in clientsIp:
			print("ip: ",i)
		print("enter 1 for reannounce or 0 to end announcement")
		choice = int(input())
		if(choice==0):
			isAnnouncementOn = False
			sock.sendto(res.dumpJson(), (broadcastInterface, broadcastPort))
			break
		#announce the welcome message over network
		#display received ips
		#check if user want to announce again or not and continue the loop if refresh happen
		# conditional : global isAnnouncementOn = False
	print("announcing broadcast ended")
	
def listenBroadcastReply(arg): #master
	global isAnnouncementOn
	print("listening broadcast reply started")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#sock.bind(('', multicastPort)) #need to be changed
	#mreq = struct.pack("4sl", socket.inet_aton(multicastInterface), socket.INADDR_ANY)
	#sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	sock.bind((broadcastListenInterface, broadcastPort))
	res = MSG({})
	while True:
		print("in recv")
		
		data, address = sock.recvfrom(BUFSIZE)
		print("in recv", isAnnouncementOn)
		res.loadJson(data)
		res.view()
		if(isAnnouncementOn==False or isAnnouncementOn=="False"):
			break
		if(res.master):
	
			continue
		if(not (res.data['ip'] in clientsIp)):
			clientsIp.append(res.data['ip'])
			ipPortMap[res.data['ip']] = res.data['port']
		print(clientsIp , ipPortMap, 'Alka', isAnnouncementOn)
		
		if(isAnnouncementOn==False or isAnnouncementOn=="False"):
			break
		#receive client's reply and add ip to ip list
		#check if announcement is still going on or not
		#if announcement is on then continue reading else exit
	print("listening broadcast reply ended")

def acceptConnections(arg):
	clientsCount = arg['clientsCount']
	while(True):
		connection, address = arg['sock'].accept()
		if address[0] in ipSockMap:
			print("Connection has been already accepted")
		elif address[0] == OWNIP:
			print("Skipping since this is my ip: ",clientIp)
		else:
			print("Accepting the connection ",clientIp)
			ipSockMap[address[0]] = connection
		tempCount = len(list(ipSockMap.keys()))
		if(tempCount>=(clientsCount+1)): # clientsCount = total - (1)master - 1(itself) but clientsIp map will contain master also
			print("All clients are connected")
			break

			

	
if __name__ == "__main__":
	print("Program started")
	#logic to trigger master and client
	print("enter 1 for master, 0 for client")
	x=int(input())
	if(x==0):
		isMaster=False
	else:
		isBusy=True  #if the system is a master, it will not involve in other download
		isMaster=True
	#logicEnd
	
	if(isMaster):
		isAnnouncementOn = True
		listenBroadcastRelpyThread=threading.Thread(target=listenBroadcastReply,args=("",))
		listenBroadcastRelpyThread.start()
		announceBroadcastThread=threading.Thread(target=announceBroadcast,args=("",))
		announceBroadcastThread.start()
		while(announceBroadcastThread.isAlive()):
			pass
		if not announceBroadcastThread.isAlive(): #if got all the clients, Time to distribute the file and send it to others
			fileLink = "https://abc.com/download"
			fileSize = 1000 #get from curl
			#logic to divide file among all clients
			clientIpSegmentMap = {}
			clientIpSegmentMap[OWNIP]={'segment':"1-100",'port':OWNPORT}
			for clientIp in clientsIp:
				clientIpSegmentMap[clientIp]={'segment':"1-100",'port':ipPortMap[clientIp]}
			distributionMsg = MSG({"fileLink":fileLink, "clientIpSegmentMap":clientIpSegmentMap},"Distribution message",isMaster)
			print("this is the distribution msg ")
			distributionMsg.view()
			for clientIp in clientsIp:
				print("ip and port ",clientIp, ipPortMap[clientIp])
				if clientIp in ipSockMap:
					print("Aleardy connected")
				elif clientIp == OWNIP:
					print("Skipping since this is my ip: ",clientIp)
				else:
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					print("making connection with: ",clientIp)
					server_address = (clientIp, ipPortMap[clientIp] )
					print('Connecting to %s port %s' % server_address)
					sock.connect(server_address)
					print("connected to client: ",clientIp)
					ipSockMap[clientIp] = sock
					sock.sendall(distributionMsg.dumpJson())
					print("distribution message sent")
				#make direct connection and send the distribution message
				#check if clientIp is it's own ip or not and is there already a connection or not
	else:
	
		listenBroadcastThread=threading.Thread(target=listenBroadcast,args=("",))
		listenBroadcastThread.start()
		while(listenBroadcastThread.isAlive()):
			pass
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('', OWNPORT)
		
		sock.bind(server_address)
		sock.listen(1)
		print('Waiting for master to connect on %s port %s' % server_address)
		connection, address = sock.accept()
		print("connected to master")
		clientsIp.append(address[0])
		ipSockMap[address[0]] = connection
		rawData = connection.recv(BUFSIZE)
		distributionMsg = MSG({})
		distributionMsg.loadJson(rawData)
		print("distribution message recieved ")
		distributionMsg.view()
		clientsIp =clientsIp+ list(distributionMsg.data['clientIpSegmentMap'].keys())
		for clientIp in clientsIp:
			ipPortMap[clientIp] = distributionMsg.data['clientIpSegmentMap'][clientIp]['port']
		clientsCount = len(clientsIp)
		sock.listen(clientsCount-2) #removed its own count and master

		acceptConnectionsThread=threading.Thread(target=acceptConnections,args=({'sock':sock,'clientsCount':clientsCount},))
		acceptConnectionsThread.start()
		
		for clientIp in clientsIp:
			if clientIp in ipSockMap:
				print("Aleardy connected")
			elif clientIp == OWNIP:
				print("Skipping since this is my ip: ",clientIp)
			else:
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				print("making connection request with: ",clientIp)
				server_address = (clientIp, ipPortMap[clientIp])
				print('Connecting to %s port %s' % server_address)
				sock.connect(server_address)
				print("connected to client: ",clientIp)
				ipSockMap[clientIp] = sock

		#make one thread to accept the connections
		
		#recv distribution message from master
		#accept connection request from master and get the distributionMsg details
		#store the clients ip in clientsIp
		#for clientIp in clientsIp:
			#print("make connection")
				#make direct connection
				#check if clientIp is it's own ip or not and is there already a connection or not
				
	#test = MSG()
	#test.view()