#!/usr/bin/env python3
import time
import VRproject_without__audio
import RTCvrangle
import gi
from Gromozeka import *
import Izbitochnii
import Jonny_Joy
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
i=0

class Jonny_WINDOW:
    def __init__(self):
        self.IP = "192.168.42.162"
        self.PATH_TO_GLASS = "/dev/ttyUSB0"
        self.GAME_TIME = 50
        
        self.video=None
        self.D=None
        self.S=None
        self.M=None
        self.Joy=None
        self.VR=None
        
        
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_title("Jonny window")
        self.window.set_default_size(300, -1)
        self.window.connect("delete_event", self.delete_event)
        self.vbox = Gtk.VBox()
        self.window.add(self.vbox)

        self.label = Gtk.Label()
        self.label.set_text("Путь к очкам:")
        self.label.set_line_wrap(True)
        self.vbox.pack_start(self.label, 0, True, 0)        

        self.path_COM0 = Gtk.Entry()
        self.path_COM0.set_text("/dev/ttyUSB0")
        self.vbox.pack_start(self.path_COM0, True, True, 0)

        self.label1 = Gtk.Label()
        self.label1.set_text("IP робота:")
        self.label1.set_line_wrap(True)
        self.vbox.pack_start(self.label1, 0, True, 0)

        self.IP_text = Gtk.Entry()
        self.IP_text.set_text("192.168.42.162")
        self.vbox.pack_start(self.IP_text, True, True, 0)

        self.label2 = Gtk.Label()
        self.label2.set_text("Время игры:")
        self.label2.set_line_wrap(True)
        self.vbox.pack_start(self.label2, 0, True, 0)

        self.GAME_TIME_text = Gtk.Entry()
        self.GAME_TIME_text.set_text("50")
        self.vbox.pack_start(self.GAME_TIME_text, True, True, 0)

        self.OK_button = Gtk.Button("Применить настройки")
        self.OK_button.connect("clicked", self.OK)
        self.vbox.add(self.OK_button)

        self.ready = Gtk.Button("Инициализация")
        self.ready.connect("clicked", self.init_all)
        self.vbox.add(self.ready)

        self.calib = Gtk.Button("Калибровка робота")
        self.calib.connect("clicked", self.Calibrate_robot)
        self.vbox.add(self.calib)

        self.glass = Gtk.Button("Реинициализация очков")
        self.glass.connect("clicked", self.start_glass)
        self.vbox.add(self.glass)

        self.vid = Gtk.Button("Реинициализация видео")
        self.vid.connect("clicked", self.start_video)
        self.vbox.add(self.vid)
        

        self.window.show_all()
    
    def init_all(self, w):
        self.video=VRproject_without__audio.AR(self.IP)
        self.video.set_player_time_game(self.GAME_TIME)
        self.D = Robot()
        self.D.add_Stepper_Controller(0)
        self.D.add_Motor_Controller(0)
        self.S = self.D.Steppers_Contr_List[0]
        self.M = self.D.Motors_Contr_List[0]
        self.D.Connect(self.IP,13133)
        self.D.Send_Online()
        self.D.Listen()
        self.M.Initialize(ISREADY)
        time.sleep(0.2)
        self.S.Initialize(ISREADY)
        time.sleep(1)
        self.Joy=Jonny_Joy.Jonny_Joystic(self.M)
        self.Joy.start()
        time.sleep(1)
        self.video.start()

        def read_handler(ang):
            self.video.set_angle_list(ang)
            self.video.set_motor_speed(self.Joy.R, self.Joy.L)
            sp=Izbitochnii.CALCULATOR_LENIVOGO_ARTEMA(ang)
            if(self.video.is_over()):
                time.sleep(1)
                self.S.Set_Steppers_Pos( Izbitochnii.middle1, Izbitochnii.middle2, Izbitochnii.middle3)
            else:
                self.S.Set_Steppers_Pos(sp[0],sp[1],sp[2])
                

        def start_handler():
            print("\nI started\n")
            self.video.go_game()

        def stop_handler():
            self.video.set_angle_list([0, 0, 0])
            self.S.Set_Steppers_Pos( Izbitochnii.middle1, Izbitochnii.middle2, Izbitochnii.middle3)
            self.video.clear_game_over()
            
        self.VR=RTCvrangle.VR_thread(self.PATH_TO_GLASS)
        self.VR.connect("START", start_handler)                                                                  
        self.VR.connect("STOP", stop_handler)                                                                   
        self.VR.connect("READ", read_handler)
        self.VR.start()
        

    def Calibrate_robot(self, w):        
        self.S.Calibrate()        

    def start_glass(self, w):
        self.VR.Exit()
        time.sleep(1)
        del self.VR
        time.sleep(2)
        def read_handler(ang):
            self.video.set_angle_list(ang)
            self.video.set_motor_speed(self.Joy.R, self.Joy.L)
            sp=Izbitochnii.CALCULATOR_LENIVOGO_ARTEMA(ang)
            if(self.video.is_over()):
                time.sleep(1)
                self.S.Set_Steppers_Pos( Izbitochnii.middle1, Izbitochnii.middle2, Izbitochnii.middle3)
            else:
                self.S.Set_Steppers_Pos(sp[0],sp[1],sp[2])
                    

        def start_handler():
            print("\nI started\n")
            self.video.go_game()

        def stop_handler():
            self.video.set_angle_list([0, 0, 0])
            self.S.Set_Steppers_Pos( Izbitochnii.middle1, Izbitochnii.middle2, Izbitochnii.middle3)
            self.video.clear_game_over()
                
        self.VR=RTCvrangle.VR_thread(self.PATH_TO_GLASS)
        self.VR.connect("START", start_handler)                                                                  
        self.VR.connect("STOP", stop_handler)                                                                   
        self.VR.connect("READ", read_handler)
        self.VR.start()
            
    def start_video(self, w):
        self.video.stop()
        time.sleep(3)
        self.video.start()
               
    def delete_event(self, widget, event, data=None):        
        Gtk.main_quit()
        self.Joy.Exit()
        self.M.Initialize(NOTREADY)
        self.D.Disconnect()
        self.VR.Exit()
        self.video.stop()
        self.video.timer_exit()
        

    def OK(self, w):
        self.IP = self.IP_text.get_text()
        self.PATH_TO_GLASS = self.path_COM0.get_text()
        self.GAME_TIME = int(self.GAME_TIME_text.get_text())
        print(self.IP)
        print(self.PATH_TO_GLASS)
        print(self.GAME_TIME)

    
        
def th():
    Gtk.main()

t = threading.Thread(target=th)

Jonny_WINDOW()

t.start()

