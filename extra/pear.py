import threading
import time
a=[]
def getIp(arg):
    while(True):
        time.sleep(3)
        a.append("1")

def getPing(arg):
    while(True):
        time.sleep(1)
        a.append("2")
    
if __name__ == "__main__":
    t=threading.Thread(target=getIp,args=("1b",))
    t.start()
    t1=threading.Thread(target=getPing,args=("1b",))
    t1.start()
    while(True):
        time.sleep(2)
        print(a)
    print("main end")