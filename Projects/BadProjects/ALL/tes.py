import pygame
import time

q = pygame.time.Clock()


pygame.init()
pygame.event.set_blocked()
#pygame.time.set_timer(pygame.USEREVENT, 1)
print(pygame.event.get())
time.sleep(1)
print(pygame.event.get())
time.sleep(1)

print(pygame.event.get())
time.sleep(1)

pygame.quit()

