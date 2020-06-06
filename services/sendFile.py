import os
import logging
from time import sleep
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
FORMAT = '[%(asctime)-15s] {%(filename)s} {%(funcName)s} {%(lineno)d} %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)
def sendFile(args):
    logging.warning("Starting sendFile")
    tcpSock = args[0]
    filename = args[1]
    filesize = args[2]
    logging.warning(f"\nSending: {filename} to {tcpSock}\n")
    logging.warning(f"Filesize : {filesize}")
    # tcpSock.send(f"{filename}{SEPARATOR}{filesize}".encode())
    
    # tcpSock.send(None)
    # ack = tcpSock.recv(BUFFER_SIZE).decode()
    # print(ack)
    # with open(filename, "rb") as f:
    
    
    # print("Send: ",len(bytes_read))
    # length = 0
    while(True):
        try:
            # filesize = os.path.getsize(filename)
            # 
            f = open(filename, "rb")
            break
        except Exception as e:
            pass
    l=0
    byte_read=f.read(BUFFER_SIZE)
    if byte_read:
        l = len(byte_read)
    while(True):
        while(not byte_read and l<filesize):
            byte_read = f.read(BUFFER_SIZE)
            
        if(byte_read):
            tcpSock.sendall(byte_read)
            l=l+len(byte_read)
            logging.warning(f"{tcpSock.getsockname()[0]} : {tcpSock.getpeername()[0]}  Length of file read: {len(byte_read)} , Total Length of file read: {l}")
            byte_read = None
            byte_read = f.read(BUFFER_SIZE)
            if(byte_read):
                logging.warning(f"{tcpSock.getsockname()[0]} : {tcpSock.getpeername()[0]} Length of file read after: {len(byte_read)}")
            else:
                logging.warning(f"No Byte read.")
        else:
            break

    # bytes_read = f.read(BUFFER_SIZE)
    # # tcpSock.sendall(bytes_read)
    # while bytes_read:
    #     if not bytes_read:
    #         # file transmitting is done
    #         logging.warning("File Sent")
    #         break
    #     # length = length + len(bytes_read)
    #     # print("Send: ",length)
    #     tcpSock.sendall(bytes_read)
    #     bytes_read = f.read(BUFFER_SIZE)
    # # tcpSock.close()
    # tcpSock.sendall(b'abcd')
    logging.warning(f"Ending sendFile for {tcpSock}")
    f.close()