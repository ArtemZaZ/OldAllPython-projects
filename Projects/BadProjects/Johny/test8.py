import time
import VRproject
import RTCvrangle
from Gromozeka import *
import Izbitochnii
import Jonny_Joy
i=0
IP = '192.168.42.162'
PATH_TO_GLASS = "/dev/ttyUSB0"
GAME_TIME = 50

video=VRproject.AR(IP)
video.set_player_time_game(GAME_TIME)

D = Robot()
D.add_Stepper_Controller(0)
D.add_Motor_Controller(0)
S = D.Steppers_Contr_List[0]
M = D.Motors_Contr_List[0]

D.Connect(IP,13133)
D.Send_Online()
D.Listen()

    
M.Initialize(ISREADY)
time.sleep(0.2)
S.Initialize(ISREADY)
S.Calibrate()

Joy=Jonny_Joy.Jonny_Joystic(M)
Joy.start()
time.sleep(4)



def read_handler(ang):
    global Joy
    video.set_angle_list(ang)
    video.set_motor_speed(Joy.R, Joy.L)
    sp=Izbitochnii.CALCULATOR_LENIVOGO_ARTEMA(ang)
    if(video.is_over()):
        S.Set_Steppers_Pos( Izbitochnii.middle1, Izbitochnii.middle2, Izbitochnii.middle3)
    else:
        S.Set_Steppers_Pos(sp[0],sp[1],sp[2])
        

def start_handler():
    print("\nI started\n")
    video.go_game()

def stop_handler():
    video.set_angle_list([0, 0, 0])
    S.Set_Steppers_Pos( Izbitochnii.middle1, Izbitochnii.middle2, Izbitochnii.middle3)
    video.clear_game_over()

VR=RTCvrangle.VR_thread(PATH_TO_GLASS)
VR.start()
VR.connect("START", start_handler)                                                                  
VR.connect("STOP", stop_handler)                                                                   
VR.connect("READ", read_handler)



time.sleep(4)
video.start()

time.sleep(300)

VR.Exit()
video.stop()
M.Initialize(NOTREADY)
Joy.Exit()
D.Disconnect()










