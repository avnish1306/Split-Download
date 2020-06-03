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
from services.sendFile import sendFile
from services.recvFile import recvFile
from services.getFileDetails import getFileDetails
from services.merge import merge
import ds1
import ds2
import ds3
from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime
import logging
from time import sleep
from random import random

fileLink = "https://dl.google.com/tag/s/appguid%3D%7B8A69D345-D564-463C-AFF1-A69D9E530F96%7D%26iid%3D%7B2A0BAEDD-4834-F37C-6BB6-2BD8AA910DF4%7D%26lang%3Den%26browser%3D4%26usagestats%3D1%26appname%3DGoogle%2520Chrome%26needsadmin%3Dprefers%26ap%3Dx64-stable-statsdef_1%26brand%3DCHBD%26installdataindex%3Dempty/update2/installers/ChromeSetup.exe"
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
broadcastInterface = "192.168.43.255"
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
clientIpList=[]
FORMAT = '[%(asctime)-15s] {%(filename)s} {%(funcName)s} {%(lineno)d} %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)

class MSG:
    master = None
    msg = None
    data = None

    def __init__(self, data, msg="", master=False):
        self.master = master
        self.msg = msg
        self.data = data

    def view(self):
        logging.warning(f"\n\nMaster: {self.master}\nMessage: {self.msg}\nData: {self.data}\n\n")

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

def listenClientTcpReq(arg):
    global clientIpList
    tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverAddress = (OWNIP, tcpPort)
    tcpSock.bind(serverAddress)
    totalClients = len(clientIpList)
    tcpSock.listen(totalClients)
    # logging.warning("ipSockMap.keys(): ",len(ipSockMap.keys()), "  totalClients: " , totalClients)
    while(len(ipSockMap.keys())<totalClients):    
        connection, address = tcpSock.accept()
        logging.warning(f'Accepted connection: {connection}')
        if address[0] not in ipSockMap:
            ipSockMap[address[0]]=connection
        logging.warning(f'Connected to client(Inside listenClientTcpReq): {address[0]}, {address[1]}')
        logging.warning(f"ipSockMap.keys(): {len(ipSockMap.keys())}  totalClients:  {totalClients}")
        if len(ipSockMap.keys())==totalClients:
            logging.warning("All clients connected")
            break
    logging.warning("Exiting listenClientTcpReq")

 
def initiateDownload(args):
    segment = args[0]
    fileLink = args[1]
    startDownload(segment, fileLink)

def listenBroadcast(arg):  # client
    global clientIpList
    data = address = None
    logging.warning("listening broadcast started")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((broadcastListenInterface, broadcastPort))
    res = MSG({})
    logging.warning('Listening for master at {}'.format(sock.getsockname()))
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
        logging.warning("Making connection with the Master at IP = {} and Port = {}".format(
            address[0], tcpPort))
        tcpServerAddress = (address[0], tcpPort)
        tcpSock.connect(tcpServerAddress)
        rawData = tcpSock.recv(BUFSIZE)
        distributionMsg = MSG({})
        distributionMsg.loadJson(rawData)
        logging.warning("distribution message received ")
        distributionMsg.view()
        #logging.warning(distributionMsg.data['clientIpSegmentMap'] , OWNIP)
        
        clientIpSegmentMap = distributionMsg.data['clientIpSegmentMap']
        segment = clientIpSegmentMap[OWNIP]
        logging.warning (segment)
        fileLink = distributionMsg.data['fileLink']
        ipSockMap[address[0]] = tcpSock
        ipSockMap[OWNIP] = None
        clientIpList = distributionMsg.data['clientIpSegmentMap'].keys()
        listenClientTcpReqThread = threading.Thread(target=listenClientTcpReq, args = ("",))
        listenClientTcpReqThread.start()

        url = fileLink.split('/')
        
        recvFileThread = None
        sleep(random()*10)
        for client in clientIpList:
            if client not in ipSockMap:
                tcpServerAddress = (client, tcpPort)
                tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcpSock.connect(tcpServerAddress)
                logging.warning(f'Requested connection: {tcpSock}')  
                ipSockMap[client]=tcpSock

        threads = []

        for client in ipSockMap:
            if(client != OWNIP):
                tcpSock = ipSockMap[client]
                # filename = str(url[len(url) - 1]) + str(clientIpSegmentMap[client])
                filename, filesize = getFileDetails(OWNIP, distributionMsg, tcpSock)
                recvFileThread = threading.Thread(target=recvFile,args=((tcpSock,filename,filesize),))
                recvFileThread.start()
                threads.append(recvFileThread)

        for x in ipSockMap:
            logging.warning(x)

        initiateDownloadThread = threading.Thread(
            target=initiateDownload, args=((segment, fileLink),))  # Download Started
        initiateDownloadThread.start()
        
        
        # while(initiateDownloadThread.is_alive()):
        #     pass
        
        filename = str(url[len(url) - 1]).split('.')[0] + str(segment) +'.spld'


        # if not initiateDownloadThread.is_alive():
        for ipSock in ipSockMap:
            client = ipSock
            if client != OWNIP:
                logging.warning(f'{ipSock}, {ipSockMap[ipSock]}')
                tcpSock = ipSockMap[client]
                fname, filesize = getFileDetails(OWNIP, distributionMsg, tcpSock, False)
                sendFileThread = threading.Thread(target=sendFile,args=((tcpSock,filename,filesize),))
                sendFileThread.start()
                threads.append(sendFileThread)

        # logging.warning("recvThread joined.")
        # recvFileThread.join()
        # # logging.warning("sendThread joined")
        # sendFileThread.join()
        for thread in threads:
            thread.join()
        logging.warning("Out of all Send and Recv Threads.")
        # listenClientTcpReqThread.join()
        # logging.warning("Out of listenClientTcpReqThread.")  
        regexFile = str(url[len(url) - 1]).split('.')[0]
        filename = str(url[len(url) - 1])
        merge(regexFile,filename)
        # tcpSock.close()
        logging.warning("listening to master ended")


def announceBroadcast(arg):
    global isAnnouncementOn
    global choice
    logging.warning("announcing broadcast started")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while(True):
        res = MSG({}, "Add request", isMaster)
        sock.sendto(res.dumpJson(), (broadcastInterface, broadcastPort))
        time.sleep(1)
        for i in clientsIp:
            logging.warning(f"ip: {i}")
        logging.warning("enter 1 for reannounce or 0 to end announcement")
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
    logging.warning("announcing broadcast ended")

def masterAcceptConnection(args):
    global segmentsFetched
    global distributionMsg
    connection = args[0]
    # address = args[1]
    # logging.warning(connection, address)
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
        # recvFileThread = threading.Thread(target=recvFile,args=((tcpSock,filename),))
        # recvFileThread.start()
        logging.warning(f'Connected to : {address[0]} : {address[1]}')
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
    while(announceBroadcastThread.is_alive()):
        pass
    # if got all the clients, Time to distribute the file and send it to others
    if not announceBroadcastThread.is_alive():
        global segmentsFetched
        global distributionMsg
        clientsIp.append(OWNIP)  
        clientIpSegmentMap = divideFile(fileLink, clientsIp)
        distributionMsg = MSG(
            {"fileLink": fileLink, "clientIpSegmentMap": clientIpSegmentMap}, "Distribution message", isMaster)
        logging.warning("This is the distribution msg ")
        distributionMsg.view()
        for element in tcpConnectionList:
            masterAcceptConnectionThread = threading.Thread(target = masterAcceptConnection, args = ((element[0],element[1]),))
            masterAcceptConnectionThread.start() 
              
        segmentsFetched = True
        segment = clientIpSegmentMap[OWNIP]

        url = fileLink.split('/')

        threads = []
        for ipSock in ipSockMap:
            client = ipSock
            if client != OWNIP:
                logging.warning(f'{ipSock}, {ipSockMap[ipSock]}')
                tcpSock = ipSockMap[client]
                # filename = str(url[len(url) - 1]) + str(clientIpSegmentMap[client])
                filename, filesize = getFileDetails(OWNIP, distributionMsg, tcpSock)
                recvFileThread = threading.Thread(target=recvFile,args=((tcpSock,filename,filesize),))
                recvFileThread.start()
                threads.append(recvFileThread)

        initiateDownloadThread = threading.Thread(target=initiateDownload, args=(
            (segment, fileLink),))  # Download Started in Master
        initiateDownloadThread.start()


        # while(initiateDownloadThread.is_alive()):
        #     pass

        segment = clientIpSegmentMap[OWNIP]
        filename = str(url[len(url) - 1]).split('.')[0] + str(segment) + '.spld'

        # if not initiateDownloadThread.is_alive():
        for ipSock in ipSockMap:
            client = ipSock
            if client != OWNIP:
                # logging.warning(ipSock, ipSockMap[ipSock])
                tcpSock = ipSockMap[client]
                fname, filesize = getFileDetails(OWNIP, distributionMsg, tcpSock, flag = False)
                sendFileThread = threading.Thread(target=sendFile,args=((tcpSock,filename,filesize),))
                sendFileThread.start()
                threads.append(sendFileThread)

        # make direct connection and send the distribution message
        # check if clientIp is it's own ip or not and is there already a connection or not
        logging.warning("recvFileThread joined")
        for thread in threads:
            thread.join()
        # recvFileThread.join()
        # sendFileThread.join()
        regexFile = str(url[len(url) - 1]).split('.')[0]
        filename = str(url[len(url) - 1])
        merge(regexFile,filename)


def Client():
    listenBroadcastThread = threading.Thread(
        target=listenBroadcast, args=("",))
    listenBroadcastThread.start()
    listenBroadcastThread.join()
    # while(listenBroadcastThread.is_alive()):
    #     pass
    # clientsIp = clientsIp+ list(distributionMsg.data['clientIpSegmentMap'].keys())
    # for clientIp in clientsIp:
    #   ipPortMap[clientIp] = distributionMsg.data['clientIpSegmentMap'][clientIp]['port']

    # clientsCount = len(clientsIp)
    # sock.listen(clientsCount-2) #removed its own count and master

    # acceptConnectionsThread=threading.Thread(target=acceptConnections,args=({'sock':sock,'clientsCount':clientsCount},))
    # acceptConnectionsThread.start()

    # for clientIp in clientsIp:
    #   if clientIp in ipSockMap:
    #       logging.warning("Aleardy connected")
    #   elif clientIp == OWNIP:
    #       logging.warning("Skipping since this is my ip: ",clientIp)
    #   else:
    #       sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #       logging.warning("making connection request with: ",clientIp)
    #       server_address = (clientIp, ipPortMap[clientIp])
    #       logging.warning('Connecting to %s port %s' % server_address)
    #       sock.connect(server_address)
    #       logging.warning("connected to client: ",clientIp)
    #       ipSockMap[clientIp] = sock

    # make one thread to accept the connections

    # recv distribution message from master
    # accept connection request from master and get the distributionMsg details
    # store the clients ip in clientsIp
    # for clientIp in clientsIp:
        #logging.warning("make connection")
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
    logging.warning("Master")
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
        # logging.warning("Program started")
        # #logic to trigger master and client
        # logging.warning("enter 1 for master, 0 for client")
        # x=int(input())
        # if(x==0):
        #   isMaster=False
        # else:
        #   isBusy=True  #if the system is a master, it will not involve in other download
        #   isMaster=True
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