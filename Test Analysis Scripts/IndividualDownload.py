import schedule
import os
import logging
import time

def download(args):
    fileLink = 'https://download.ccleaner.com/ccsetup567.exe'
    fileName = fileLink.split('/')
    fileName = fileName[len(fileName)-1]
    startTime = time.time()
    os.system('curl -L  -o ' + '"' + fileName + '"' + ' ' + '"' + fileLink +'"')
    logging.warning(f"Time to finish download : {time.time() - startTime}")

schedule.every().day.at("22:15").do(download, "Download Started")

while True:
    schedule.run_pending()