import time
import RTCjoystic

J = RTCjoystic.Joystick()
J.connect("/dev/input/js0")
J.info()
time.sleep(2)
J.start()

def hand():
    print("IT'S ALIVE")

J.connectButton('trigger', hand)

while(True):
    print(J.Axis.get('z'))
    #print(J.Buttons.get('trigger'))
    time.sleep(0.1)

J.exit()
