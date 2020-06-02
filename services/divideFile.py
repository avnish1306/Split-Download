import requests
import re
import logging
FORMAT = '[%(asctime)-15s] {%(filename)s} {%(funcName)s} {%(lineno)d} %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)
def divideFile(url, clientList):
    #clientList = ['192.168.1.1', '192.168.1.2', '192.168.1.3','192.162.2.3']
    #url = 'http://releases.ubuntu.com/19.10/ubuntu-19.10-desktop-amd64.iso'
    logging.warning('Please wait while segments are being calculated')
    head = requests.head(url, allow_redirects=True).headers
    size = int(head.get('Content-Length'))-1
    start = 0
    if size % len(clientList) == 0:
        individualSize = size / len(clientList)
    else:
        individualSize = size // len(clientList)
    end = individualSize
    clientFileSection = {}
    for clientIp in clientList:
        clientFileSection[clientIp] = str(int(start)) + '-' + str(int(end))
        start = end + 1
        end += individualSize
    clientFileSection[clientList[len(clientList)-1]] = str(int(end - 2*individualSize + 1)) + '-' + str(size)
    logging.warning('File Size = {}'.format(size))
    logging.warning (clientFileSection)
    return clientFileSection
