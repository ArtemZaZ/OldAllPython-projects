import gi
import sys
import time
gi.require_version("Gst", "1.0")
gi.require_version("Gtk", "3.0")
import math
from gi.repository import Gst, GObject, GLib
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

initGLflag = False  # флаг инициализации opengl, все что связано с opengl в gstreamer должно быть определено глобально, т.к. когда кидаем функцию drawcallback в gst, сама ф-ия исполняется в gst модуле, который видит только глобальное пр-во имен, т.е. функцию drawcallback в класс не запихнешь

def loadImageStr ( fileName ):      # загружает изображение из файла(в формате png)
    glEnable(GL_TEXTURE_2D)
    image  = Image.open ( fileName )
    width  = image.size [0]
    height = image.size [1]
    image  = image.tobytes( "raw", "RGBA", 0, -1 )
    return (width, height, image)   # возвращает кортеж из ширины, высоты изображения и самого изображения

class textureBlock():
    def __init__(self):
        self.texture=0                      # сама текстура
        self.pathImage=None                 # путь до изображени    
        self.image=''                       # изображение
        self.pixelX=0                       # количество пикселей по x
        self.pixelY=0                       # количество пикселей по y
        self.vertexcoord1 = [ -1.0, -1.0]   # координаты отрисовки в opengl
        self.vertexcoord2 = [ -1.0, 1.0]
        self.vertexcoord3 = [ 1.0, 1.0]
        self.vertexcoord4 = [ 1.0, -1.0]
        self.Transparent = False            # флаг показывающий во весь ли экран растягивается изображение

    def setImage(self, path):               # загрузить изображение
        self.pathImage=path
        temp=loadImageStr(self.pathImage)
        self.pixelX=temp[0]
        self.pixelY=temp[1]
        self.image=temp[2]
        

    def createTexture(self):        # генерация текстуры
        glEnable(GL_TEXTURE_2D)     # разрешить использовать текстуры
        glEnable(GL_BLEND)          # включить смешивание
        glEnable(GL_ALPHA_TEST)     # разрешить прозрачность
        glAlphaFunc(GL_GEQUAL, 0.4) # не пропускать прозрачность ниже 0.4
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)        # один из видов смешивания, подробнее читать в интернете
        glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE )     
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        self.texture=glGenTextures(1)        # создать дескриптор текстуры
        glBindTexture(GL_TEXTURE_2D, self.texture)  # связать тектуру с внутренним буффером текстур
        glTexImage2D(GL_TEXTURE_2D, 0, 4, self.pixelX, self.pixelY, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.image) # создание текстуры из изображения
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP) # некоторые параметры текстуры
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    def getTexture(self): # возвращает текстуру
        return texture
    
    def setVertexcoord(self, x1,x2,x3,x4):  # установить координаты отрисовки текстурного блока(текстура будет масштабироваться по ним)
        self.vertexcoord1 = x1
        self.vertexcoord2 = x2
        self.vertexcoord3 = x3
        self.vertexcoord4 = x4

    def setPositionAndScale(self,x, y, scale_x, scale_y): # установить позицию и масштаб изображения
        self.vertexcoord1=[x, y]
        self.vertexcoord2=[x+int(scale_x*self.pixelX), y]
        self.vertexcoord3=[x+int(scale_x*self.pixelX), y+int(scale_y*self.pixelY)]
        self.vertexcoord4=[x, y+int(scale_y*self.pixelY)]
        


TEXTURE0=textureBlock()                 # текстура, накладываемая на видео

def initGL():
    #global TEXTURE0    
    glClearColor(0.0, 0.0, 0.0, 0.0)    # очистка экрана
    #glEnable(GL_DEPTH_TEST)             # включить глубину
    glEnable(GL_BLEND)                  # включить смешивание
    glEnable(GL_ALPHA_TEST)             # включить прозрачность
    glAlphaFunc(GL_GEQUAL, 0.4)         # не пропускать прозрачность ниже 0.4
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # один из видов смешивания, подробнее читать в интернете
    if(TEXTURE0.pixelX*TEXTURE0.pixelY>0): # если размер изображения не ноль
        TEXTURE0.createTexture()           # создать текстуру    
        if( TEXTURE0.texture == 0):        # если текстура равна нулю 
            print("ERROR: Gen texture\n")   
    
    
def draw_callback0(GST_object, width, height, texture):    # не исправлено до конца
    global initGLflag   
    global TEXTURE0   

    Scale=float(width)/float(height)        # масштабирование
    if not initGLflag:                      # если контекст opengl еще не проинициализирован
        initGL()                            # инициализацию нужно производить именно сдесь, т.к. только эта ф-ия будет исполняться в модуле gst, собственно она и инициализирует opengl в нем
        glutInit(sys.argv)    
        initGLflag = True
    k=(float(width)/(2.0*Scale))            
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Очистить цветовой и глубинный буффер
    glEnable(GL_TEXTURE_2D)                             # Разрешить отрисовку тектуры
    glMatrixMode   ( GL_PROJECTION )                    # настройка матриц opengl
    glLoadIdentity ()
    gluPerspective ( 90.0, Scale, 1.0, 200.0 )
    glMatrixMode   ( GL_MODELVIEW )
    glLoadIdentity ()

    glBindTexture(GL_TEXTURE_2D, texture)               # привязать текстуру
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)                              # растянуть текстуру на весь Viewport
    glVertex3f(-1.0*Scale, -1.0, -1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-1.0*Scale,  1.0, -1.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( 1.0*Scale,  1.0, -1.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( 1.0*Scale, -1.0, -1.0)
    glEnd()
     
                
     
    if(TEXTURE0.texture):
        if(TEXTURE0.Transparent):     
            TEXTURE0.setScale(-1.0, -1.0, Scale, 1.0)
        else:            
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
    def __init__(self, IP = '127.0.0.1', RTP_RECV_PORT = 5000, RTCP_RECV_PORT = 5001, RTCP_SEND_PORT = 5005, overlay = draw_callback0):    # ip и порты по умолчанию
        Gst.init(sys.argv)        # Инициализация компонентов           
        glutInit(sys.argv)        
        GObject.threads_init()        
        GLib.setenv("GST_GL_API", "opengl", False)  # включить поддержку старых версий openGL
        self.VIDEO_CAPS="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)JPEG,payload=(int)26,ssrc=(uint)1006979985,clock-base=(uint)312170047,seqnum-base=(uint)3174"    # caps приема
        self.IP=IP              # ip приема
        self.RTP_RECV_PORT0=RTP_RECV_PORT    # Порты приема
        self.RTCP_RECV_PORT0=RTCP_RECV_PORT
        self.RTCP_SEND_PORT0=RTCP_SEND_PORT
        self.drawcall=overlay           # callback функция отрисовки, можно передать свою
        self.PAUSED=False               # Метка паузы, мб потом заменить ее на что-нибудь        
        self.texture0=0

        
    def start(self):    # Запуск видео
        if(self.PAUSED):
            self.player.set_state(Gst.State.PLAYING)    
            self.PAUSED=False
        else:
            global initGLflag
            self.initElement()         # инициализация компонентов
            self.linkElement()         # линковка
            initGLflag=False
            self.player.set_state(Gst.State.READY)
            self.player.set_state(Gst.State.PAUSED)
            self.player.set_state(Gst.State.PLAYING)

    def paused(self):                   # пауза
        self.player.set_state(Gst.State.PAUSED)
        self.PAUSED=True

    def stop(self):                     # остановка и освобождение ресурсов
        self.player.set_state(Gst.State.NULL)
        self.PAUSED=False
        print("STOP")
    
        
    
    def on_error(self, bus, msg):       # прием ошибок
        err, dbg = msg.parse_error()
        print("ERROR:", msg.src.get_name(), ":", err.message)
        if dbg:
            print("Debug info:", dbg)

    
    def on_eos(self, bus, msg):         # ловим конец передачи видео
        print("End-Of-Stream reached")
        self.player.set_state(Gst.State.READY)

 
    
    def draw_overlay(self, path, x =  0, y = 0, scale_x=1.0, scale_y=1.0, Transparent=False):
        global TEXTURE0
        TEXTURE0.setImage(path)
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
     
    
    def initElement(self):       # инициализация компонентов        
        self.player = Gst.Pipeline.new("player")         # создаем pipeline
        if not self.player:
            print("ERROR: Could not create pipeline.")
            sys.exit(1)
            
        self.bus=self.player.get_bus()               # создаем шину передачи сообщений и ошибок от GST
        self.bus.add_signal_watch()
        self.bus.connect("message::error", self.on_error)
        self.bus.connect("message::eos", self.on_eos)

        ################ VIDEODEPAY ################################
        
        self.videodepay0=Gst.ElementFactory.make('rtpjpegdepay', 'videodepay0') # создаем раскпаковщик видео формата jpeg
        if not self.videodepay0:
            print("ERROR: Could not create videodepay0.")
            sys.exit(1)

        ################  SOURCE  ##################################        
        
            
        self.rtpbin = Gst.ElementFactory.make('rtpbin', 'rtpbin')   # создаем rtpbin
        self.player.add(self.rtpbin)                                # добавляем его в Pipeline
        self.caps = Gst.caps_from_string(self.VIDEO_CAPS)           # в каком формате принимать видео

        ### дальше идет очень странная система RTP
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
        self.decoder0 = Gst.ElementFactory.make('jpegdec', "decoder0")       # декодирует jpeg формат
        if not self.decoder0:
            print("ERROR: Could not create decoder0.")
            sys.exit(1)

       
            
######################### GLUPLOAD ###########################
        self.glupload0 = Gst.ElementFactory.make('glupload', "glupload0")    # загрузка в openGL
        if not self.glupload0:
            print("ERROR: Could not create glupload0.")
            sys.exit(1)


       

######################## GLCOLORCONVERT ############################
        self.glcolorconvert0 = Gst.ElementFactory.make("glcolorconvert", "glcolorconvert0") # преобразует цвета в формат цветов openGL
        if not self.glcolorconvert0:
            print("ERROR: Could not create glcolorconvert0.")
            sys.exit(1)


        

######################### CAPS AND SINK ###########################
               
        self.sink = Gst.ElementFactory.make('glimagesink', "video-output")      # окно вывода видео
        if not self.sink:
            print("ERROR: Could not create sink.")
            sys.exit(1)


######################### VIDEOSCALE ##################################
        
        self.videoscale0 = Gst.ElementFactory.make("videoscale", "videoscale0") # растягиваем изображение 
        if not self.videoscale0:
            print("ERROR: Could not create videoscale0.")
            sys.exit(1) 


######################## FILTERAPP ####################################
        
        self.glfilterapp0 = Gst.ElementFactory.make("glfilterapp", "glfilterapp0")      # GL-фильтр, позволяет рисовать
        self.glfilterapp0.connect("client-draw", self.drawcall)             # но у него есть небольшой косяк, если передавать в него переменную или ссылку как-то, то только глобвльную
                                                                            # т.к. нельзя сделать callback-функцию фильтра, которая будет принадлежать классу

##################################################################        
        self.player.add(self.videodepay0)       # добавляем все элементы в pipeline
        self.player.add(self.decoder0)
        self.player.add(self.glupload0)
        self.player.add(self.glcolorconvert0)
        self.player.add(self.glfilterapp0)
        self.player.add(self.videoscale0)
        
        self.player.add(self.sink)

    def linkElement(self):                      # функция линковки элементов
        link_ok = self.videodepay0.link(self.decoder0)
        if not link_ok:
            print("ERROR: Could not link videodepay0 with decoder0.")
            sys.exit(1)
            
        link_ok = self.decoder0.link(self.glupload0)
        if not link_ok:
            print("ERROR: Could not link decoder0 with videoscale0.")
            sys.exit(1)
                        
        link_ok = self.glupload0.link(self.glcolorconvert0)
        if not link_ok:
            print("ERROR: Could not link glupload0 with glcolorconvert0.")
            sys.exit(1)
            
        link_ok = self.glcolorconvert0.link(self.glfilterapp0)
        if not link_ok:
            print("ERROR: Could not link glcolorconvert0 with glfilterapp0.")
            sys.exit(1)
        
        link_ok = self.glfilterapp0.link(self.sink)
        if not link_ok:
            print("ERROR: Could not link videoscale0 with sink.")
            sys.exit(1)

        





    



        

