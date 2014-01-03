import sys
import time
import signal
import thread
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
        """ Upon receiving a message we place these 
        objects onto the status queue for consumption by
        the rest of the system """
        self.count += 1
        self.status_queue.put(message)

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
                #log.debug("CMD:%s" % repr(cmd))
                log.debug("Wrote %d bytes" % len(str(cmd)))
                self.write_message(str(cmd))
                #self.write_message("CMD:%s" % repr(cmd))
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
    
    stop_event = Event()

    def __init__(self, cmd_queue, status_queue):
        """ Initialize the process and queues """
        super(WSServerProcess, self).__init__()
        self.daemon = True
        self.cmd_queue = cmd_queue
        self.status_queue = status_queue
        # Create a status object that parses the status packets
        # on the queue
        
    def run(self):
        """ Setup the tornado websocket server
        setup a periodic callback to see if the
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
        tornado.ioloop.PeriodicCallback(self.periodic_exit, 50).start()
        
        try:
            log.debug("Tornado server IOLoop starting")
            tornado.ioloop.IOLoop.instance().start() 
        except (KeyboardInterrupt, SystemExit):
            tornado.ioloop.IOLoop.instance().stop()
        

    @staticmethod
    def periodic_exit():
        """ Callback to stop the tornado
        web server
        """
        #log.debug("Checking Exit")
        if WSServerProcess.stop_event.is_set():
            log.debug("Stopping Tornado server")
            tornado.ioloop.IOLoop.instance().stop()

    def run_cmd(self, cmd):        
        self.cmd_queue.put(cmd)
        
    def stop(self):
        WSServerProcess.stop_event.set()

command_queue = Queue()
status_queue = Queue()
wscomproc = WSServerProcess(command_queue, status_queue)
status = Status()
status.update_from_queue(status_queue)        

def start_server():
    """ Helper function to start the server """
    log.debug("Starting wsserver process")
    wscomproc.start()


def stop_server():
    """ Helper function to stop the server """
    log.debug("Stopping wsserver")
    wscomproc.terminate()

def exit_gracefully(signum, frame):
    """ Callback for when we want to shut down the process
    and server threads
    """
    print "Exit Gracefully, Ctrl+C pressed"
    log.debug("Ask the status update thread to quit")
    status.stop_update()
    log.debug("Set the stop event in main thread")
    exit_event.set()
    wscomproc.stop()
    log.debug("Ask the wscommproc to terminate")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)    
    

    def send_test_cmds():
        for i in range(2):
            time.sleep(0.5)
            wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][0](100.0))            
            wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][1](5.0))
            wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][2](100.0))
            time.sleep(0.5)
            wscomproc.run_cmd(cmd_lookup['Valves']['set_state0'](0xAA))
            time.sleep(0.5)
            wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][0](20.0))
            wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][1](20.0))
            wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][2](20.0))
            time.sleep(0.5)
            wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][0](5.0))        
            wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][1](100.0))
            wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][2](5.0))
		
        wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][0](0.0))        
        wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][1](0.0))
        wscomproc.run_cmd(cmd_lookup['Mixers']['set_duty_cycle'][2](0.0))
		
        for j in range(3):
            for i in range(16):
                time.sleep(0.1)
                wscomproc.run_cmd(cmd_lookup['Valves']['set_state0'](1<<i))
            for i in range(16):
                time.sleep(0.1)
                wscomproc.run_cmd(cmd_lookup['Valves']['set_state1'](1<<i))
            for i in range(16):
                time.sleep(0.1)
                wscomproc.run_cmd(cmd_lookup['Valves']['set_state2'](1<<i))			
        wscomproc.run_cmd(cmd_lookup['Valves']['set_state0'](0))
        wscomproc.run_cmd(cmd_lookup['Valves']['set_state1'](0))					
        wscomproc.run_cmd(cmd_lookup['Valves']['set_state2'](0))			
		
        for i in range(3):
            time.sleep(0.5)
            wscomproc.run_cmd(cmd_lookup['Fans']['turn_on'][i]())
            time.sleep(0.5)
            wscomproc.run_cmd(cmd_lookup['Fans']['turn_off'][i]())
		    
    #thread.start_new_thread(send_test_cmds, ())    
    
    log.debug("Starting loop to check status")
    start_server()
    
    #while(not exit_event.is_set()):
    #    if status.is_valid:
    #        print "Thermocouple 0 err_code= %x" % ord(status['Thermocouples'][0]['error_code'])
    #    time.sleep(1.0)
    #log.debug("Attempt to join wscomproc")
    #wscomproc.join()
    