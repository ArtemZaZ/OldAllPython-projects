import sys
stop = 1
StickValue=0
def readStick(pipe):
    global stop
    global StickValue
    action = []
    while stop == 1:
        for character in pipe.read(1):
            action += [int(character)]
            if len(action) == 8:
                StickValue = action
                action = []
                stop = 2
                    ##when joystick is stationary code hangs here.
                return  StickValue


pipe = open('/dev/input/js0', 'rb') #open joystick 
action = []
while True:
    StickValue = readStick(pipe)
    print (StickValue)
