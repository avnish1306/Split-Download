import os
import logging
import json
from time import sleep

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
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
        data = rawData.encode('ASCII')
        logging.warning(f'Data :{data}')
        return data


def sendFile(args):
    tcpSock = args[1]
    filename = args[2]
    logging.warning(f"\nSending: {filename} to {tcpSock}\n")
    filesize = os.path.getsize(filename)
    fileObject = {}
    fileObject['filename'] = filename
    fileObject['filesize'] = filesize
    # logging.warning(f'filename:{filename}  filesize:{filesize}')
    msg = MSG(fileObject)
    tcpSock.sendall(msg.dumpJson())
    sleep(1)
    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                logging.warning("File Sent")
                # tcpSock.close()
                exit(0)
            tcpSock.sendall(bytes_read) 
    # tcpSock.close()