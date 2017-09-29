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

DEST = '127.0.0.1'
#DEST = '192.168.42.162'

RTP_RECV_PORT0 = 5000
RTCP_RECV_PORT0 = 5001
RTCP_SEND_PORT0 = 5005

RTP_RECV_PORT1 = 6000
RTCP_RECV_PORT1 = 6001
RTCP_SEND_PORT1 = 6005
VIDEO_CAPS="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)JPEG,payload=(int)26,ssrc=(uint)1006979985,clock-base=(uint)312170047,seqnum-base=(uint)3174"
Gst.init(sys.argv)


player = Gst.Pipeline.new("player")

#dvdemux = Gst.ElementFactory.make("qtdemux", "dvdemux")
#q1 = Gst.ElementFactory.make("queue", "q1")

pulsesrc0 = Gst.ElementFactory.make('pulsesrc', "pulsesrc0")
if not pulsesrc0:
    print("ERROR: Could not create pulsesrc0.")
    sys.exit(1)
 
#pulsesrc0.set_property('stream-properties', "audio/x-raw,clock-rate=8000,format=S16LE")


audio_caps=Gst.caps_from_string(AUDIO_CAPS)
#self.pulsesrc0.set_property('device', self.audio_caps)
        

speexenc0 = Gst.ElementFactory.make('speexenc', "speexenc0")
if not speexenc0:
    print("ERROR: Could not create speexenc0.")
    sys.exit(1)

rtpspeexpay0 = Gst.ElementFactory.make('rtpspeexpay', "rtpspeexpay0")
if not rtpspeexpay0:
    print("ERROR: Could not create rtpspeexpay0.")
    sys.exit(1)

rtpbin = Gst.ElementFactory.make('rtpbin', 'rtpbin')






            



audpsink_rtpout = Gst.ElementFactory.make("udpsink", "audpsink_rtpout")
audpsink_rtpout.set_property('host', DEST)
audpsink_rtpout.set_property('port', 7000)
 

audpsink_rtcpout = Gst.ElementFactory.make("udpsink", "audpsink_rtcpout")
audpsink_rtcpout.set_property('host', DEST)
audpsink_rtcpout.set_property('port', 7001)
audpsink_rtcpout.set_property('sync', False)
audpsink_rtcpout.set_property('async', False)

 

audpsrc_rtcpin = Gst.ElementFactory.make("udpsrc", "audpsrc_rtcpin")
audpsrc_rtcpin.set_property('port', 7005)

#player.add(dvdemux)
#player.add(q1)
player.add(rtpbin)
player.add(pulsesrc0)
player.add(speexenc0)        
player.add(rtpspeexpay0)
player.add(audpsink_rtpout)
player.add(audpsink_rtcpout)
player.add(audpsrc_rtcpin)

rtpspeexpay0.link_pads('src', rtpbin, 'send_rtp_sink_2')
rtpbin.link_pads('send_rtp_src_2', audpsink_rtpout, 'sink')
rtpbin.link_pads('send_rtcp_src_2', audpsink_rtcpout, 'sink')
audpsrc_rtcpin.link_pads('src', rtpbin, 'recv_rtcp_sink_2')


"""
def dvdemux_padded(demuxer, pad):

    #print "Demux_Callback entry: "+str(pad.get_name())

    if pad.get_name() == "video_0":

        print ("Video Template")

        qv_pad = q1.get_static_pad("sink")

        pad.link(qv_pad)

    elif pad.get_name() == "audio_0":

        print ("Audio Template")

        qa_pad = q2.get_static_pad("sink")

        pad.link(qa_pad)

    else:

        print ("Template: "+str(pad.get_property("template").name_template))"""

#dvdemux.connect('pad-added', dvdemux_padded)



link_ok = pulsesrc0.link(speexenc0)
if not link_ok:
    print("ERROR: Could not link videodepay1 with decoder1.")
    sys.exit(1)
    
link_ok = speexenc0.link(rtpspeexpay0)
if not link_ok:
    print("ERROR: Could not link decoder1 with glupload1.")
    sys.exit(1)
            
player.set_state(Gst.State.PLAYING)


while(True):
    time.sleep(1)
    


