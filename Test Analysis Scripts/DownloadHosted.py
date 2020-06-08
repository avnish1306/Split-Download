import os
import logging
import time
import requests

fileLink = 'https://download.ccleaner.com/ccsetup567.exe'
fileName = fileLink.split('/')
fileName = str(fileName[len(fileName)-1])

while(True):
    try:
        head = requests.head('http://192.168.43.92:8000/' + fileName, allow_redirects=True).headers
        if head:
            startTime = time.time()
            os.system('curl -L  -o ' + '"' + fileName + '"' + ' ' + 'http://192.168.43.92:8000/' + fileName)
            logging.warning(f"Time to finish download: {time.time() - startTime + 30}")
            break
    except Exception as e:
        pass
