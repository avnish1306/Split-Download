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
import ds4
import ds5
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
ui4 = None
ui5 = None
Form = "abc"
Form2 = None
Form4 = None
Form5 = None
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
OWNIP = getOwnIp()   
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
    filenameWithExt = args[2]
    startDownload(segment, fileLink, filenameWithExt)
    logging.warning("Exiting initiateDownload")

def listenBroadcast(arg):  # client
    global clientIpList
    global clientDownloadStarted
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
        clientDownloadStarted()
        distributionMsg.view()
        filenameWithExt = distributionMsg.data['filenameWithExt']

        clientIpSegmentMap = distributionMsg.data['clientIpSegmentMap']
        segment = clientIpSegmentMap[OWNIP]
        logging.warning (segment)
        fileLink = distributionMsg.data['fileLink']
        ipSockMap[address[0]] = tcpSock
        ipSockMap[OWNIP] = None
        clientIpList = distributionMsg.data['clientIpSegmentMap'].keys()
        listenClientTcpReqThread = threading.Thread(target=listenClientTcpReq, args = ("",))
        listenClientTcpReqThread.start()

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
                filename, filesize = getFileDetails(OWNIP, distributionMsg, tcpSock)
                recvFileThread = threading.Thread(target=recvFile,args=((tcpSock,filename,filesize),))
                recvFileThread.start()
                threads.append(recvFileThread)

        for x in ipSockMap:
            logging.warning(x)

        initiateDownloadThread = threading.Thread(
            target=initiateDownload, args=((segment, fileLink, filenameWithExt),))  # Download Started
        initiateDownloadThread.start()
        threads.append(initiateDownloadThread)
        
        
        filename = filenameWithExt.split('.')[0] + str(segment) +'.spld'

        for ipSock in ipSockMap:
            client = ipSock
            if client != OWNIP:
                logging.warning(f'{ipSock}, {ipSockMap[ipSock]}')
                tcpSock = ipSockMap[client]
                fname, filesize = getFileDetails(OWNIP, distributionMsg, tcpSock, False)
                sendFileThread = threading.Thread(target=sendFile,args=((tcpSock,filename,filesize),))
                sendFileThread.start()
                threads.append(sendFileThread)

        for thread in threads:
            thread.join()
        logging.warning("Out of all Send and Recv Threads.")
 
        
        regexFile = filenameWithExt.split('.')[0]
        merge(distributionMsg)
        downloadComplete()
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
            # sock.sendto(res.dumpJson(), (broadcastInterface, broadcastPort))
            tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcpServerAddress = (OWNIP, tcpPort)
            tcpSock.connect(tcpServerAddress)
            break
        choice = -1
    # announce the welcome message over network
    # display received ips
    # check if user want to announce again or not and continue the loop if refresh happen
    # conditional : global isAnnouncementOn = False
    sock.close()
    logging.warning("announcing broadcast ended")

def sendDistributionMsg(args):
    global segmentsFetched
    global distributionMsg
    connection = args[0]
    connection.sendall(distributionMsg.dumpJson())
    logging.warning("Exiting sendDistributionMsg")

def listenTcp(arg):
    tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverAddress = (OWNIP, tcpPort)
    tcpSock.bind(serverAddress)
    tcpSock.listen(10)
    while(True):    
        connection, address = tcpSock.accept()
        if connection.getsockname()[0] == connection.getpeername()[0]:
            break
        tcpConnectionList.append((connection, address))
        clientsIp.append(address[0])
        ipSockMap[address[0]] = connection
        # refreshList()
        logging.warning(f'Connected to : {address[0]} : {address[1]}')
    logging.warning("Exiting listenTcp thread.")

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
    announceBroadcastThread.join()
    # while(announceBroadcastThread.is_alive()):
    #     pass

    # if got all the clients, Time to distribute the file and send it to others
    # if not announceBroadcastThread.is_alive():
    global segmentsFetched
    global distributionMsg
    clientsIp.append(OWNIP)
    clientIpSegmentMap, filenameWithExt = divideFile(fileLink, clientsIp)
    distributionMsg = MSG(
        {"fileLink": fileLink, "clientIpSegmentMap": clientIpSegmentMap, "filenameWithExt" : filenameWithExt}, "Distribution message", isMaster)
    logging.warning("This is the distribution msg ")
    distributionMsg.view()
    for element in tcpConnectionList:
        sendDistributionMsgThread = threading.Thread(target = sendDistributionMsg, args = ((element[0],element[1]),))
        sendDistributionMsgThread.start()
 
            
    segmentsFetched = True
    segment = clientIpSegmentMap[OWNIP]

    threads = []
    for ipSock in ipSockMap:
        client = ipSock
        if client != OWNIP:
            logging.warning(f'{ipSock}, {ipSockMap[ipSock]}')
            tcpSock = ipSockMap[client]
            filename, filesize = getFileDetails(OWNIP, distributionMsg, tcpSock)
            recvFileThread = threading.Thread(target=recvFile,args=((tcpSock,filename,filesize),))
            recvFileThread.start()
            threads.append(recvFileThread)

    initiateDownloadThread = threading.Thread(target=initiateDownload, args=(
        (segment, fileLink, filenameWithExt),))  # Download Started in Master
    initiateDownloadThread.start()
    threads.append(initiateDownloadThread)

    segment = clientIpSegmentMap[OWNIP]
    filename = filenameWithExt.split('.')[0] + str(segment) + '.spld'

    for ipSock in ipSockMap:
        client = ipSock
        if client != OWNIP:
            tcpSock = ipSockMap[client]
            fname, filesize = getFileDetails(OWNIP, distributionMsg, tcpSock, flag = False)
            sendFileThread = threading.Thread(target=sendFile,args=((tcpSock,filename,filesize),))
            sendFileThread.start()
            threads.append(sendFileThread)

    logging.warning("recvFileThread joined")
    for thread in threads:
        thread.join()

    regexFile = filenameWithExt.split('.')[0]
    merge(distributionMsg)
    downloadComplete()
    logging.warning("Exiting Master")

def Client():
    listenBroadcastThread = threading.Thread(
        target=listenBroadcast, args=("",))
    listenBroadcastThread.start()
    Form.close()
    ui5.changeText("Waiting",'red')
    Form5.show()

    # listenBroadcastThread.join()
def clientDownloadStarted():
    ui5.changeText("Downloading")

def startMasterScreen():
    global app
    global Form2
    global Form

def checkClientList(args):
    global clientsIp
    global choice
    logging.warning("CheckClientList called")
    length = 0
    while(choice != 0):
        # logging.warning(f'{len(clientsIp)}')
        sleep(1)
        if(length != len(clientsIp)):
            length = len(clientsIp)
            logging.warning("Refreshing List")
            refreshList()
    logging.warning("Exiting chechkClientList")
        

def startMasterUtil():
    logging.warning("Master")
    masterThread = threading.Thread(target=Master, args=('',))
    masterThread.start()
    checkClientListThread = threading.Thread(target=checkClientList, args=('',))
    checkClientListThread.start()
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
    global fileLink
    fileLink = str(ui4.downloadLink.toPlainText())
    fileLink = fileLink.strip()
    choice = 0
    Form4.close()
    Form5.show()

def urlPicker():
    Form2.close()
    Form4.show()

def downloadComplete():
    ui5.changeText("Download Complete",'green')
    ui5.label_2.setVisible(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui1 = ds1.Ui_Form()
    ui1.setupUi(Form)
    Form2 = QtWidgets.QWidget()
    ui2 = ds2.Ui_Form()
    ui2.setupUi(Form2)

    Form4 = QtWidgets.QWidget()
    ui4 = ds4.Ui_Form()
    ui4.setupUi(Form4)

    Form5 = QtWidgets.QWidget()
    ui5 = ds5.Ui_Form()
    ui5.setupUi(Form5)

    ui1.Master.clicked.connect(startMasterUtil)
    ui1.Client.clicked.connect(Client)
    ui2.Refresh.clicked.connect(reannounce)
    ui2.Next.clicked.connect(urlPicker)

    ui4.Download.clicked.connect(endAnnounceMent)
    Form.show()
    sys.exit(app.exec_())
    # while(True):
    #     pass