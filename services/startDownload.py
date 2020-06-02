import os
import logging
def startDownload(segment, fileLink):
    url = fileLink.split('/')
    fileName = str(url[len(url) - 1]).split('.')[0] + str(segment) + '.spld'
    os.system('curl -s -L  -o ' + fileName +' --range ' + segment + ' ' +fileLink)
    # logging.warning(f"Downloading : {os.path.getsize(fileName)}")

    # os.system('curl -F 'file=fileName' http://localhost/')
