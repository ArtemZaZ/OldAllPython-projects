import ProbaVideoCV

IP = '127.0.0.1'
RTP_RECV_PORT0 = 5000
RTCP_RECV_PORT0 = 5001
RTCP_SEND_PORT0 = 5005

RTP_RECV_PORT1 = 6000
RTCP_RECV_PORT1 = 6001
RTCP_SEND_PORT1 = 6005

CVG=CVGstreamer(IP, RTP_RECV_PORT0, RTCP_RECV_PORT0, RTCP_SEND_PORT0)

print("I started")
CVG.start()


while True:
    message = CVG.bus.timed_pop_filtered(10000, Gst.MessageType.ANY)
    # print "image_arr: ", image_arr
    if CVG.cvImage is not None:
        gray = cv2.cvtColor(CVG.cvImage, cv2.COLOR_BGR2RGB)
        cv2.imshow("appsink image arr", CVG.cvImage)
        
        cv2.waitKey(1)
    if message:
        if message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(("Error received from element %s: %s" % (
                message.src.get_name(), err)))
            print(("Debugging information: %s" % debug))
            break
        elif message.type == Gst.MessageType.EOS:
            print("End-Of-Stream reached.")
            break
        elif message.type == Gst.MessageType.STATE_CHANGED:
            if isinstance(message.src, Gst.Pipeline):
                old_state, new_state, pending_state = message.parse_state_changed()
                print(("Pipeline state changed from %s to %s." %
                       (old_state.value_nick, new_state.value_nick)))
        else:
            print("Unexpected message received.")

    

