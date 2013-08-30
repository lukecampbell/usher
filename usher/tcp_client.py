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
    def __init__(self, host, port, timeout=10):
        self.host = host
        self.port = port
        self.timeout = timeout

        # Make sure the server is alive
        self.nop()

    def acquire_lease(self, namespace, expiration=60):
        '''
        Acquire a lease
        returns the expiration time or 0 on failure
        '''
        message = pack('<BBH', MessageParser.ACQUIRE_MESSAGE, expiration, len(namespace))
        message += namespace
        with UsherSocket(self.host, self.port) as s, gevent.timeout.Timeout(self.timeout):
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
        with UsherSocket(self.host, self.port) as s, gevent.timeout.Timeout(self.timeout):
            s.send(message)
            retval = s.recv(1)
            retval = unpack('<B', retval)[0]
        return retval
    
    def nop(self):
        message = pack('<B', MessageParser.NOP_MESSAGE)
        with UsherSocket(self.host, self.port) as s, gevent.timeout.Timeout(self.timeout):
            s.send(message)
            retval = s.recv(1)
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

    def __init__(self, cli, name, blocking=True, timeout=10, acquisition_timeout=10, raise_timeout=True):
        self.cli = cli
        self.name = name
        self.blocking = blocking
        self.timeout = timeout
        self.acquisition_timeout = acquisition_timeout
        self.raise_timeout = raise_timeout
        self.gevent_timeout = gevent.timeout.Timeout(self.timeout)

    def acquire(self, blocking=True, timeout=10, lease_time=60):
        '''
        Acquire the lock
        blocking - Whether or not the call should block
        timeout  - time in seconds it should wait before timing out
        returns True on sucess and False on Failre
        raises Timeout 
        '''
        expiration = self.cli.acquire_lease(self.name, lease_time)
        if expiration != 0:
            return True
        if blocking:
            done = gevent.event.Event()
            with gevent.timeout.Timeout(timeout):
                while not done.wait(1):
                    expiration = self.cli.acquire_lease(self.name, lease_time)
                    if expiration != 0:
                        done.set()
                return True
        return False

    def release(self):
        r = self.cli.release_lease(self.name)
        if r == 0:
            raise RuntimeError("Couldn't release the lock")


    def __enter__(self):
        self.acquire(blocking=self.blocking, timeout=self.acquisition_timeout, lease_time=self.timeout)
        if self.raise_timeout:
            self.gevent_timeout.start()
        return self

    def __exit__(self, type, value, traceback):
        self.release()
        self.gevent_timeout.cancel()




       

