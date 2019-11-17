import os

def startDownload(segment, fileLink):
    url = fileLink.split('/')
    fileName = url[len(url) - 1]
    os.system('curl -L  -o ' + fileName +' --range ' + segment + ' ' +fileLink)
