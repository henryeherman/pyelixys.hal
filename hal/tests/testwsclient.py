import sys
import time
import signal
import thread
import websocket
from websocket import ABNF
from pyelixys.hal.status import Status

stat = Status()


def on_message(ws, message):
    """ When test client receives a command print it to console """

    print "FROM SERVER: %s" % repr(message)


def on_error(ws, error):
    """ If we have a communication error print it to console """

    print error


def on_close(ws):
    """ If websocket hardware server closes the connection print to console """
    print "### closed ###"


def on_open(ws):
    """ On opening a new connection to the websocket server take the
    test_data increment the packet_id and send it to the server as
    a status packet.  This is done in a thread so the main thread
    can still receive the incoming command packets and print them to
    the console """

    def run(*args):
        for i in range(50):
            print "Sent packet id: #%d" % i
            pktdata.test_data[1] = i
            pkt = stat.struct.pack(*pktdata.test_data)
            ws.send(pkt, ABNF.OPCODE_BINARY)
            time.sleep(.1)
        ws.close()
        print "thread terminating..."
    thread.start_new_thread(run, ())


def exit_gracefully(signum, frame):
    """ If requested by signal, exit gracefully """
    print "Exit Gracefully, Ctrl+C pressed"
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)  # Setup signal callback
     #websocket.enableTrace(True) # Enable for websocket trace!
    ws = websocket.WebSocketApp("ws://localhost:8888/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
