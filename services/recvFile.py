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
    #     print(received)
        # received = received.decode()
    #     while(received == ''):
    #         received = tcpSock.recv(BUFFER_SIZE).decode()
        # logging.warning(f"Received: {type(received)} {received}")
        # filename, filesize = received.split(SEPARATOR)
        # filename = os.path.basename(filename)
        # filesize = int(filesize)
        # tcpSock.send("ACK".encode())
    # except Exception as e:
    #     logging.warning(f'Exception in {tcpSock}.\n\n Error Thrown: {e}\n')
    # file_read = 0
    length=0
    with open(filename, "wb") as f:
        while (True):
            bytes_read = tcpSock.recv(BUFFER_SIZE)
            length = length + len(bytes_read)
            print("recv: ",length)
            f.write(bytes_read)
            if length >= filesize: 
                # tcpSock.close()
                logging.warning("File Received. Break")
                break
                # exit()
            # file_read  = file_read + len(bytes_read)
            
            # bytes_read = tcpSock.recv(BUFFER_SIZE)
        logging.warning("File Received")
    # tcpSock.close()
    logging.warning(f"Ending recvFile for {tcpSock}")