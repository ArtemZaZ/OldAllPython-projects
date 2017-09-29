import VRangletest
import time
import threading

#class EVENT_STEK():    
#    self.EVENT_LIST=[]
def handler():
    angle=VR_TH.get_angle()
    print(angle)
    print("\nITS WORK!!!\n")

class EVENT_MASTER(threading.Thread):                      # потоковый класс
    def __init__(self):                       # конструктор
        threading.Thread.__init__(self)                 # функция инициализирующая поток
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
            
        

VR_TH=VRangletest.VR_thread("/dev/ttyUSB0")
VR_TH.start()


EV=EVENT_MASTER()
EV.connect("START", handler)
EV.start()
    
time.sleep(0.05)
    
#VR_TH.Exit()


