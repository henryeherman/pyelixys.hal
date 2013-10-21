#!/usr/bin/python
import sys
import signal
sys.path.append("../")
sys.path.append("./")
import pktdata
from websocket import create_connection, ABNF
import time
import status



stat = status.Status()

ws = create_connection("ws://localhost:8888/ws")

def exit_gracefully(signum, frame):
    print "Exit Gracefully, Ctrl+C pressed"            
    ws.close()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_gracefully)


print "Sending packet"
for i in range(10):
    #print pktdata.test_data
    pkt = stat.struct.pack(*pktdata.test_data)
    ws.send(pkt, ABNF.OPCODE_BINARY)
    print "Sent %d" % i
    print "Receiving..."
    #result = ws.recv()
    #print "Received '%s'" % result
    time.sleep(0.05)
ws.close()
