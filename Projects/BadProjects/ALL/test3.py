import VRangle
import time

angle=[]

def handler(ang):
    global angle
    angle=ang
    print(angle)

def handler1():
    print("\nI stoped\n")

def handler2():
    print("\nI started\n")

VR_TH=VRangle.VR_thread("/dev/ttyUSB0")
VR_TH.start()

VR_TH.connect("START", handler2)
VR_TH.connect("STOP", handler1)
VR_TH.connect("READ", handler)

time.sleep(20)
VR_TH.Exit()
