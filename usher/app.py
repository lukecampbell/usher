#!/usr/bin/python
'''
This is where the application code will live
'''
from usher.tcp_server import UsherTCPServer
from usher.log import enable_console_logging, log, DEBUG,INFO,WARNING,ERROR,CRITICAL

import sys
import argparse
import signal
import gevent
import gevent.event

server = None

def usher_server():
    global server
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log-level", help="set the log level")
    parser.add_argument("-i", "--interface", help="the ip-address or host of the interface to listen on")
    parser.add_argument("-p", "--port", type=int, help="port to listen on")
    args = parser.parse_args()

    host = '127.0.0.1' # Run on localhost by default
    port = 50582

    if args.log_level:
        level = args.log_level
        if level.lower() == 'debug':
            enable_console_logging(DEBUG)
        elif level.lower() == 'info':
            enable_console_logging(INFO)
        elif level.lower() == 'warning':
            enable_console_logging(WARNING)
        elif level.lower() == 'error':
            enable_console_logging(ERROR)
        elif level.lower() == 'critical':
            enable_console_logging(CRITICAL)
    if args.interface:
        ifc = args.interface
        if ifc == 'any':
            host = '0.0.0.0'
        elif ifc == 'all':
            host = '0.0.0.0'
        else:
            host = ifc
    if args.port:
        port = args.port

    gevent.signal(signal.SIGINT, sigint)
    gevent.signal(signal.SIGTERM, sigint)
    log.info("Server Listening on %s:%s", host, port)
    server = UsherTCPServer((host,port))
    server.start()
    while True:
        gevent.sleep(100)

def usher_client():
    pass

def sigint():
    global server
    if server is not None:
        log.info("Shutting down")
        server.stop()
    sys.exit(0)



if __name__ == '__main__':
    usher_server()
