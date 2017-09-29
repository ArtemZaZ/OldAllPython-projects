import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import time
import VRproject
import RTCvrangle
from Gromozeka import *
import Izbitochnii
from Work_with_Joystik import *
import threading
i=0

D = Robot()
D.add_Stepper_Controller(0)
D.add_Motor_Controller(0)
S = self.D.Steppers_Contr_List[0]
M = self.D.Motors_Contr_List[0]

def read_handler(ang):
    global i
    video.set_angle_list(ang)
    sp=Izbitochnii.CALCULATOR_LENIVOGO_ARTEMA(ang)
    if(i<2):
        if(video.is_over()):
            S.Set_Steppers_Pos( Izbitochnii.middle1, Izbitochnii.middle2, Izbitochnii.middle3)
        else:
            S.Set_Steppers_Pos(sp[0],sp[1],sp[2])
        i=0
    i=i+1
        

def start_handler():
    print("\nI started\n")
    video.go_game()

def stop_handler():
    video.set_angle_list([0, 0, 0])
    S.Set_Steppers_Pos( Izbitochnii.middle1, Izbitochnii.middle2, Izbitochnii.middle3)
    video.clear_game_over()

class AR_Window():
    
    def __init__(self):
        global D, S, M
        self.IP = "192.168.42.162"
        self.Path = "/dev/ttyUSB0"
        self.time_game = 60

        
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_title("Jonny Interface")
        self.window.set_default_size(300, -1)
        self.window.connect("delete_event", self.delete_event)
        self.vbox = Gtk.VBox()
        self.window.add(self.vbox)

        self.ip_label = Gtk.Label()
        self.ip_label.set_text("IP Робота:")
        self.vbox.pack_start(self.ip_label, 0, True, 0)        

        
        self.ip_entry = Gtk.Entry()
        self.ip_entry.set_max_length(17)
        self.ip_entry.set_text(self.IP)
        self.vbox.pack_start(self.ip_entry, True, True, 0)        

        self.glass_label = Gtk.Label()
        self.glass_label.set_text("Путь к очкам:")
        self.vbox.pack_start(self.glass_label, 0, True, 0) 

        self.glass_port = Gtk.Entry()
        self.glass_port.set_max_length(17)
        self.glass_port.set_text(self.Path)
        self.vbox.pack_start(self.glass_port, True, True, 0)

        self.OK_button = Gtk.Button("Применить настройки")
        self.OK_button.connect("clicked", self.OK)
        self.vbox.add(self.OK_button)

        self.connect_button = Gtk.Button("Connect")
        self.connect_button.connect("clicked", self.Connect)
        self.vbox.add(self.connect_button)

        self.disconnect_button = Gtk.Button("Disconnect")
        self.disconnect_button.connect("clicked", self.Disconnect)
        self.vbox.add(self.disconnect_button)

        self.init_button = Gtk.Button("Init")
        self.init_button.connect("clicked", self.Init)
        self.vbox.add(self.init_button)

        self.start_button = Gtk.Button("Start")
        self.start_button.connect("clicked", self.Start)
        self.vbox.add(self.start_button)
        
        self.video=VRproject.AR()

        self.video.set_player_time_game(self.time_game)

        self.D = Robot()
        self.D.add_Stepper_Controller(0)
        self.D.add_Motor_Controller(0)
        self.S = self.D.Steppers_Contr_List[0]
        self.M = self.D.Motors_Contr_List[0]
                

        self.window.show_all()



    def delete_event(self, widget, event, data=None):
        print(222)
        Gtk.main_quit()
        
        self.VR.Exit()
        self.video.stop()
        self.M.Initialize(NOTREADY)
        self.DDDDD.Exit=True
        self.D.Disconnect()        

    def OK(self, w):
        self.IP = self.ip_entry.get_text()
        self.Path = self.glass_port.get_text()

    def Connect(self, w):
        self.connect_funct(self.IP, self.Path)

    def Disconnect(self, w):
        self.disconnect_funct()

    def Init(self, w):
        self.init_funct()

    def Start(self, w):
        self.start_funct()

    def set_funct(self, param, funct):
        if(param=="CONNECT"):
            self.connect_funct=funct
        if(param=="DISCONNECT"):
            self.disconnect_funct=funct
        if(param=="INIT"):
            self.init_funct=funct
        if(param=="START"):
            self.start_funct=funct
        if(param=="EXIT"):
            self.exit_funct=funct


def th():
    Gtk.main()

t = threading.Thread(target=th)



