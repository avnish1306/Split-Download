import os
import logging
import time

fileLink = 'https://download.ccleaner.com/ccsetup567.exe'
fileName = fileLink.split('/')
fileName = fileName[len(fileName)-1]
startTime = time.time()
os.system('curl -L  -o ' + '"' + fileName + '"' + ' ' + '"' + fileLink +'"')
logging.warning(f"Time to finish download and host: {time.time() - startTime + 30}")
os.system('py -m http.server')
