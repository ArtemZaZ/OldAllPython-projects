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
        temp_axis=self.Joy.get_axis()
        if(temp_axis!=None):
            x_temp=-temp_axis.get('x')
            y_temp=-temp_axis.get('y')
            trottle_temp=temp_axis.get('trottle')        
        
            x=int(100*x_temp)
            y=int(100*y_temp)
            trottle=((trottle_temp+1.0)/2)

            x = ((x+2)//20)*20 
            y = ((y+2)//20)*20                              
            
            
            if x<=0:
                if y<=0:
                    speedR = y + x  
                    speedL = y - x
                if y>0:
                    speedR = y + x
                    speedL = y - x
                
            if x>0:
                if y<=0:
                    speedR = y + x
                    speedL = y - x
                if y>0:
                    speedR = y + x
                    speedL = y - x

            speedR=int(trottle*speedR/2)
            speedL=int(trottle*speedL/2)
            
            self.R = -speedR
            self.L = -speedL
        else:
            self.R = 0
            self.L = 0
            
        
    def run(self):
        while(not self.EXIT):
            tempR=self.R
            tempL=self.L
            self.convert_speed()
            if((tempR!=self.R) or (tempL!=self.L)):
                self.M.MotorA(self.L)
                self.M.MotorB(self.R)
            #print("self.L", self.L)
            #print("self.R", self.R)
            time.sleep(0.5)
                
            
        
    def Exit(self):
        self.EXIT=True
        self.Joy.Exit()
        












    
    

