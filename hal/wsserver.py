import sys
import time
import signal
import tornado.httpserver
from multiprocessing import Process, Event, Queue
from Queue import Empty
import tornado.websocket
import tornado.ioloop
import tornado.web
#import json
from status import Status
from cmds import cmd_lookup
sys.path.append('../')
from logs import wsslog as log
import datetime

exit_event = Event()

pkt_send_timeout = 0.1


class WSHandler(tornado.websocket.WebSocketHandler):
    """ This the the main websocket handler that deals with incoming
    connections from the elixys synthesizer hardware client.
    It reads the incoming status packets and make them available
    but putting them onto a queue.  The handler also, periodically
    send the commands from the software to the hardware.
    """

    status = Status()
    handler_instances = []

    def initialize(self, cmd_queue, status_queue):
        """ Setup the cmd and statu queuse
        The cmd_queue is in the outbound queue
        commands to the elixys synthesizer get placed
        on this queue before being sent to the hardware.
        The status_queue is the inbound queue, the
        status of the system is received on this queue and
        used to update the global system status.
        """

        self.cmd_queue = cmd_queue
        self.status_queue = status_queue

    def open(self):
        """ The handler is run when the websocket
        connection from the client is first run.
        Since only one client should connect at a time,
        we track the number of clients and close an clients
        to try to connect later.  In addition we also
        set up a timed callback that will check to see i
        if any commands have been place in the outbound
        cmd_queue, and then sends any that are avalaible
        """

        self.count = 0
        if self in WSHandler.handler_instances:
            WSHandler.handler_instances.remove(self)
        WSHandler.handler_instances.append(self)

        log.debug("New client %d connected to wsserver" %
                  len(WSHandler.handler_instances))
        # Handle case where we have two clients, which is not allowed!
        if len(WSHandler.handler_instances) > 1:
            log.error("Too many clients attempting to connect!")
            self.write_message("Too many connections! Closing yours.")
            WSHandler.handler_instances.pop()
            self.close()
            return
        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(seconds=pkt_send_timeout), self.send_pkt)
        #self.write_message("Hello client")

    def on_message(self, message):
        """ Upon receiving a message we parse the incoming status packet
        binary data and convert it in to a Status dictionary.
        This dictionary now contains the entire state of the system.
        We place these objects onto the status queue for consumption by
        the rest of the system """

        # print 'message received %d' % len(message)
        data = self.status.parse_packet(message)
        #log.debug(json.dumps(data['Header'], sort_keys=True, indent=1))
        #print "Message: %d\r\n" % self.count
        self.count += 1
        self.status_queue.put(data)

    def on_close(self):
        """ This handler deals with when we close a connection
        from a client.  In this case we remove it from the list
        of clients (which should always have a length of 1)
        then log the connection being closed """

        WSHandler.handler_instances.remove(self)
        log.debug('connection closed')

    def send_pkt(self):
        """ This callback is periodically called to send all
        the commands on the cmd_queue out to the hardware.
        First check to see if there is a client connected.
        Then if we have a client see if there are commands on
        the cmd_queue.  If we have commands, pop them off the queue
        and send them, till none are left. Finally, reschedule
        this handler to be run again in the near future """

        if len(WSHandler.handler_instances) == 0:
            return
        #print "Attempt to send pkt"
        #print "ID in WSHandler %d" % id(self.cmd_queue)
        try:
            while True:
                cmd = self.cmd_queue.get(block=False)
                log.debug("CMD:%s" % repr(cmd))
                self.write_message("CMD:%s" % str(cmd))
        except Empty:
            pass
        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(seconds=pkt_send_timeout), self.send_pkt)


class WSServerProcess(Process):
    """ The websocket hardware server runs in its own
    process.  It accepts the cmd and status queues and
    passes them to the tornado websock server.
    This is the object the rest of the system interfaces
    with to communicate directly with the hardware.
    Since it is a process we must use queues for all communication.
    """

    def __init__(self, cmd_queue, status_queue):
        """ Initialize the process and queues """
        super(WSServerProcess, self).__init__()
        self.cmd_queue = cmd_queue
        self.status_queue = status_queue

    def run(self):
        """ Setup the tornado websocket server
        Setup a periodic callback to see if the
        server should exit gracefully
        """
        log.debug("Running server")
        self.application = tornado.web.Application([
            (r'/ws', WSHandler,
             dict(cmd_queue=self.cmd_queue,
             status_queue=self.status_queue)),
        ])
        self.http_server = tornado.httpserver.HTTPServer(self.application)
        self.http_server.listen(8888)
        tornado.ioloop.PeriodicCallback(self.periodic_exit, 100).start()
        try:
            log.debug("Tornado server IOLoop starting")
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            log.debug("Server shutting down, got KeyboardInterrupt")
            tornado.ioloop.IOLoop.instance().stop()

    def terminate(self):
        """ If we are told to exit,
        go ahead and terminate the tornado server
        """
        tornado.ioloop.IOLoop.instance().stop()
        super(WSServerProcess, self).terminate()

    @staticmethod
    def periodic_exit():
        """ Callback to stop the tornado
        web server
        """
        #log.debug("Checking Exit")
        if exit_event.is_set():
            log.debug("Stopping Tornado server")
            tornado.ioloop.IOLoop.instance().stop()

    def run_cmd(self, cmd):
        #print "Adding %s to queue" % cmd
        self.cmd_queue.put(cmd)
        #print id(self.cmd_queue)

command_queue = Queue()
status_queue = Queue()
wscomproc = WSServerProcess(command_queue, status_queue)


def exit_gracefully(signum, frame):
    """ Callback for when we want to shut down the process
    and server threads
    """
    print "Exit Gracefully, Ctrl+C pressed"
    wscomproc.terminate()
    sys.exit(0)


def start_server():
    """ Helper function to start the server """

    log.debug("Starting wsserver process")
    wscomproc.start()


def stop_server():
    """ Helper function to stop the server """
    log.debug("Stopping wsserver")
    wscomproc.terminate()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)

    def check_for_status():
        """ When testing the server, grab the
        incoming status packet and print the packet id """

        while(True):
            time.sleep(.01)
            try:
                statusdict = wscomproc.status_queue.get(block=False)
                print "Status id: %d" % statusdict['Header']['packet_id']
            except Empty:
                pass

    # Run the check_for_status function as a thread so we
    #  can add cmds to the cmd_queue in the main thread
    import thread
    thread.start_new_thread(check_for_status, ())

    start_server()
    for i in range(10):
        time.sleep(2)
        wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][0](100.0))
        wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][1](10.0))
        wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][2](10.0))
        time.sleep(2)
        wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][2](50.0))
        time.sleep(2)
        wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][3](50.0))
        time.sleep(0.5)
