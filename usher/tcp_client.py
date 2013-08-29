#!/usr/bin/env python
from usher.tcp_server import MessageParser

from struct import pack, unpack
import socket

import gevent.event
import gevent

class UsherSocket(socket.socket):
    '''
    A socket wrapper that can be used in a context-manager
    '''
    def __init__(self, host, port):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host,port))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class UsherTCPClient:
    '''
    The usher TCP Client
    '''
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def acquire_lease(self, namespace, expiration=60):
        '''
        Acquire a lease
        returns the expiration time or 0 on failure
        '''
        message = pack('<BBH', MessageParser.ACQUIRE_MESSAGE, expiration, len(namespace))
        message += namespace
        with UsherSocket(self.host, self.port) as s:
            s.send(message)
            retval = s.recv(1)
            retval = unpack('<B', retval)[0]
        return retval

    def release_lease(self, namespace):
        '''
        Release a lease
        returns 0 on success
        '''
        message = pack('<BH', MessageParser.RELEASE_MESSAGE, len(namespace))
        message += namespace
        with UsherSocket(self.host, self.port) as s:
            s.send(message)
            retval = s.recv(1)
            retval = unpack('<B', retval)[0]
        return retval

class UsherLock:
    '''
    A distributed lock

    Usage:
    usher = UsherTCPClient('localhost', 9090)
    lock = UsherLock(usher)

    with lock:
        do_something()
    '''

    def __init__(self, cli, name):
        self.cli = cli
        self.name = name

    def acquire(self, blocking=True, timeout=10):
        '''
        Acquire the lock
        blocking - Whether or not the call should block
        timeout  - time in seconds it should wait before timing out
        returns True on sucess and False on Failre
        raises Timeout 
        '''
        expiration = self.cli.acquire_lease(self.name, 60)
        if expiration != 0:
            return True
        if blocking:
            done = gevent.event.Event()
            with gevent.timeout.Timeout(timeout):
                while not done.wait(1):
                    expiration = self.cli.acquire_lease(self.name, 60)
                    if expiration != 0:
                        done.set()
                return True
        return False

    def release(self):
        r = self.cli.release_lease(self.name)
        if r == 0:
            raise RuntimeError("Couldn't release the lock")


    def __enter__(self):
        self.acquire(blocking=True, timeout=10)
        return self

    def __exit__(self, type, value, traceback):
        self.release()




       

