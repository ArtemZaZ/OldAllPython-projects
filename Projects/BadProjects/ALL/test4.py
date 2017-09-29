import event_master

def functOK():
    i=0
    while(i<10):
        print("OK\n")
        i=i+1

def functOK1():
    i=0
    while(i<10):
        print("OK1\n")
        i=i+1

def summ(a,b):
    c=a+b;
    i=0
    while(i<10):
        print(c+i)
        i=i+1    

a1=4
b1=6
def functOK2():
    global a1
    global b1
    summ(a1, b1)    
    

EV=event_master.EVENT_MASTER()
EV.start()

ev=event_master.Event_block()
ev1=event_master.Event_block()
ev2=event_master.Event_block()

ev.setFun(functOK)
ev1.setFun(functOK1)
ev2.setFun(functOK2)

EV.append(ev)
EV.append(ev1)
EV.append(ev2)

ev.push()
ev1.push()
ev2.push()
