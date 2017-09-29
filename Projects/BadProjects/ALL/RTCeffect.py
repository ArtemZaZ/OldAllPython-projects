from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def draw_rectangle(size):
    glBegin(GL_QUADS)
    glVertex3f(-size, 0.0, -1.0)
    glVertex3f(-size,  size, -1.0)
    glVertex3f( 0.0,  size, -1.0)
    glVertex3f( 0.0, 0.0, -1.0)
    glEnd()

def draw_wire_rectangle(size):
    glBegin(GL_LINES)
    glVertex3f(-size, 0.0, -1.0)
    glVertex3f(-size,  size, -1.0)
    
    glVertex3f(-size,  size, -1.0)
    glVertex3f( 0.0,  size, -1.0)    

    glVertex3f( 0.0,  size, -1.0)
    glVertex3f( 0.0, 0.0, -1.0)

    glVertex3f( 0.0, 0.0, -1.0)
    glVertex3f(-size, 0.0, -1.0)
    glEnd()

def draw_number(number, size, texture):
    
    H=0.3
    W=0.23
    dH=0.03
    dW=0.035
    textur_coord=[0, 0, 0, 0]
    if(number==1):
        textur_coord[0]=0.0
        textur_coord[1]=1.0-(H)-0.025
        textur_coord[2]=W
        textur_coord[3]=H
    if(number==2):
        textur_coord[0]=0.0+(W+dW)
        textur_coord[1]=1.0-(H)-0.025
        textur_coord[2]=W
        textur_coord[3]=H
    if(number==3):
        textur_coord[0]=0.0+2*(W+dW)
        textur_coord[1]=1.0-(H)-0.02
        textur_coord[2]=W
        textur_coord[3]=H
    if(number==4):
        textur_coord[0]=0.0+3*(W+dW)
        textur_coord[1]=1.0-(H)-0.02
        textur_coord[2]=W
        textur_coord[3]=H

    if(number==5):
        textur_coord[0]=0.0
        textur_coord[1]=1.0-2*(H+dH)
        textur_coord[2]=W
        textur_coord[3]=H
    if(number==6):
        textur_coord[0]=0.0+(W+dW)
        textur_coord[1]=1.0-2*(H+dH)
        textur_coord[2]=W
        textur_coord[3]=H
    if(number==7):
        textur_coord[0]=0.0+2*(W+dW)
        textur_coord[1]=1.0-2*(H+dH)
        textur_coord[2]=W
        textur_coord[3]=H
    if(number==8):
        textur_coord[0]=0.0+3*(W+dW)
        textur_coord[1]=1.0-2*(H+dH)
        textur_coord[2]=W
        textur_coord[3]=H

    if(number==9):
        textur_coord[0]=0.0+(W+dW)-0.02
        textur_coord[1]=1.0-3*(H+dH)-0.01
        textur_coord[2]=W
        textur_coord[3]=H

    if(number==0):
        textur_coord[0]=0.0+2*(W+dW)
        textur_coord[1]=1.0-3*(H+dH)-0.01
        textur_coord[2]=W
        textur_coord[3]=H

    if(number==10):
        textur_coord[0]=0.0
        textur_coord[1]=1.0-3*(H+dH)
        textur_coord[2]=W
        textur_coord[3]=H

        
    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)
    
    glTexCoord2f(textur_coord[0], textur_coord[1])
    
    glVertex3f(0.0, 0.0+size, 0.0)
    
    glTexCoord2f(textur_coord[0], textur_coord[1]+textur_coord[3])
    glVertex3f(0.0, 0.0, 0.0)
    glTexCoord2f(textur_coord[0]+textur_coord[2], textur_coord[1]+textur_coord[3])
    glVertex3f(0.0+size, 0.0, 0.0)
    glTexCoord2f(textur_coord[0]+textur_coord[2], textur_coord[1])
    glVertex3f(0.0+size, 0.0+size, 0.0)
    glEnd()
    

class Speedometr():
    def __init__(self, coord=[0,0,0], size=0.1):
        self.motor_power=0
        self.coord=coord
        self.num=10
        self.drawing_num=0
        self.size=size

    def set_motor_power(self, power):
        self.motor_power=power

    def calculate(self):
        self.drawing_num=( self.motor_power // (self.num-4))

    def draw_speedometr(self):
        i=0
        glDisable(GL_TEXTURE_2D)
        self.calculate()
        glPushMatrix()
        glTranslate(self.coord[0], self.coord[1], self.coord[2])
        while(i<self.num):
            if (i<self.drawing_num):
                if(i<(self.num-2)):                    
                    if(i<(self.num-5)):
                        glColor4f(0.0, 1.0, 0.0, 1.0)    
                        #glutWireCube( 1.0 )
                        draw_rectangle(self.size)
                    else:
                        glColor4f(1.0, 1.0, 0.0, 1.0)    
                        #glutWireCube( 1.0 )
                        draw_rectangle(self.size)
                
                else:
                    glColor4f(1.0, 0.0, 0.0, 1.0)    
                    #glutSolidCube( 1.0 )
                    draw_rectangle(self.size)
            else:
                if(i<(self.num-2)):                    
                    if(i<(self.num-5)):
                        glColor4f(0.0, 1.0, 0.0, 1.0)    
                        #glutWireCube( 1.0 )
                        draw_wire_rectangle(self.size)
                    else:
                        glColor4f(1.0, 1.0, 0.0, 1.0)    
                        #glutWireCube( 1.0 )
                        draw_wire_rectangle(self.size)
                        
                else:
                    glColor4f(1.0, 0.0, 0.0, 1.0)    
                    #glutWireCube( 1.0 )
                    draw_wire_rectangle(self.size)

            i=i+1
            glTranslate(0.0, -(self.size+self.size*0.2), 0.0)
        glPopMatrix()
        glEnable(GL_TEXTURE_2D)

class Number_Spedometr():
    def __init__(self, coord, size):
        self.motor_power=0.0
        self.coord=coord
        self.revers=False
        self.draw_mass=[0,0,0]
        self.size=size

    def set_motor_power(self, power):
        self.motor_power = abs(power)
        if(power<0):
            self.revers=True
        else:
            self.revers=False
        self.draw_mass[2] = int(self.motor_power % 10)
        self.draw_mass[1] = int((self.motor_power//10)%10)
        self.draw_mass[0] = int((self.motor_power//100)%10)
        
    def draw_num_speedometr(self, texture):
        glPushMatrix()
        glTranslate(self.coord[0], self.coord[1], self.coord[2])
        if(self.revers):
            draw_number(10, self.size, texture)
        glTranslate(self.size, 0.0, 0.0)
        draw_number(self.draw_mass[0], self.size, texture)
        glTranslate(self.size, 0.0, 0.0)
        draw_number(self.draw_mass[1], self.size, texture)
        glTranslate(self.size, 0.0, 0.0)
        draw_number(self.draw_mass[2], self.size, texture)
        glPopMatrix()
            
            
         
