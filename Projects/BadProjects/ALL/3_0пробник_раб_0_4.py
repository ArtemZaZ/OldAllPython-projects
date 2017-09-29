import gi
import sys
import os
import serial
import threading
import time
gi.require_version("Gst", "1.0")
gi.require_version("Gtk", "3.0")
import pygame
import math
from gi.repository import Gst, GObject, Gtk, GLib
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

#from OpenGL import arrays
#from OpenGL import GLX

STOPREAD=False

appLock = GLib.Mutex()
appCond = GLib.Cond()
GST_initflag = False
texture0 = 0
init_GL_flag= False
angle_list =[0,0,0]
timer0=0
timer1=0
timer=0

FPS_frame=0

#DEST = '127.0.0.1'
DEST = '192.168.42.162'

RTP_RECV_PORT0 = 5000
RTCP_RECV_PORT0 = 5001
RTCP_SEND_PORT0 = 5005

RTP_RECV_PORT1 = 6000
RTCP_RECV_PORT1 = 6001
RTCP_SEND_PORT1 = 6005
VIDEO_CAPS="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)JPEG,payload=(int)26,ssrc=(uint)1006979985,clock-base=(uint)312170047,seqnum-base=(uint)3174"

class VR_angle(object):
        def __init__(self, portname, yaw=0,  pitch=0, roll=0):
            self.port = serial.Serial(portname, baudrate=115200)
            self.yaw = yaw
            self.pitch = pitch
            self.roll = roll
            self.yaw0 = yaw
            self.pitch0 = pitch
            self.roll0 = roll
            
            self.buff=b''
            self.listbuff=[]
            self.yawSTR = b''
            self.pitchSTR = b''
            self.rollSTR = b''
            self.Startflag=False
            

        def _del_(self):
            port.close()

        def read_bytesstr(self):
            k=self.port.read()
            while k!=b'<':
                k=self.port.read()
            while k!=b'>':
                if k!=b'<':
                    self.buff+=k
                k=self.port.read()

        def convert_srtbuffer(self):
            global angle_list
            self.listbuff = list(map(bytes, self.buff.split()))

            if self.listbuff[0]==b'ypr':
                self.yaw = float(self.listbuff[1])
                self.pitch = float(self.listbuff[2])
                self.roll = float(self.listbuff[-1])
                angle_list=self.get_ypr_list()

            if(self.Startflag):
                self.yaw0 = self.yaw
                self.pitch0 = self.pitch
                self.roll0 = self.roll   
                self.Startflag=False
            
                
            if self.listbuff[0]==b'*':
                print("COMMENT: \n")

            if self.listbuff[0]==b'start':                    
                self.Startflag=True

            if self.listbuff[0]==b'stop':
       
                self.yaw0 = 0
                self.pitch0 = 0
                self.roll0 = 0

                
        def get_yaw(self):
            return self.yaw
        def get_pitch(self):
            return self.pitch
        def get_roll(self):
            return self.roll
        def get_ypr_list(self):
            A=[self.yaw-self.yaw0, self.pitch-self.pitch0, self.roll-self.roll0]
            return A


        def start_read_VR_angle(self):
            self.read_bytesstr()
            #print(self.buff, '\n')
            self.buff=b''
            self.port.write(b'g')
            while not STOPREAD:
                self.read_bytesstr()
                self.convert_srtbuffer()
                #print(self.buff, '\n')                
                #print(self.yaw, self.pitch, self.roll, '\n')
                #print(self.yaw0, self.pitch0, self.roll0, '\n')
                self.buff=b''


class VR_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global angle_list
        firstVR=VR_angle("/dev/ttyUSB0")
        firstVR.start_read_VR_angle()
        print("VR_THREAD stop")
        




def readfromfile(filename):
    file=open(filename, "r")
    shaderstr=file.read()
    file.close()
    return shaderstr

def loadImageStr ( fileName ):
    glEnable(GL_TEXTURE_2D)

    image1  = pygame.image.load( fileName )
    imagestr = pygame.image.tostring(image1, "RGBA")
    return imagestr

def initGL ():
    global texture0
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_DST_ALPHA)
    glEnable(GL_ALPHA_TEST)
    
    glAlphaFunc(GL_GREATER, 0.4)
    glEnable(GL_TEXTURE_2D)
    glDepthMask(GL_FALSE)
    
    glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE )
    textureImage = loadImageStr("ring.png")


    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    texture0=glGenTextures(1)
    
    glBindTexture(GL_TEXTURE_2D, texture0)
    glTexImage2D(GL_TEXTURE_2D, 0, 4, 722, 706, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureImage)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    #glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_ALPHA_TEST)
    #glShadeModel(GL_FLAT)
    print(texture0)





def reshape(w, h):
    glViewport     ( 0, 0, w, h )
    glMatrixMode   ( GL_PROJECTION )
    glLoadIdentity ()
    gluPerspective ( 60.0, float(w)/float (h), 1.0, 60.0 )
    glMatrixMode   ( GL_MODELVIEW )

def draw_callback0(GST_object, width, height, texture):
    global appLock
    global appCond
    global texture0
    global init_GL_flag
    global angle_list
    global timer
    global timer0
    global timer1
    global FPS_frame
    FPS_frame=FPS_frame+1

    timer=time.time()
    timer1=timer1+timer-timer0
    
    if(timer1>1):
        print(2*FPS_frame)
        FPS_frame=0
        timer1=0    
    timer0=timer
    
    
    #timer0=time.time()
    if not appLock.trylock():
        print("error Lock")
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_ALPHA_TEST)
    glEnable(GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    if not init_GL_flag:
            initGL()
            init_GL_flag = True

    glMatrixMode   ( GL_PROJECTION )
    glLoadIdentity ()
    gluPerspective ( 60.0, float(width)/float (height), 1.0, 200.0 )
    glMatrixMode   ( GL_MODELVIEW )
    glLoadIdentity ()

    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)
    #glColor4f(0.0, 0.0, 0.0, 0.3)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0,  1.0, -1.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( 1.0,  1.0, -1.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( 1.0, -1.0, -1.0)
    glEnd()
    

  
    gluLookAt(50,-20,50,50+math.sin(angle_list[0]/180*3.14),-20+math.tan((180-angle_list[1])/180*3.14), 50-math.cos(angle_list[0]/180*3.14),0,1,0)
    

    
    glBindTexture(GL_TEXTURE_2D, texture0)
    glBegin(GL_QUADS)
    glColor4f(1.0, 1.0, 1.0, 0.3)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(0.0, 0.0, 100.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(100.0, 0.0, 100.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(100.0, 0.0, 0.0)

    glEnd()
    
    
    glDisable(GL_ALPHA_TEST)

    #GLib.Mutex.unlock(GST_object.lock)
    appCond.signal()
    
    #GLib.Cond.signal(appCond)
    #GLib.Mutex.unlock(appLock)
    appLock.unlock()
    
    
    
    
    return True
        
def draw_callback1(GST_object, width, height, texture):
    global appLock
    global appCond
    global texture0
    global angle_list
    if not appLock.trylock():
        print("error Lock")
    glEnable(GL_TEXTURE_2D)
    glMatrixMode   ( GL_PROJECTION )
    glLoadIdentity ()
    gluPerspective ( 60.0, float(width)/float (height), 1.0, 200.0 )
    glMatrixMode   ( GL_MODELVIEW )
    glLoadIdentity ()
    #print(texture)
    #print(texture0)
    glEnable(GL_ALPHA_TEST)
    glEnable(GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
   
    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)
    glColor4f(0.0, 0.0, 0.0, 0.3)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0,  1.0, -1.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( 1.0,  1.0, -1.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( 1.0, -1.0, -1.0)
    glEnd()
    

  
    gluLookAt(50,-20,50,50+math.sin(angle_list[0]/180*3.14),-20+math.tan((180-angle_list[1])/180*3.14), 50-math.cos(angle_list[0]/180*3.14),0,1,0)
    

    
    glBindTexture(GL_TEXTURE_2D, texture0)
    glBegin(GL_QUADS)
    glColor4f(1.0, 1.0, 1.0, 0.3)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(0.0, 0.0, 100.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(100.0, 0.0, 100.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(100.0, 0.0, 0.0)

    glEnd()
    glDisable(GL_ALPHA_TEST)
    
    
    
    #GLib.Mutex.unlock(GST_object.lock)
    appCond.signal()
    
    #GLib.Cond.signal(appCond)
    #GLib.Mutex.unlock(appLock)
    appLock.unlock()
    
    
    return True
		                            


        

simple_vertex_shader_str_gles2 = readfromfile("vertex_shader.frag")
distortion_fragment_shader=readfromfile("fragment_shader.frag")

class GTK_Main:
    
    
    
    def init_VARandLIB(self):
        global appLock
        global appCond
        
        print (appLock)
        Gtk.init(sys.argv)
        
        
        

        Gst.init(sys.argv)
        #GLib.Mutex.init(appLock)
        print(appLock)
        #GLib.Cond.init(appCond)
        

        glutInit(sys.argv)
        #initGL()
        appLock.init()
        appCond.init()
        print(appLock)
        GLib.setenv("GST_GL_API", "opengl", False)

        self.player = Gst.Pipeline.new("player")
        if not self.player:
            print("ERROR: Could not create pipeline.")
            sys.exit(1)
            
        bus=self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message::error", self.on_error)
        bus.connect("message::eos", self.on_eos)

################ VIDEODEPAY ################################
        videodepay0=Gst.ElementFactory.make('rtpjpegdepay', 'videodepay0')
        if not videodepay0:
            print("ERROR: Could not create videodepay0.")
            sys.exit(1)

        videodepay1=Gst.ElementFactory.make('rtpjpegdepay', 'videodepay1')
        if not videodepay1:
            print("ERROR: Could not create videodepay1.")
            sys.exit(1)
        
################  SOURCE  ##################################        
        
            
        rtpbin = Gst.ElementFactory.make('rtpbin', 'rtpbin')
        self.player.add(rtpbin)
        caps = Gst.caps_from_string(VIDEO_CAPS)
        
        def pad_added_cb(rtpbin, new_pad, depay):
            sinkpad = Gst.Element.get_static_pad(depay, 'sink')
            lres = Gst.Pad.link(new_pad, sinkpad)        
        
       
        rtpsrc0 = Gst.ElementFactory.make('udpsrc', 'rtpsrc0')
        rtpsrc0.set_property('port', RTP_RECV_PORT0)
    
        # we need to set caps on the udpsrc for the RTP data
        
        rtpsrc0.set_property('caps', caps)
    
        rtcpsrc0 = Gst.ElementFactory.make('udpsrc', 'rtcpsrc0')
        rtcpsrc0.set_property('port', RTCP_RECV_PORT0)

        rtcpsink0 = Gst.ElementFactory.make('udpsink', 'rtcpsink0')
        rtcpsink0.set_property('port', RTCP_SEND_PORT0)
        rtcpsink0.set_property('host', DEST)
    
        # no need for synchronisation or preroll on the RTCP sink
        rtcpsink0.set_property('async', False)
        rtcpsink0.set_property('sync', False)
        self.player.add(rtpsrc0, rtcpsrc0, rtcpsink0)

        

        srcpad0 = Gst.Element.get_static_pad(rtpsrc0, 'src')
        
        sinkpad0 = Gst.Element.get_request_pad(rtpbin, 'recv_rtp_sink_0')
        lres0 = Gst.Pad.link(srcpad0, sinkpad0)
    
        # get an RTCP sinkpad in session 0
        srcpad0 = Gst.Element.get_static_pad(rtcpsrc0, 'src')
        sinkpad0 = Gst.Element.get_request_pad(rtpbin, 'recv_rtcp_sink_0')
        lres0 = Gst.Pad.link(srcpad0, sinkpad0)
    
        # get an RTCP srcpad for sending RTCP back to the sender
        srcpad0 = Gst.Element.get_request_pad(rtpbin, 'send_rtcp_src_0')
        sinkpad0 = Gst.Element.get_static_pad(rtcpsink0, 'sink')
        lres0 = Gst.Pad.link(srcpad0, sinkpad0)
        
###################### SECOND ################################

            
        #rtpbin1 = Gst.ElementFactory.make('rtpbin', 'rtpbin1')
        #self.player.add(rtpbin1)
            
        rtpsrc1 = Gst.ElementFactory.make('udpsrc', 'rtpsrc1')
        rtpsrc1.set_property('port', RTP_RECV_PORT1)
    
        # we need to set caps on the udpsrc for the RTP data
        
        rtpsrc1.set_property('caps', caps)
    
        rtcpsrc1 = Gst.ElementFactory.make('udpsrc', 'rtcpsrc1')
        rtcpsrc1.set_property('port', RTCP_RECV_PORT1)

        rtcpsink1 = Gst.ElementFactory.make('udpsink', 'rtcpsink1')
        rtcpsink1.set_property('port', RTCP_SEND_PORT1)
        rtcpsink1.set_property('host', DEST)
    
        # no need for synchronisation or preroll on the RTCP sink
        rtcpsink1.set_property('async', False)
        rtcpsink1.set_property('sync', False)
        self.player.add(rtpsrc1, rtcpsrc1, rtcpsink1)


        srcpad1 = Gst.Element.get_static_pad(rtpsrc1, 'src')
        sinkpad1 = Gst.Element.get_request_pad(rtpbin, 'recv_rtp_sink_1')
        lres1 = Gst.Pad.link(srcpad1, sinkpad1)
    
        # get an RTCP sinkpad in session 0
        srcpad1 = Gst.Element.get_static_pad(rtcpsrc1, 'src')
        sinkpad1 = Gst.Element.get_request_pad(rtpbin, 'recv_rtcp_sink_1')
        lres1 = Gst.Pad.link(srcpad1, sinkpad1)
    
        # get an RTCP srcpad for sending RTCP back to the sender
        srcpad1 = Gst.Element.get_request_pad(rtpbin, 'send_rtcp_src_1')
        sinkpad1 = Gst.Element.get_static_pad(rtcpsink1, 'sink')
        lres1 = Gst.Pad.link(srcpad1, sinkpad1)
        rtpbin.connect('pad-added', pad_added_cb, videodepay1)
        rtpbin.connect('pad-added', pad_added_cb, videodepay0)


############### DECODER ######################################
        decoder0 = Gst.ElementFactory.make('jpegdec', "decoder0")
        if not decoder0:
            print("ERROR: Could not create decoder0.")
            sys.exit(1)

        decoder1 = Gst.ElementFactory.make('jpegdec', "decoder1")
        if not decoder1:
            print("ERROR: Could not create decoder1.")
            sys.exit(1)
            
######################### GLUPLOAD ###########################
        glupload0 = Gst.ElementFactory.make('glupload', "glupload0")
        if not glupload0:
            print("ERROR: Could not create glupload0.")
            sys.exit(1)


        glupload1 = Gst.ElementFactory.make('glupload', "glupload1")
        if not glupload1:
            print("ERROR: Could not create glupload1.")
            sys.exit(1)    
            

######################## GLCOLORCONVERT ############################
        glcolorconvert0 = Gst.ElementFactory.make("glcolorconvert", "glcolorconvert0")
        if not glcolorconvert0:
            print("ERROR: Could not create glcolorconvert0.")
            sys.exit(1)


        glcolorconvert1 = Gst.ElementFactory.make("glcolorconvert", "glcolorconvert1")
        if not glcolorconvert1:
            print("ERROR: Could not create glcolorconvert1.")
            sys.exit(1)

######################### CAPS AND SINK ###########################
               
        sink = Gst.ElementFactory.make('glimagesink', "video-output")
        if not sink:
            print("ERROR: Could not create sink.")
            sys.exit(1)

            
       

######################### VIDEOMIXER ##################################
        videomixer = Gst.ElementFactory.make("glvideomixer", "videomixer")
        if not videomixer:
            print("ERROR: Could not create videomixer.")
            sys.exit(1)      

        
        videomixer.set_property("background", 1)
        videomixer.set_property("async-handling", 1)
        videomixer.set_property("message-forward", 1)

        mixer_sink_pad0 = videomixer.get_request_pad("sink_%u")
        mixer_sink_pad0.set_property("xpos", 640)
        mixer_sink_pad0.set_property("ypos", 0)
        mixer_sink_pad0.set_property("width", 640)

        mixer_sink_pad1 = videomixer.get_request_pad("sink_%u")
        mixer_sink_pad1.set_property("xpos", 0)
        mixer_sink_pad1.set_property("ypos", 0)
        mixer_sink_pad1.set_property("width", 640)

########################## SHADER #####################################
        glshader = Gst.ElementFactory.make("glshader", "glshader")
        glshader.set_property("vertex", simple_vertex_shader_str_gles2)
        glshader.set_property("fragment", distortion_fragment_shader)

####################### FILTERAPP ####################################
        
        glfilterapp0 = Gst.ElementFactory.make("glfilterapp", "glfilterapp0")
        
        

        glfilterapp0.connect("client-draw", draw_callback0)

        glfilterapp1 = Gst.ElementFactory.make("glfilterapp", "glfilterapp1")
        

        glfilterapp1.connect("client-draw", draw_callback1)

##################################################################        
        self.player.add(videodepay0)
        self.player.add(decoder0)
        self.player.add(glupload0)
        self.player.add(glcolorconvert0)
        self.player.add(glfilterapp0)
        self.player.add(videodepay1)
        self.player.add(decoder1)
        self.player.add(glupload1)
        self.player.add(glcolorconvert1)
        self.player.add(glfilterapp1)
        self.player.add(videomixer)
        self.player.add(glshader)        
        self.player.add(sink)

        
        link_ok = videodepay0.link(decoder0)
        if not link_ok:
            print("ERROR: Could not link videodepay0 with decoder0.")
            sys.exit(1)
        link_ok = decoder0.link(glupload0)
        if not link_ok:
            print("ERROR: Could not link decoder0 with glupload0.")
            sys.exit(1)
        link_ok = glupload0.link(glcolorconvert0)
        if not link_ok:
            print("ERROR: Could not link glupload0 with glcolorconvert0.")
            sys.exit(1)
        link_ok = glcolorconvert0.link(glfilterapp0)
        if not link_ok:
            print("ERROR: Could not link glcolorconvert0 with glfilterapp0.")
            sys.exit(1)
        
            

        source0_src_pad = glfilterapp0.get_static_pad("src")
        link_ok = source0_src_pad.link(mixer_sink_pad0)
        print (link_ok)

        


        link_ok = videodepay1.link(decoder1)
        if not link_ok:
            print("ERROR: Could not link videodepay1 with decoder1.")
            sys.exit(1)
        link_ok = decoder1.link(glupload1)
        if not link_ok:
            print("ERROR: Could not link decoder1 with glupload1.")
            sys.exit(1)
        link_ok = glupload1.link(glcolorconvert1)
        if not link_ok:
            print("ERROR: Could not link glupload1 with glcolorconvert1.")
            sys.exit(1)
        link_ok = glcolorconvert1.link(glfilterapp1)
        if not link_ok:
            print("ERROR: Could not link glcolorconvert1 with glfilterapp1.")
            sys.exit(1)

        source1_src_pad = glfilterapp1.get_static_pad("src")
        link_ok = source1_src_pad.link(mixer_sink_pad1)
        print (link_ok)
            
        link_ok = videomixer.link(glshader)
        if not link_ok:
            print("ERROR: Could not link videomixer with glshader.")
            sys.exit(1)

        link_ok = glshader.link(sink)
        if not link_ok:
            print("ERROR: Could not link glshader with sink.")
            sys.exit(1)
        

        
    
    def __init__(self):
        loop = GLib.MainLoop.new(None, False)
        global GST_initflag
        if not GST_initflag:
            GTK_Main.init_VARandLIB(self)
            GST_initflag = True
        
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Videotestsrc-Player")
        window.set_default_size(300, -1)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        
        self.button = Gtk.Button("Start")
        self.button.connect("clicked", self.start_stop)
        vbox.add(self.button)
        window.show_all()
        loop.run()
################################################################        
                

#############################################         
    def on_error(self, bus, msg):
        err, dbg = msg.parse_error()
        print("ERROR:", msg.src.get_name(), ":", err.message)
        if dbg:
            print("Debug info:", dbg)

    
    def on_eos(self, bus, msg):
        print("End-Of-Stream reached")
        self.playbin.set_state(Gst.State.READY)
#############################################
        
    def start_stop(self, w):
        global STOPREAD
        if self.button.get_label() == "Start":
            self.button.set_label("Stop")
            self.player.set_state(Gst.State.PLAYING)
        else:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
            STOPREAD=True
    

    
########################################################
VR_TH=VR_thread()
VR_TH.start()
GObject.threads_init()
Gst.init(None)
GTK_Main()
Gtk.main()


