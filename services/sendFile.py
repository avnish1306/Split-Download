import os
import logging
from time import sleep
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
FORMAT = '[%(asctime)-15s] {%(filename)s} {%(funcName)s} {%(lineno)d} %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)
def sendFile(args):
    logging.warning("Starting sendFile")
    tcpSock = args[1]
    filename = args[2]
    logging.warning(f"\nSending: {filename} to {tcpSock}\n")
    filesize = os.path.getsize(filename)
    # tcpSock.send(f"{filename}{SEPARATOR}{filesize}".encode())
    logging.warning(f"Filesize : {filesize}")
    # tcpSock.send(None)
    # ack = tcpSock.recv(BUFFER_SIZE).decode()
    # print(ack)
    # with open(filename, "rb") as f:
    f = open(filename, "rb")
    bytes_read = f.read()
    print("Send: ",len(bytes_read))
    # length = 0
    tcpSock.sendall(bytes_read)
    # while bytes_read:
    #     # if not bytes_read:
    #     #     # file transmitting is done
    #     #     logging.warning("File Sent")
    #     #     # tcpSock.close()
    #     #     exit(0)
        
    #     length = length + len(bytes_read)
    #     print("Send: ",length)
    #     tcpSock.sendall(bytes_read)
    #     bytes_read = f.read(BUFFER_SIZE)
    # # tcpSock.close()
    # tcpSock.sendall(b'abcd')
    logging.warning(f"Ending sendFile")
    f.close()