import time
import VRproject
import RTCvrangle
from Gromozeka import *
import Izbitochnii
import RTCjoystic
import Jonny_Joy
i=0
SPEED=15.0

class joy_stic(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.Joy=RTCjoystic.Joystick_master()
        self.Joy.start()
        self.EXIT=False
        self.x=0.0
        self.y=0.0
        self.speed_x=0.0
        self.speed_y=0.0
        time.sleep(3)

    def convert_speed(self):
        global SPEED
        temp_axis=self.Joy.get_axis()
        if(temp_axis!=None):
            self.speed_x=temp_axis.get('x')
            self.speed_y=temp_axis.get('y')
            self.x=self.x+self.speed_x*SPEED*0.1
            self.y=self.y+self.speed_y*SPEED*0.1
            #self.trottle_temp=temp_axis.get('trottle')         
        else:
            pass
            
        
    def run(self):
        while(not self.EXIT):
            self.convert_speed()
            time.sleep(0.1)
                        
    def Exit(self):
        self.EXIT=True
        self.Joy.Exit()
    

video=VRproject_nine.AR()
video.set_player_time_game(70)


Joy=joy_stic()
Joy.start()
#time.sleep(4)



def read_handler(ang):
    global i
    global Joy
    video.set_angle_list(ang)
    video.set_coord(Joy.x, 0.0, Joy.y)
        

def start_handler():
    print("\nI started\n")
    video.go_game()

def stop_handler():
    video.set_angle_list([0, 0, 0])
    video.clear_game_over()

#VR=RTCvrangle.VR_thread("/dev/ttyUSB0")
#VR.start()
#VR.connect("START", start_handler)                                                                  
#VR.connect("STOP", stop_handler)                                                                   
#VR.connect("READ", read_handler)



#time.sleep(4)
video.start()

time.sleep(300)
Joy.Exit()
#VR.Exit()
video.stop()










