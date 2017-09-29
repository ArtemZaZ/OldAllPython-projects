from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pygame


def loadImageStr ( fileName ):
    image1  = pygame.image.load( fileName )
    imagestr = pygame.image.tostring(image1, "RGBA")
    return imagestr


def load_png_texture( fileName, pixelx, pixely ):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GEQUAL, 0.4)

    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE )
    textureImage = loadImageStr(fileName )

    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    texture=4
    print(texture)

    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, pixelx, pixely, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureImage)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    print(texture)
    return texture

a=load_png_texture("kompas.png", 900, 800)
print(a)
