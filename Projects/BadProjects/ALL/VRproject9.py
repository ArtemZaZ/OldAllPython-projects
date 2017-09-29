import gi
import sys
import os
import serial
import threading
import time
gi.require_version("Gst", "1.0")
gi.require_version("Gtk", "3.0")
import math
from gi.repository import Gst, GObject, Gtk, GLib
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

import RTCvideo
import RTCevent_master
from RTCeffect import *


WIDTH=1280
HEIGHT=720

END_TIMER=False


texture0=RTCvideo.texture_block()
game_over_texture=RTCvideo.texture_block()
speedR=Speedometr([0.57, 0.5, 0.0], 0.05)
speedL=Speedometr([-0.57, 0.5, 0.0], 0.05)

angle_list = [0,0,0]
coord_list = [0,0,0]
init_GL_flag= False
distance=-15.0
temp=0.0

speedR_now=0
speedL_now=0




DEST = '127.0.0.1'
#DEST = '192.168.42.162'

RTP_RECV_PORT0 = 5000
RTCP_RECV_PORT0 = 5001
RTCP_SEND_PORT0 = 5005

RTP_RECV_PORT1 = 6000
RTCP_RECV_PORT1 = 6001
RTCP_SEND_PORT1 = 6005

RTP_RECV_PORT1 = 7000
RTCP_RECV_PORT1 = 7001
RTCP_SEND_PORT1 = 7005
VIDEO_CAPS="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)JPEG,payload=(int)26,ssrc=(uint)1006979985,clock-base=(uint)312170047,seqnum-base=(uint)3174"
AUDIO_CAPS="application/x-rtp,media=(string)audio,clock-rate=(int)8000,encoding-name=(string)SPEEX"


        

class Timer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.timer=0
        self.RUN=False
        self.predel=100
        self.Exit=False
        
    def run(self):
        global END_TIMER
        while not self.Exit:
            if self.RUN:
                self.timer=self.timer+1
                print(self.timer)
                if(self.timer>=self.predel):
                    END_TIMER=True
                    self.RUN=False  
            time.sleep(1)
        
    def clear(self):
        self.RUN=False
        self.timer=0
        
    def set_predel(self, pr):
        self.predel=pr

    def go(self):
        global END_TIMER
        self.RUN=True
        self.timer=0
        END_TIMER=False


    def exit(self):
        self.Exit=True

timer1=Timer()


def initGL():
    global texture0
    global game_over_texture
    
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_ALPHA_TEST)
    
    glAlphaFunc(GL_GREATER, 0.4)
    glEnable(GL_TEXTURE_2D)
    glDepthMask(GL_FALSE)
    
    texture0.set_image("arrow.png")
    texture0.set_vertexcoord([-6.0, 17.0, -10.0-34.0], [-6.0, 17.0, -10.0-22.0], [6.0, 17.0, -10.0-22.0], [6.0, 17.0, -10.0-34.0])

    game_over_texture.set_image("game_over.png")
    game_over_texture.set_vertexcoord([-1.0, -0.8, -1.0], [-1.0,  1.2, -1.0], [1.0,  1.2, -1.0], [1.0, -0.8, -1.0])
    
    if(texture0.pixel_x*texture0.pixel_x>0):
        texture0.gen_texture()
        if( texture0.texture ==0):        
            print("ERROR: Gen texture\n")

    if(game_over_texture.pixel_x*game_over_texture.pixel_x>0):
        game_over_texture.gen_texture()
        if( game_over_texture.texture ==0):        
            print("ERROR: Gen texture\n")

    glEnable(GL_TEXTURE_2D)
    glDisable(GL_ALPHA_TEST)



def draw_videotexture(texture):
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


def draw_arrow(texture0):
                  ##############################    

    glDisable(GL_TEXTURE_2D)

    glPushMatrix()
    glTranslate(0.0, 17.0, -28.0)
    glRotatef(90.0, 1.0, 0.0,0.0)

    
    glColor4f(1.0, 1.0, 1.0, 0.7)
    
    glutSolidCylinder( 1.0 , 1.0, 10, 10)
    glPopMatrix()
 
    glEnable(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, texture0.texture)
    glBegin(GL_QUADS)
    glColor4f(1.0, 1.0, 1.0, 0.3)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(texture0.vertexcoord1[0], texture0.vertexcoord1[1], texture0.vertexcoord1[2])
    glTexCoord2f(0.0, 0.0)
    glVertex3f(texture0.vertexcoord2[0], texture0.vertexcoord2[1], texture0.vertexcoord2[2])
    glTexCoord2f(1.0, 0.0)
    glVertex3f(texture0.vertexcoord3[0], texture0.vertexcoord3[1], texture0.vertexcoord3[2])
    glTexCoord2f(1.0, 1.0)
    glVertex3f(texture0.vertexcoord4[0], texture0.vertexcoord4[1], texture0.vertexcoord4[2])
    glEnd()
    


    

    

def draw_cube(texture, size):
    glPushMatrix()
    
    glTranslate(20.0, 0.0, 0.0)

    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)



     
    glTexCoord2f(0.0, 0.0)
    glVertex3f(  size, -size, -size )
    glTexCoord2f(0.0, 1.0)
    glVertex3f(  size,  size, -size )
    glTexCoord2f(1.0, 1.0)
    glVertex3f( -size,  size, -size )
    glTexCoord2f(1.0, 0.0)
    glVertex3f( -size, -size, -size )
     
    glEnd()

    glBegin(GL_QUADS)    
    glColor3f(   1.0,  1.0, 1.0 )
    glTexCoord2f(0.0, 0.0)
    glVertex3f(  size, -size, size )
    glTexCoord2f(0.0, 1.0)    
    glVertex3f(  size,  size, size)
    glTexCoord2f(1.0, 1.0)   
    glVertex3f( -size,  size, size )
    glTexCoord2f(1.0, 0.0)
    glVertex3f( -size, -size, size )
    glEnd()
     
    
    glBegin(GL_QUADS)
    glColor3f(  1.0,  0.0,  1.0 )
    glTexCoord2f(0.0, 0.0)
    glVertex3f( size, -size, -size )
    glTexCoord2f(0.0, 1.0)
    glVertex3f( size,  size, -size )
    glTexCoord2f(1.0, 1.0)
    glVertex3f( size,  size,  size )
    glTexCoord2f(1.0, 0.0)
    glVertex3f( size, -size,  size )
    glEnd()
     
    
    glBegin(GL_QUADS)
    glColor3f(   0.0,  1.0,  0.0 )
    glTexCoord2f(0.0, 0.0)
    glVertex3f( -size, -size,  size )
    glTexCoord2f(0.0, 1.0)
    glVertex3f( -size,  size,  size )
    glTexCoord2f(1.0, 1.0)
    glVertex3f( -size, size, -size )
    glTexCoord2f(1.0, 0.0)
    glVertex3f( -size, -size, -size )
    glEnd()
     
    
    glBegin(GL_QUADS)
    glColor3f(   0.0,  0.0,  1.0 )
    glTexCoord2f(0.0, 0.0)
    glVertex3f(  size,  size,  size )
    glTexCoord2f(0.0, 1.0)
    glVertex3f(  size,  size, size )
    glTexCoord2f(1.0, 1.0)
    glVertex3f( -size,  size, -size )
    glTexCoord2f(0.0, 1.0)
    glVertex3f( -size,  size,  size )
    glEnd()
     
    
    glBegin(GL_QUADS)
    glColor3f(   1.0,  0.0,  0.0 )
    glTexCoord2f(0.0, 0.0)
    glVertex3f(  size, -size, -size )
    glTexCoord2f(0.0, 1.0)
    glVertex3f(  size, -size,  size )
    glTexCoord2f(1.0, 1.0)
    glVertex3f( -size, -size,  size )
    glTexCoord2f(1.0, 0.0)
    glVertex3f( -size, -size, -size )
    glEnd()

    glPopMatrix()
    




def draw_callback0(GST_object, width, height, texture):
    global END_TIMER
    global texture0
    global game_over_texture
    global init_GL_flag
    global distance
    global angle_list
    global speedR
    global speedL
    global speedR_now
    global speedL_now
    global temp
    global coord_list

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_ALPHA_TEST)
    glEnable(GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    if not init_GL_flag:
        initGL()
        init_GL_flag = True
        
    glMatrixMode   ( GL_PROJECTION )
    glLoadIdentity ()
    gluPerspective ( 60.0, float(width)/float (height),  1.0, 200.0 )
    glMatrixMode   ( GL_MODELVIEW )
    glLoadIdentity ()

    draw_videotexture(texture)
    temp=temp+1
    if(temp>100):
        temp=0
    speedR.set_motor_power(speedR_now)
    speedL.set_motor_power(speedL_now)

    glPushMatrix()
    glTranslate(-0.02, 0.0, 0.0)
    speedR.draw_speedometr()
    speedL.draw_speedometr()
    ang=angle_list
    if END_TIMER:
        glBindTexture(GL_TEXTURE_2D, game_over_texture.texture)

        glTranslate(-0.04, 0.0, 0.0)

        #glTranslate(0.5, 0.0, 0.0)

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(game_over_texture.vertexcoord1[0], game_over_texture.vertexcoord1[1], distance+game_over_texture.vertexcoord1[2])
        glTexCoord2f(0.0, 0.0)
        glVertex3f(game_over_texture.vertexcoord2[0], game_over_texture.vertexcoord2[1], distance+game_over_texture.vertexcoord2[2])
        glTexCoord2f(1.0, 0.0)
        glVertex3f(game_over_texture.vertexcoord3[0], game_over_texture.vertexcoord3[1], distance+game_over_texture.vertexcoord3[2])
        glTexCoord2f(1.0, 1.0)
        glVertex3f(game_over_texture.vertexcoord4[0], game_over_texture.vertexcoord4[1], distance+game_over_texture.vertexcoord4[2])
        glEnd()
        

        ang=[0,0,0]
        if(distance<-2.0):
            distance=distance+1.0
    else:
        distance=-15.0

    glPopMatrix()
    

    
    glPushMatrix()

    gluLookAt(0.0+coord_list[0], -7+coord_list[1], 0.0+coord_list[2], coord_list[0]+math.sin(ang[0]/180*math.pi),-7+coord_list[1]+math.tan((180-ang[1])/180*math.pi), coord_list[2]-math.cos(ang[0]/180*math.pi),0,1,0)
    glTranslate(-1.5*math.cos(ang[0]/180*math.pi), 0.0, -1.5*math.sin(ang[0]/180*math.pi))

    draw_cube(game_over_texture.texture, 4)
    draw_arrow(texture0)
    glPopMatrix()

    

    
    glDisable(GL_ALPHA_TEST)
    glDisable(GL_BLEND)

    return True


def draw_callback1(GST_object, width, height, texture):
    global END_TIMER
    global texture0
    global game_over_texture
    global distance
    global init_GL_flag
    global angle_list
    global speedR
    global speedL
    global speedR_now
    global speedL_now
    global temp

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

    draw_videotexture(texture)
    
    glPushMatrix()
    glTranslate(0.02, 0.0, 0.0)
    speedR.draw_speedometr()
    speedL.draw_speedometr()
    

    ang=angle_list
    
    if END_TIMER:
        glBindTexture(GL_TEXTURE_2D, game_over_texture.texture)
        #glTranslate(-0.5, 0.0, 0.0)
        glTranslate(0.04, 0.0, 0.0)

        glBegin(GL_QUADS)
        glColor4f(1.0, 1.0, 1.0, 0.3)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(game_over_texture.vertexcoord1[0], game_over_texture.vertexcoord1[1], distance+game_over_texture.vertexcoord1[2])
        glTexCoord2f(0.0, 0.0)
        glVertex3f(game_over_texture.vertexcoord2[0], game_over_texture.vertexcoord2[1], distance+game_over_texture.vertexcoord2[2])
        glTexCoord2f(1.0, 0.0)
        glVertex3f(game_over_texture.vertexcoord3[0], game_over_texture.vertexcoord3[1], distance+game_over_texture.vertexcoord3[2])
        glTexCoord2f(1.0, 1.0)
        glVertex3f(game_over_texture.vertexcoord4[0], game_over_texture.vertexcoord4[1], distance+game_over_texture.vertexcoord4[2])
        glEnd()

        ang=[0,0,0]
    glPopMatrix()



    glPushMatrix()

    gluLookAt(0.0+coord_list[0], -7+coord_list[1], 0.0+coord_list[2], coord_list[0]+math.sin(ang[0]/180*math.pi),-7+coord_list[1]+math.tan((180-ang[1])/180*math.pi), coord_list[2]-math.cos(ang[0]/180*math.pi),0,1,0)
    glTranslate(1.5*math.cos(ang[0]/180*math.pi), 0.0, 1.5*math.sin(ang[0]/180*math.pi))

    draw_cube(game_over_texture.texture, 4)
    draw_arrow(texture0)
    glPopMatrix()

    

    
    
    
    #glTranslate(-distance, 0.0, 0.0)

    
    glDisable(GL_ALPHA_TEST)
    glDisable(GL_BLEND)
    
    return True





class AR:
    

    def __init__(self):
        global timer1
        self.simple_vertex_shader_str_gles2 = RTCvideo.read_shader_fromfile("vertex_shader.frag")
        self.distortion_fragment_shader=RTCvideo.read_shader_fromfile("fragment_shader.frag")
        Gst.init(sys.argv)
        glutInit(sys.argv)
        GLib.setenv("GST_GL_API", "opengl", False)
        self.PAUSED=False
        
        

    def start(self):
        if(self.PAUSED==True):
            self.player.set_state(Gst.State.PLAYING)
            timer1.start()
            self.PAUSED=False
        else:
            global init_GL_flag
            self.init_element()
            self.link_element()
            timer1.start()
            init_GL_flag=False
            self.player.set_state(Gst.State.READY)
            self.player.set_state(Gst.State.PAUSED)
            self.player.set_state(Gst.State.PLAYING)


    def paused(self):
        self.player.set_state(Gst.State.PAUSED)
        self.PAUSED=True

    def stop(self):
        global timer1
        timer1.exit()
        self.player.set_state(Gst.State.NULL)
        self.PAUSED=False
        
        print("STOP")

    def on_error(self, bus, msg):
        err, dbg = msg.parse_error()
        print("ERROR:", msg.src.get_name(), ":", err.message)
        if dbg:
            print("Debug info:", dbg)

    
    def on_eos(self, bus, msg):
        print("End-Of-Stream reached")
        self.player.set_state(Gst.State.READY)


    def set_angle_list(self, angle):
        global angle_list
        angle_list=angle

    def set_motor_speed(self, R, L):
        global speedR_now
        global speedL_now
        speedR_now=abs(R)
        speedL_now=abs(L)

    def set_coord(self, x, y, z):
        global coord_list
        coord_list=[x,y,z]

    def set_player_time_game(self, time=30):
        global timer1
        timer1.set_predel(time)

    def go_game(self):
        global timer1
        timer1.go()

    def clear_game_over(self):
        global END_TIMER
        global timer1
        timer1.clear()
        END_TIMER=False

    def is_over(self):
        global END_TIMER
        return END_TIMER


    def init_element(self):
        self.player = Gst.Pipeline.new("player")
        if not self.player:
            print("ERROR: Could not create pipeline.")
            sys.exit(1)
            
        self.bus=self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message::error", self.on_error)
        self.bus.connect("message::eos", self.on_eos)

################ VIDEODEPAY ################################
        self.videodepay0=Gst.ElementFactory.make('rtpjpegdepay', 'videodepay0')
        if not self.videodepay0:
            print("ERROR: Could not create videodepay0.")
            sys.exit(1)

        self.videodepay1=Gst.ElementFactory.make('rtpjpegdepay', 'videodepay1')
        if not self.videodepay1:
            print("ERROR: Could not create videodepay1.")
            sys.exit(1)

        self.audiodepay0=Gst.ElementFactory.make('rtpspeexdepay', 'audiodepay0')
        if not self.audiodepay0:
            print("ERROR: Could not create audiodepay0.")
            sys.exit(1)
        
################  SOURCE  ##################################        
        
            
        self.rtpbin = Gst.ElementFactory.make('rtpbin', 'rtpbin')
        self.player.add(self.rtpbin)
        self.caps = Gst.caps_from_string(VIDEO_CAPS)
        self.audio_caps = Gst.caps_from_string(AUDIO_CAPS)
        
        def pad_added_cb(rtpbin, new_pad, depay):
            sinkpad = Gst.Element.get_static_pad(depay, 'sink')
            lres = Gst.Pad.link(new_pad, sinkpad)        
        
       
        self.rtpsrc0 = Gst.ElementFactory.make('udpsrc', 'rtpsrc0')
        self.rtpsrc0.set_property('port', RTP_RECV_PORT0)
    
        # we need to set caps on the udpsrc for the RTP data
        
        self.rtpsrc0.set_property('caps', self.caps)
    
        self.rtcpsrc0 = Gst.ElementFactory.make('udpsrc', 'rtcpsrc0')
        self.rtcpsrc0.set_property('port', RTCP_RECV_PORT0)

        self.rtcpsink0 = Gst.ElementFactory.make('udpsink', 'rtcpsink0')
        self.rtcpsink0.set_property('port', RTCP_SEND_PORT0)
        self.rtcpsink0.set_property('host', DEST)
    
        # no need for synchronisation or preroll on the RTCP sink
        self.rtcpsink0.set_property('async', False)
        self.rtcpsink0.set_property('sync', False)
        self.player.add(self.rtpsrc0, self.rtcpsrc0, self.rtcpsink0)

        

        self.srcpad0 = Gst.Element.get_static_pad(self.rtpsrc0, 'src')
        
        self.sinkpad0 = Gst.Element.get_request_pad(self.rtpbin, 'recv_rtp_sink_0')
        self.lres0 = Gst.Pad.link(self.srcpad0, self.sinkpad0)
    
        # get an RTCP sinkpad in session 0
        self.srcpad0 = Gst.Element.get_static_pad(self.rtcpsrc0, 'src')
        self.sinkpad0 = Gst.Element.get_request_pad(self.rtpbin, 'recv_rtcp_sink_0')
        self.lres0 = Gst.Pad.link(self.srcpad0, self.sinkpad0)
    
        # get an RTCP srcpad for sending RTCP back to the sender
        self.srcpad0 = Gst.Element.get_request_pad(self.rtpbin, 'send_rtcp_src_0')
        self.sinkpad0 = Gst.Element.get_static_pad(self.rtcpsink0, 'sink')
        self.lres0 = Gst.Pad.link(self.srcpad0, self.sinkpad0)
        
###################### SECOND ################################

            
        #rtpbin1 = Gst.ElementFactory.make('rtpbin', 'rtpbin1')
        #self.player.add(rtpbin1)
            
        self.rtpsrc1 = Gst.ElementFactory.make('udpsrc', 'rtpsrc1')
        self.rtpsrc1.set_property('port', RTP_RECV_PORT1)
    
        # we need to set caps on the udpsrc for the RTP data
        
        self.rtpsrc1.set_property('caps', self.caps)
    
        self.rtcpsrc1 = Gst.ElementFactory.make('udpsrc', 'rtcpsrc1')
        self.rtcpsrc1.set_property('port', RTCP_RECV_PORT1)

        self.rtcpsink1 = Gst.ElementFactory.make('udpsink', 'rtcpsink1')
        self.rtcpsink1.set_property('port', RTCP_SEND_PORT1)
        self.rtcpsink1.set_property('host', DEST)
    
        # no need for synchronisation or preroll on the RTCP sink
        self.rtcpsink1.set_property('async', False)
        self.rtcpsink1.set_property('sync', False)
        self.player.add(self.rtpsrc1, self.rtcpsrc1, self.rtcpsink1)


        self.srcpad1 = Gst.Element.get_static_pad(self.rtpsrc1, 'src')
        self.sinkpad1 = Gst.Element.get_request_pad(self.rtpbin, 'recv_rtp_sink_1')
        self.lres1 = Gst.Pad.link(self.srcpad1, self.sinkpad1)
    
        # get an RTCP sinkpad in session 0
        self.srcpad1 = Gst.Element.get_static_pad(self.rtcpsrc1, 'src')
        self.sinkpad1 = Gst.Element.get_request_pad(self.rtpbin, 'recv_rtcp_sink_1')
        self.lres1 = Gst.Pad.link(self.srcpad1, self.sinkpad1)
    
        # get an RTCP srcpad for sending RTCP back to the sender
        self.srcpad1 = Gst.Element.get_request_pad(self.rtpbin, 'send_rtcp_src_1')
        self.sinkpad1 = Gst.Element.get_static_pad(self.rtcpsink1, 'sink')
        self.lres1 = Gst.Pad.link(self.srcpad1, self.sinkpad1)
        self.rtpbin.connect('pad-added', pad_added_cb, self.videodepay1)
        self.rtpbin.connect('pad-added', pad_added_cb, self.videodepay0)


###################AUDIO######################################
        self.rtpsrc2 = Gst.ElementFactory.make('udpsrc', 'rtpsrc2')
        self.rtpsrc2.set_property('port', RTP_RECV_PORT2)
    
        # we need to set caps on the udpsrc for the RTP data
        
        self.rtpsrc2.set_property('caps', self.audio_caps)
    
        self.rtcpsrc2 = Gst.ElementFactory.make('udpsrc', 'rtcpsrc2')
        self.rtcpsrc2.set_property('port', RTCP_RECV_PORT2)

        self.rtcpsink2 = Gst.ElementFactory.make('udpsink', 'rtcpsink2')
        self.rtcpsink2.set_property('port', RTCP_SEND_PORT2)
        self.rtcpsink2.set_property('host', DEST)
    
        # no need for synchronisation or preroll on the RTCP sink
        self.rtcpsink2.set_property('async', False)
        self.rtcpsink2.set_property('sync', False)
        self.player.add(self.rtpsrc2, self.rtcpsrc2, self.rtcpsink2)


        self.srcpad2 = Gst.Element.get_static_pad(self.rtpsrc2, 'src')
        self.sinkpad2 = Gst.Element.get_request_pad(self.rtpbin, 'recv_rtp_sink_2')
        self.lres2 = Gst.Pad.link(self.srcpad2, self.sinkpad2)
    
        # get an RTCP sinkpad in session 0
        self.srcpad2 = Gst.Element.get_static_pad(self.rtcpsrc2, 'src')
        self.sinkpad2 = Gst.Element.get_request_pad(self.rtpbin, 'recv_rtcp_sink_2')
        self.lres2 = Gst.Pad.link(self.srcpad2, self.sinkpad2)
    
        # get an RTCP srcpad for sending RTCP back to the sender
        self.srcpad2 = Gst.Element.get_request_pad(self.rtpbin, 'send_rtcp_src_2')
        self.sinkpad2 = Gst.Element.get_static_pad(self.rtcpsink2, 'sink')
        self.lres2 = Gst.Pad.link(self.srcpad2, self.sinkpad2)
        self.rtpbin.connect('pad-added', pad_added_cb, self.audiodepay0)


############### DECODER ######################################
        self.decoder0 = Gst.ElementFactory.make('jpegdec', "decoder0")
        if not self.decoder0:
            print("ERROR: Could not create decoder0.")
            sys.exit(1)

        self.decoder1 = Gst.ElementFactory.make('jpegdec', "decoder1")
        if not self.decoder1:
            print("ERROR: Could not create decoder1.")
            sys.exit(1)

################## AUDIO_DECODER ############################
        self.decoder2 = Gst.ElementFactory.make('speexdec', "decoder2")
        if not self.decoder2:
            print("ERROR: Could not create decoder2.")
            sys.exit(1)

        self.audioconvert0 = Gst.ElementFactory.make("audioconvert", "audioconvert0")
        if not self.audioconvert0:
            print("ERROR: Could not create audioconvert0.")
            sys.exit(1)

        self.autoaudiosink0 = Gst.ElementFactory.make("autoaudiosink", "autoaudiosink0")
        if not self.autoaudiosink0:
            print("ERROR: Could not create autoaudiosink0.")
            sys.exit(1)
       
######################### GLUPLOAD ###########################


        self.glupload0 = Gst.ElementFactory.make('glupload', "glupload0")
        if not self.glupload0:
            print("ERROR: Could not create glupload0.")
            sys.exit(1)


        self.glupload1 = Gst.ElementFactory.make('glupload', "glupload1")
        if not self.glupload1:
            print("ERROR: Could not create glupload1.")
            sys.exit(1)    
            

######################## GLCOLORCONVERT ############################
        self.glcolorconvert0 = Gst.ElementFactory.make("glcolorconvert", "glcolorconvert0")
        if not self.glcolorconvert0:
            print("ERROR: Could not create glcolorconvert0.")
            sys.exit(1)


        self.glcolorconvert1 = Gst.ElementFactory.make("glcolorconvert", "glcolorconvert1")
        if not self.glcolorconvert1:
            print("ERROR: Could not create glcolorconvert1.")
            sys.exit(1)

######################### SINK ###########################
               
        self.sink = Gst.ElementFactory.make('glimagesink', "video-output")
        if not self.sink:
            print("ERROR: Could not create sink.")
            sys.exit(1)
            
######################### VIDEOMIXER ##################################
        self.videomixer = Gst.ElementFactory.make("glvideomixer", "videomixer")
        if not self.videomixer:
            print("ERROR: Could not create videomixer.")
            sys.exit(1)      

        
        self.videomixer.set_property("background", 1)
        self.videomixer.set_property("async-handling", 1)
        self.videomixer.set_property("message-forward", 1)

        self.mixer_sink_pad0 = self.videomixer.get_request_pad("sink_%u")
        self.mixer_sink_pad0.set_property("xpos", WIDTH/2)
        self.mixer_sink_pad0.set_property("ypos", 0)
        self.mixer_sink_pad0.set_property("width", WIDTH/2)
        self.mixer_sink_pad0.set_property("height", HEIGHT)


        self.mixer_sink_pad1 = self.videomixer.get_request_pad("sink_%u")
        self.mixer_sink_pad1.set_property("xpos", 0)
        self.mixer_sink_pad1.set_property("ypos", 0)
        self.mixer_sink_pad1.set_property("width", WIDTH/2)
        self.mixer_sink_pad1.set_property("height", HEIGHT)


########################## SHADER #####################################
        self.glshader = Gst.ElementFactory.make("glshader", "glshader")
        self.glshader.set_property("vertex", self.simple_vertex_shader_str_gles2)
        self.glshader.set_property("fragment", self.distortion_fragment_shader)

####################### FILTERAPP ####################################
        
        self.glfilterapp0 = Gst.ElementFactory.make("glfilterapp", "glfilterapp0")

        self.glfilterapp0.connect("client-draw", draw_callback0)

        self.glfilterapp1 = Gst.ElementFactory.make("glfilterapp", "glfilterapp1")
        
        self.glfilterapp1.connect("client-draw", draw_callback1)

##################################################################        
        self.player.add(self.videodepay0)
        self.player.add(self.decoder0)
        self.player.add(self.glupload0)
        self.player.add(self.glcolorconvert0)
        self.player.add(self.glfilterapp0)
        self.player.add(self.videodepay1)
        self.player.add(self.decoder1)
        self.player.add(self.glupload1)
        self.player.add(self.glcolorconvert1)
        self.player.add(self.glfilterapp1)
        self.player.add(self.videomixer)
        self.player.add(self.glshader)        
        self.player.add(self.sink)

        self.player.add(self.decoder2)
        self.player.add(self.audioconvert0)        
        self.player.add(self.autoaudiosink0)


    
    def link_element(self):
        link_ok = self.videodepay0.link(self.decoder0)
        if not link_ok:
            print("ERROR: Could not link videodepay0 with decoder0.")
            sys.exit(1)
        link_ok = self.decoder0.link(self.glupload0)
        if not link_ok:
            print("ERROR: Could not link decoder0 with glupload0.")
            sys.exit(1)
        link_ok = self.glupload0.link(self.glcolorconvert0)
        if not link_ok:
            print("ERROR: Could not link glupload0 with glcolorconvert0.")
            sys.exit(1)
        link_ok = self.glcolorconvert0.link(self.glfilterapp0)
        if not link_ok:
            print("ERROR: Could not link glcolorconvert0 with glfilterapp0.")
            sys.exit(1)
        
            

        self.source0_src_pad = self.glfilterapp0.get_static_pad("src")
        link_ok = self.source0_src_pad.link(self.mixer_sink_pad0)
        print (link_ok)

        

        link_ok = self.videodepay1.link(self.decoder1)
        if not link_ok:
            print("ERROR: Could not link videodepay1 with decoder1.")
            sys.exit(1)
        link_ok = self.decoder1.link(self.glupload1)
        if not link_ok:
            print("ERROR: Could not link decoder1 with glupload1.")
            sys.exit(1)
        link_ok = self.glupload1.link(self.glcolorconvert1)
        if not link_ok:
            print("ERROR: Could not link glupload1 with glcolorconvert1.")
            sys.exit(1)
        link_ok = self.glcolorconvert1.link(self.glfilterapp1)
        if not link_ok:
            print("ERROR: Could not link glcolorconvert1 with glfilterapp1.")
            sys.exit(1)

        self.source1_src_pad = self.glfilterapp1.get_static_pad("src")
        link_ok = self.source1_src_pad.link(self.mixer_sink_pad1)
        print (link_ok)
            
        link_ok = self.videomixer.link(self.glshader)
        if not link_ok:
            print("ERROR: Could not link videomixer with glshader.")
            sys.exit(1)

        link_ok = self.glshader.link(self.sink)
        if not link_ok:
            print("ERROR: Could not link glshader with sink.")
            sys.exit(1)

#########################################################
        link_ok = self.audiodepay0.link(self.decoder2)
        if not link_ok:
            print("ERROR: Could not link audiodepay0 with decoder2.")
            sys.exit(1)
        link_ok = self.decoder2.link(self.audioconvert0)
        if not link_ok:
            print("ERROR: Could not link decoder2 with audioconvert0.")
            sys.exit(1)
        link_ok = self.audioconvert0.link(self.autoaudiosink0)
        if not link_ok:
            print("ERROR: Could not link audioconvert0 with autoaudiosink0.")
            sys.exit(1)
        



