import time
import threading



class Event_block():
    def __init__(self, Name=None, Fun=None):
        self.name=Name
        self.event=threading.Event()
        self.foo=Fun
        

    def setFun(self, f):
        self.foo=f

    def push(self):
        self.event.set()




"""class EVENT_MASTER(threading.Thread):                      
    def __init__(self):                       
        threading.Thread.__init__(self)                
        self.EVENT_LIST=[]
        self.n=0

    def FSTART(self):
        return 0
        
    def run(self):
        while(1):
            if(VRangletest.START.isSet()):
                self.EVENT_LIST.append(self.FSTART)
                VRangletest.START.clear()
                self.n=self.n+1
            if (self.n>0):
                self.EVENT_LIST.pop(0)()
                self.n=self.n-1
            time.sleep(1)
    

    def connect(self, strc, foo):
        if(strc=="START"):
            self.FSTART=foo

            
"""


    

    

class EVENT_MASTER(threading.Thread):                      
    def __init__(self):                       
        threading.Thread.__init__(self)
        self.EVENT_LIST=[]
        self.EVENT_STEK=[]
        self.EXIT_EM=False
        
        self.threads=[]

    

    def run(self):
        while not self.EXIT_EM:
            for element in self.EVENT_LIST:
                if(element.event.isSet()):
                    self.EVENT_STEK.append(element)
                    element.event.clear()

                if(len(self.EVENT_STEK)>0):
                    self.threads.append(threading.Thread(target=self.EVENT_STEK.pop(0).foo))
                    self.threads.pop(0).start()

    def quit(self):
        EXIT_EM=True

    def append(self, event):
        self.EVENT_LIST.append(event)










def functOK():
    i=0
    while(i<10):
        print("OK\n")
        i=i+1

def functOK1():
    i=0
    while(i<10):
        print("OK1\n")
        i=i+1

def functOK2():
    i=0
    while(i<10):
        print("OK2\n")
        i=i+1







EV=EVENT_MASTER()
EV.start()

ev=Event_block()
ev1=Event_block()
ev2=Event_block()

ev.setFun(functOK)
ev1.setFun(functOK1)
ev2.setFun(functOK2)


EV.append(ev)
EV.append(ev1)
EV.append(ev2)





ev.push()

ev1.push()

ev2.push()



