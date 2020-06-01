import os
import logging
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
    # tcpSock.sendall(f"{filename}{SEPARATOR}{filesize}".encode())
    logging.warning(f"Filesize : {filesize}")
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
    logging.warning("Ending sendFile")