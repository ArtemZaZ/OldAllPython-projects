import time
import RTCjoystic

J = RTCjoystic.Joystick()
J.connect("/dev/input/js0")
J.info()
time.sleep(2)
J.start()

def hand():
    print("IT'S ALIVE!!!")

def hand2():
    print("REALY!!!")

J.connectButton('unknown(0x12d)', hand)
J.connectButton('thumb', hand2)

while(True):
    print(J.Axis.get('x'))
    #print(J.Buttons.get('trigger'))
    time.sleep(0.1)
J.exit()
