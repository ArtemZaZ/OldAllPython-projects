import RTCjoystic
import time
import threading
 

class Jonny_Joystic(threading.Thread):
    def __init__(self, M):
        threading.Thread.__init__(self)
        self.Joy=RTCjoystic.Joystick_master()
        self.Joy.start()
        self.EXIT=False
        self.L=0
        self.R=0
        self.M=M
        time.sleep(3)

    def convert_speed(self):
        x=int((100*((self.Joy.get_axis()).get('x'))))
        y=int((100*((self.Joy.get_axis()).get('y'))))

        x = ((x+2)//20)*20 
        y = -((y+2)//20)*20

        x = int(x//2)                     
    
        
        if x<=0:
            if y<=0:
                speedR = y + x
                speedL = y
            if y>0:
                speedR = y - x
                speedL = y
            
        if x>0:
            if y<=0:
                speedR = y
                speedL = y - x
            if y>0:
                speedR = y
                speedL = y + x 
        
        self.R = speedR
        self.L = speedL
        
        
    def run(self):
        while(not self.EXIT):
            self.convert_speed()
            self.M.MotorA(self.L)
            self.M.MotorB(self.R)
            time.sleep(0.5)
                
            
        
    def Exit(self):
        self.EXIT=True
        self.Joy.Exit()
        













    
    

