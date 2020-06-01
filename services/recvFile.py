import os
import logging
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
FORMAT = '[%(asctime)-15s] {%(filename)s} {%(funcName)s} {%(lineno)d} %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)
def recvFile(args):
    logging.warning("Starting recvFile")
    logging.warning(f"args : {args}")
    tcpSock = args[0]
    filename = args[1]
    filesize = args[2]
    # filename, filesize = getFileDetails()
    logging.warning(f"Before Receiving at: {tcpSock}")
    logging.warning(f"filename: {filename},  filesize: {filesize}")
    # try:
    #     received = tcpSock.recv(BUFFER_SIZE).decode()
    #     while(received == ''):
    #         received = tcpSock.recv(BUFFER_SIZE).decode()
    #     logging.warning(f"Received: {type(received)} {received}")
    #     filename, filesize = received.split(SEPARATOR)
    #     filename = os.path.basename(filename)
    #     filesize = int(filesize)
    # except Exception as e:
    #     logging.warning(f'Exception in {tcpSock}.\n\n Error Thrown: {e}\n')
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
    logging.warning("Ending recvFile")