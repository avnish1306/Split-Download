import threading
import time
import socket
import struct
import json
import sys
from services.portServices import get_free_tcp_port
from services.divideFile import divideFile
from services.startDownload import startDownload
from services.getOwnIp import getOwnIp
import ds1
import ds2
import ds3
from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime
fileLink = "https://download.ccleaner.com/ccsetup563.exe"
appendLock = threading.Lock()
segmentsFetched = False
choice = -1
ui1 = "abc"
ui2 = "abc"
ui3 = "abc"
Form = "abc"
Form2 = None
app = "abc"
isMaster = False
isBusy = False  # Tell whether the this system is already busy in some download or not
PORT = 5200
BUFSIZE = 655350
broadcastPort = 2100
tcpPort = 8888
clientsIp = []  # list to store clients
tcpConnectionList = []
broadcastInterface = "255.255.255.255"
broadcastListenInterface = "0.0.0.0"
multicastInterface = '224.1.1.1'
multicastPort = 1306
basePort = 6000
isAnnouncementOn = True
ipSockMap = {}
ipThreadMap = {}
ipPortMap = {}
clientFileSection = {}
clientIpSegmentMap = {}
OWNPORT = get_free_tcp_port()
OWNIP = getOwnIp()    #socket.gethostbyname(socket.gethostname()) 


class MSG:
    master = None
    msg = None
    data = None

    def __init__(self, data, msg="", master=False):
        self.master = master
        self.msg = msg
        self.data = data

    def view(self):
        print("\nMaster: ", self.master, "\nMessage: ",
              self.msg, "\nData: ", self.data)

    def getJson(self):
        return {'master': self.master, 'msg': self.msg, 'data': self.data}

    def loadJson(self, rawData):
        decodedData = rawData.decode('ASCII')
        obj = json.loads(decodedData)           #returns an object from a string representing a json object.
        self.master = obj['master']
        self.msg = obj['msg']
        self.data = obj['data']

    def dumpJson(self):
        rawData = json.dumps(self.getJson())    #returns a string representing a json object from an object.
        return rawData.encode('ASCII')

distributionMsg = MSG({})

def initiateDownload(args):
    segment = args[0]
    fileLink = args[1]
    startDownload(segment, fileLink)

def listenBroadcast(arg):  # client
    data = address = None
    print("listening broadcast started")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((broadcastListenInterface, broadcastPort))
    res = MSG({})
    print('Listening for master at {}'.format(sock.getsockname()))
    while True:
        # receive broadcast message
        # if the message is from master exit the while loop else continue listening
        data, address = sock.recvfrom(BUFSIZE)
        res.loadJson(data)
        if(res.master == True or res.master == "True"):
                break
        sock.close()
    if res.msg == 'Add request':
        tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Making connection with the Master at IP = {} and Port = {}".format(
            address[0], tcpPort))
        tcpServerAddress = (address[0], tcpPort)
        tcpSock.connect(tcpServerAddress)
        rawData = tcpSock.recv(BUFSIZE)
        distributionMsg = MSG({})
        distributionMsg.loadJson(rawData)
        print("distribution message recieved ")
        distributionMsg.view()
        #print(distributionMsg.data['clientIpSegmentMap'] , OWNIP)
        segment = distributionMsg.data['clientIpSegmentMap'][OWNIP]
        print (segment)
        fileLink = distributionMsg.data['fileLink']
        initiateDownloadThread = threading.Thread(
            target=initiateDownload, args=((segment, fileLink),))  # Download Started
        initiateDownloadThread.start()
        tcpSock.close()
        print("listening to master ended")


def announceBroadcast(arg):
    global isAnnouncementOn
    global choice
    print("announcing broadcast started")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while(True):
        res = MSG({}, "Add request", isMaster)
        sock.sendto(res.dumpJson(), (broadcastInterface, broadcastPort))
        time.sleep(1)
        for i in clientsIp:
            print("ip: ", i)
        print("enter 1 for reannounce or 0 to end announcement")
        # refreshList()
        while(choice == -1):
            pass
        if(choice == 0):
            isAnnouncementOn = False
            res.msg = 'Broadcast Ends'
            sock.sendto(res.dumpJson(), (broadcastInterface, broadcastPort))
            break
        choice = -1
    # announce the welcome message over network
    # display received ips
    # check if user want to announce again or not and continue the loop if refresh happen
    # conditional : global isAnnouncementOn = False
    sock.close()
    print("announcing broadcast ended")

def masterAcceptConnection(args):
    global segmentsFetched
    global distributionMsg
    connection = args[0]
    # address = args[1]
    # print(connection, address)
    # appendLock.acquire()
    # clientsIp.append(address[0])
    # ipSockMap[address[0]] = connection
    # appendLock.release()
    # while(segmentsFetched == False):
    #     continue
    # now = datetime.now()
    connection.sendall(distributionMsg.dumpJson())

def listenTcp(arg):
    tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverAddress = (OWNIP, tcpPort)
    tcpSock.bind(serverAddress)
    tcpSock.listen(10)
    while(True):       
        connection, address = tcpSock.accept()
        tcpConnectionList.append((connection, address))
        clientsIp.append(address[0])
        ipSockMap[address[0]] = connection
        print('Connected to :', address[0], ':', address[1])
        if choice == 0:
            break

def Master(arg):
    startMasterScreen()
    global isMaster
    isMaster = True
    global isAnnouncementOn
    isAnnouncementOn = True
    
    listenTcpThread = threading.Thread(target=listenTcp, args = ("",))
    listenTcpThread.start()
    announceBroadcastThread = threading.Thread(
        target=announceBroadcast, args=("",))
    announceBroadcastThread.start()
    while(announceBroadcastThread.isAlive()):
        pass
    # if got all the clients, Time to distribute the file and send it to others
    if not announceBroadcastThread.isAlive():
        global segmentsFetched
        global distributionMsg
        clientsIp.append(OWNIP)  
        clientIpSegmentMap = divideFile(fileLink, clientsIp)
        distributionMsg = MSG(
            {"fileLink": fileLink, "clientIpSegmentMap": clientIpSegmentMap}, "Distribution message", isMaster)
        print("This is the distribution msg ")
        distributionMsg.view()
        for element in tcpConnectionList:
            masterAcceptConnectionThread = threading.Thread(target = masterAcceptConnection, args = ((element[0],element[1]),))
            masterAcceptConnectionThread.start()       
        segmentsFetched = True
        segment = clientIpSegmentMap[OWNIP]
        initiateDownloadThread = threading.Thread(target=initiateDownload, args=(
            (segment, fileLink),))  # Download Started in Master
        initiateDownloadThread.start()

        # make direct connection and send the distribution message
        # check if clientIp is it's own ip or not and is there already a connection or not


def Client():
    listenBroadcastThread = threading.Thread(
        target=listenBroadcast, args=("",))
    listenBroadcastThread.start()
    while(listenBroadcastThread.isAlive()):
        pass
    # clientsIp = clientsIp+ list(distributionMsg.data['clientIpSegmentMap'].keys())
    # for clientIp in clientsIp:
    # 	ipPortMap[clientIp] = distributionMsg.data['clientIpSegmentMap'][clientIp]['port']

    # clientsCount = len(clientsIp)
    # sock.listen(clientsCount-2) #removed its own count and master

    # acceptConnectionsThread=threading.Thread(target=acceptConnections,args=({'sock':sock,'clientsCount':clientsCount},))
    # acceptConnectionsThread.start()

    # for clientIp in clientsIp:
    # 	if clientIp in ipSockMap:
    # 		print("Aleardy connected")
    # 	elif clientIp == OWNIP:
    # 		print("Skipping since this is my ip: ",clientIp)
    # 	else:
    # 		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 		print("making connection request with: ",clientIp)
    # 		server_address = (clientIp, ipPortMap[clientIp])
    # 		print('Connecting to %s port %s' % server_address)
    # 		sock.connect(server_address)
    # 		print("connected to client: ",clientIp)
    # 		ipSockMap[clientIp] = sock

    # make one thread to accept the connections

    # recv distribution message from master
    # accept connection request from master and get the distributionMsg details
    # store the clients ip in clientsIp
    # for clientIp in clientsIp:
        #print("make connection")
        # make direct connection
        # check if clientIp is it's own ip or not and is there already a connection or not

#test = MSG()
# test.view()


def startMasterScreen():
    global app
    global Form2
    global Form
    # Form.close()
    #app = QtWidgets.QApplication(sys.argv)

    # Form2.show()
    # ui2.Master.clicked.connect(Master)
    # ui1.Client.clicked.connect(Client)

    # Form.show()
    # sys.exit(app.exec_())


def startMasterUtil():
    print("Master")
    masterThread = threading.Thread(target=Master, args=('',))
    masterThread.start()
    Form.close()
    Form2.show()
    refreshList()


def reannounce():
    global choice
    choice = 1
    refreshList()


def refreshList():
    global clientsIp
    model = QtGui.QStandardItemModel()
    ui2.listView.setModel(model)

    for i in clientsIp:
        item = QtGui.QStandardItem(i)
        model.appendRow(item)


def endAnnounceMent():
    global choice
    choice = 0


if __name__ == "__main__":
        # print("Program started")
        # #logic to trigger master and client
        # print("enter 1 for master, 0 for client")
        # x=int(input())
        # if(x==0):
        # 	isMaster=False
        # else:
        # 	isBusy=True  #if the system is a master, it will not involve in other download
        # 	isMaster=True
        # #logicEnd

        # if(isMaster):

        # else:
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui1 = ds1.Ui_Form()
    ui1.setupUi(Form)
    Form2 = QtWidgets.QWidget()
    ui2 = ds2.Ui_Form()
    ui2.setupUi(Form2)
    ui1.Master.clicked.connect(startMasterUtil)
    ui1.Client.clicked.connect(Client)
    ui2.Refresh.clicked.connect(reannounce)
    ui2.Next.clicked.connect(endAnnounceMent)
    Form.show()
    # Form2.show()
    sys.exit(app.exec_())
    while(True):
        pass
