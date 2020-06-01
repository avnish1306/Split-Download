import os
import logging
import json

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
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

def recvFile(args):
    tcpSock = args[0]
    filename = args[1]
    logging.warning(f"Before Receiving at: {tcpSock}")
    try:
        received, address = tcpSock.recvfrom(BUFFER_SIZE)
        logging.warning(f'Received :{received}')
        msgObject = MSG({})
        msgObject.loadJson(received)
        filename = msgObject.data['filename']
        filesize = msgObject.data['filesize']
        # while(received == ''):
        #     received = tcpSock.recv(BUFFER_SIZE).decode()
        logging.warning(f"Received: {type(received)} {received} ")
        # filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)
    except Exception as e:
        logging.warning(f'Exception in {tcpSock}.\n\n Error Thrown: {e}\n')
    file_read = 0
    with open(filename, "wb") as f:
        while file_read < filesize:
            bytes_read = tcpSock.recv(BUFFER_SIZE)
            if not bytes_read: 
                # tcpSock.close()
                logging.warning("File Received")
                exit()
            file_read  = file_read + len(bytes_read)
            f.write(bytes_read)
        logging.warning("File Received")
    # tcpSock.close()