import os

def merge(regexFile, filename):
    os.system(f'copy /b {regexFile}*.spld {filename}')
    print("Files merged")
    # if(os.system(f'copy /b {regexFile}* {filename}')):
    os.system(f'del {regexFile}*.spld')
