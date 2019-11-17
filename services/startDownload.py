import os

def startDownload(segment, fileLink):
    url = fileLink.split('/')
    fileName = str(url[len(url) - 1]) + str(segment)
    os.system('curl -L  -o ' + fileName +' --range ' + segment + ' ' +fileLink)
