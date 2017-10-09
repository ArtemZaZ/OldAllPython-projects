import gi
import sys
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

DEST = '127.0.0.1'
init_GL_flag = False

RTP_RECV_PORT0 = 5000
RTCP_RECV_PORT0 = 5001
RTCP_SEND_PORT0 = 5005

RTP_RECV_PORT1 = 6000
RTCP_RECV_PORT1 = 6001
RTCP_SEND_PORT1 = 6005
VIDEO_CAPS="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)JPEG,payload=(int)26,ssrc=(uint)1006979985,clock-base=(uint)312170047,seqnum-base=(uint)3174"



def loadImageStr ( fileName ):
    glEnable(GL_TEXTURE_2D)
    image  = Image.open ( fileName )
    width  = image.size [0]
    height = image.size [1]
    image  = image.tobytes( "raw", "RGBA", 0, -1 )   
    return (width, height, image)

class texture_block():
    def __init__(self):
        self.texture=0
        self.path_to_image=None
        self.image=''
        self.pixel_x=0
        self.pixel_y=0
        self.vertexcoord1 = [ -1.0, -1.0]
        self.vertexcoord2 = [ -1.0, 1.0]
        self.vertexcoord3 = [ 1.0, 1.0]
        self.vertexcoord4 = [ 1.0, -1.0]
        self.Transparent = False
        self.scale_x=1.0
        self.scale_y=1.0

    def set_image(self, path):
        self.path_to_image=path
        temp=loadImageStr(self.path_to_image)
        self.pixel_x=temp[0]
        self.pixel_y=temp[1]
        self.image=temp[2]
        

    def gen_texture(self):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GEQUAL, 0.4)

        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE )
        

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        self.texture=glGenTextures(1)
        
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, 4, self.pixel_x, self.pixel_y, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.image)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    def get_texture(self):
        return texture
    
    def set_vertexcoord(self, x1,x2,x3,x4):
        self.vertexcoord1 = x1
        self.vertexcoord2 = x2
        self.vertexcoord3 = x3
        self.vertexcoord4 = x4

    def set_scale(self, x,y,scale_x,scale_y):
        self.scale_x=scale_x
        self.scale_y=scale_y
        


TEXTURE0=texture_block()



def read_shader_fromfile(filename):
    file=open(filename, "r")
    shaderstr=file.read()
    file.close()
    return shaderstr



def initGL ():
    global TEXTURE0
    
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GEQUAL, 0.4)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    if(TEXTURE0.pixel_x*TEXTURE0.pixel_x>0):
        TEXTURE0.gen_texture()
        if( TEXTURE0.texture ==0):        
            print("ERROR: Gen texture\n")

    
        
    
    
    
def draw_callback0(GST_object, width, height, texture):    
    global init_GL_flag
    global TEXTURE0

    Scale=float(width)/float(height)
    if not init_GL_flag:
        initGL()
        glutInit(sys.argv)    
        init_GL_flag = True
    k=(float(width)/(2.0*Scale))
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_TEXTURE_2D)
    glMatrixMode   ( GL_PROJECTION )
    glLoadIdentity ()
    gluPerspective ( 90.0, Scale, 1.0, 200.0 )
    glMatrixMode   ( GL_MODELVIEW )
    glLoadIdentity ()

    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)
                
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-1.0*Scale, -1.0, -1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0*Scale,  1.0, -1.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( 1.0*Scale,  1.0, -1.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( 1.0*Scale, -1.0, -1.0)
    glEnd()
     
                
        
    if(TEXTURE0.texture!=0):
        if(TEXTURE0.Transparent==True):     
            glBindTexture(GL_TEXTURE_2D, TEXTURE0.texture)
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(-1.0*Scale, -1.0, -1.0)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(-1.0*Scale,  1.0, -1.0)
            glTexCoord2f(1.0, 1.0)
            glVertex3f( 1.0*Scale,  1.0, -1.0)
            glTexCoord2f(1.0, 0.0)
            glVertex3f( 1.0*Scale, -1.0, -1.0)
            glEnd()
        else:
            x1=(TEXTURE0.vertexcoord1[0]/k)-1.0*Scale
            y1=(TEXTURE0.vertexcoord1[1]/k)-1.0
            x2=(TEXTURE0.vertexcoord2[0]/k)-1.0*Scale
            y2=(TEXTURE0.vertexcoord2[1]/k)-1.0
            x3=(TEXTURE0.vertexcoord3[0]/k)-1.0*Scale
            y3=(TEXTURE0.vertexcoord3[1]/k)-1.0
            x4=(TEXTURE0.vertexcoord4[0]/k)-1.0*Scale
            y4=(TEXTURE0.vertexcoord4[1]/k)-1.0



            x1=(TEXTURE0.vertexcoord1[0]/k)-1.0*Scale
            y1=(TEXTURE0.vertexcoord1[1]/k)-1.0
            x2=(TEXTURE0.vertexcoord2[0]/k)-1.0*Scale
            y2=(TEXTURE0.vertexcoord2[1]/k)-1.0
            x3=(TEXTURE0.vertexcoord3[0]/k)-1.0*Scale
            y3=(TEXTURE0.vertexcoord3[1]/k)-1.0
            x4=(TEXTURE0.vertexcoord4[0]/k)-1.0*Scale
            y4=(TEXTURE0.vertexcoord4[1]/k)-1.0    
            
            glBindTexture(GL_TEXTURE_2D, TEXTURE0.texture)
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(x1, y1, -1.0)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(x2, y2, -1.0)
            glTexCoord2f(1.0, 1.0)
            glVertex3f(x3, y3, -1.0)
            glTexCoord2f(1.0, 0.0)
            glVertex3f(x4, y4, -1.0)
            glEnd()
            
    return True
    


class Video:

    
    
    def delete_event(self, widget, event, data=None):
        Gtk.main_quit()
        return False

   
    
    def __init__(self, IP, RTP_RECV_PORT, RTCP_RECV_PORT, RTCP_SEND_PORT, overlay=draw_callback0):
        Gst.init(sys.argv)
        
        glutInit(sys.argv)
        
        GObject.threads_init()
        
        GLib.setenv("GST_GL_API", "opengl", False)
        self.VIDEO_CAPS="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)JPEG,payload=(int)26,ssrc=(uint)1006979985,clock-base=(uint)312170047,seqnum-base=(uint)3174"
        self.IP=IP
        self.RTP_RECV_PORT0=RTP_RECV_PORT
        self.RTCP_RECV_PORT0=RTCP_RECV_PORT
        self.RTCP_SEND_PORT0=RTCP_SEND_PORT
        self.init_GL_flag=False
        self.drawcall=overlay
        self.PAUSED=False
        
        self.texture0=0

        
    
        

    def start(self):
        if(self.PAUSED==True):
            self.player.set_state(Gst.State.PLAYING)
            self.PAUSED=False
        else:
            global init_GL_flag
            self.init_element()
            self.link_element()
            init_GL_flag=False
            self.player.set_state(Gst.State.READY)
            self.player.set_state(Gst.State.PAUSED)
            self.player.set_state(Gst.State.PLAYING)

    def paused(self):
        self.player.set_state(Gst.State.PAUSED)
        self.PAUSED=True

    def stop(self):
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

 
    
    def draw_overlay(self, path, x =  0, y = 0, scale_x=1.0, scale_y=1.0, Transparent=False):
        global TEXTURE0
        TEXTURE0.set_image(path)
        #vertexcoord1=[x, y]
        #vertexcoord2=[x+width, y]
        #vertexcoord3=[x+width, y+height]
        #vertexcoord4=[x, y+height]
        #TEXTURE0.set_vertexcoord(vertexcoord1, vertexcoord2, vertexcoord3, vertexcoord4)

        vertexcoord1=[x, y]
        vertexcoord2=[x+int(scale_x*TEXTURE0.pixel_x), y]
        vertexcoord3=[x+int(scale_x*TEXTURE0.pixel_x), y+int(scale_y*TEXTURE0.pixel_x)]
        vertexcoord4=[x, y+int(scale_y*TEXTURE0.pixel_x)]
        TEXTURE0.set_vertexcoord(vertexcoord1, vertexcoord2, vertexcoord3, vertexcoord4)
        TEXTURE0.Transparent=Transparent
            
    
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

        ################  SOURCE  ##################################        
        
            
        self.rtpbin = Gst.ElementFactory.make('rtpbin', 'rtpbin')
        self.player.add(self.rtpbin)
        self.caps = Gst.caps_from_string(self.VIDEO_CAPS)
        
        def pad_added_cb(rtpbin, new_pad, depay):
            sinkpad = Gst.Element.get_static_pad(depay, 'sink')
            lres = Gst.Pad.link(new_pad, sinkpad)        
        
       
        self.rtpsrc0 = Gst.ElementFactory.make('udpsrc', 'rtpsrc0')
        self.rtpsrc0.set_property('port', self.RTP_RECV_PORT0)
    
        # we need to set caps on the udpsrc for the RTP data
        
        self.rtpsrc0.set_property('caps', self.caps)
    
        self.rtcpsrc0 = Gst.ElementFactory.make('udpsrc', 'rtcpsrc0')
        self.rtcpsrc0.set_property('port', self.RTCP_RECV_PORT0)

        self.rtcpsink0 = Gst.ElementFactory.make('udpsink', 'rtcpsink0')
        self.rtcpsink0.set_property('port', self.RTCP_SEND_PORT0)
        self.rtcpsink0.set_property('host', self.IP)
    
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

    
        self.rtpbin.set_property('drop-on-latency', True)
        self.rtpbin.set_property('buffer-mode', 1)


        self.rtpbin.connect('pad-added', pad_added_cb, self.videodepay0)


############### DECODER ######################################
        self.decoder0 = Gst.ElementFactory.make('jpegdec', "decoder0")
        if not self.decoder0:
            print("ERROR: Could not create decoder0.")
            sys.exit(1)

       
            
######################### GLUPLOAD ###########################
        self.glupload0 = Gst.ElementFactory.make('glupload', "glupload0")
        if not self.glupload0:
            print("ERROR: Could not create glupload0.")
            sys.exit(1)


       

######################## GLCOLORCONVERT ############################
        self.glcolorconvert0 = Gst.ElementFactory.make("glcolorconvert", "glcolorconvert0")
        if not self.glcolorconvert0:
            print("ERROR: Could not create glcolorconvert0.")
            sys.exit(1)


        

######################### CAPS AND SINK ###########################
               
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
        self.mixer_sink_pad0.set_property("xpos", 0)
        self.mixer_sink_pad0.set_property("ypos", 0)
        
        #self.mixer_sink_pad0.set_property("width", 1280)
        #self.mixer_sink_pad0.set_property("height", 720)



######################## FILTERAPP ####################################
        
        self.glfilterapp0 = Gst.ElementFactory.make("glfilterapp", "glfilterapp0")

        self.glfilterapp0.connect("client-draw", self.drawcall)


##################################################################        
        self.player.add(self.videodepay0)
        self.player.add(self.decoder0)
        self.player.add(self.glupload0)
        self.player.add(self.glcolorconvert0)
        self.player.add(self.glfilterapp0)
        self.player.add(self.videomixer)
        
        self.player.add(self.sink)

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
        self.source0_src_pad.link(self.mixer_sink_pad0)
        
        link_ok = self.videomixer.link(self.sink)
        if not link_ok:
            print("ERROR: Could not link glshader with sink.")
            sys.exit(1)

        





    



        

