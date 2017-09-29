import time
import math
import RTCvideo


IP = '127.0.0.1'
RTP_RECV_PORT0 = 5000
RTCP_RECV_PORT0 = 5001
RTCP_SEND_PORT0 = 5005





video=RTCvideo.Video(IP, RTP_RECV_PORT0, RTCP_RECV_PORT0, RTCP_SEND_PORT0)
video.draw_overlay("ring.png", x = 0, y = 0, scale_x = 0.6, scale_y = 0.8)


print("I started")
video.start()

time.sleep(1000)

video.stop()
print("I stopped")

time.sleep(1)

video.start()
print("I started")

time.sleep(10)

video.paused()
print("I paused")

time.sleep(10)

print("I started")
video.start()

time.sleep(10)

video.stop()
print("I stopped")


