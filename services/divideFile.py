import requests
import re

def divideFile(url, clientList):
    #clientList = ['192.168.1.1', '192.168.1.2', '192.168.1.3','192.162.2.3']
    #url = 'http://releases.ubuntu.com/19.10/ubuntu-19.10-desktop-amd64.iso'
    print('Please wait while segments are being calculated')
    head = requests.head(url, allow_redirects=True).headers
    size = head.get('Content-Length')
    start = 0
    if int(size) % len(clientList) == 0:
        individualSize = int(size) / len(clientList)
    else:
        individualSize = int(size) // len(clientList)
    end = individualSize
    clientFileSection = {}
    for clientIp in clientList:
        clientFileSection[clientIp] = str(int(start)) + '-' + str(int(end))
        start = end + 1
        end += individualSize
    clientFileSection[clientList[len(clientList)-1]] = str(int(end - 2*individualSize + 1)) + '-' + str(int(size))
    print('File Size = {}'.format(size))
    print (clientFileSection)
    return clientFileSection
