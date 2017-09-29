### Замки стоит поменять на очередь, чтобы не возникало тупиков 
from Gromozeka import *
import time

D = Robot()
D.add_Stepper_Controller(0)
S = D.Steppers_Contr_List[0]
D.Connect("192.168.42.162",13133)
D.Send_Online()
D.Listen()
time.sleep(0.2)
S.Initialize(ISREADY)
S.Calibrate()
#S.Set_Steppers_Pos(0,0,0)
time.sleep(3)
D.Disconnect()
print("AAAAAAAAPCHHI")
