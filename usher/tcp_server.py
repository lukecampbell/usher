#!/usr/bin/env python

import gevent.monkey
gevent.monkey.patch_all()

from gevent.server import StreamServer
from usher.server import UsherServer
from usher.log import log, DEBUG

from struct import pack, unpack


'''
NOP Message
0x00

Acquire Message

'''


class MessageParser:
    NOP_MESSAGE     = 0x00
    ACQUIRE_MESSAGE = 0x01
    RELEASE_MESSAGE = 0x02

    def __init__(self, socket):
        self.socket = socket

    def read_uint(self, bytes):
        buf = None
        val = None
        if bytes == 1:
            buf = self.read(1)
            val = unpack('B', buf)[0]
        if bytes == 2:
            buf = self.read(2)
            val = unpack('H', buf)[0]
        if bytes == 4:
            buf = self.read(4)
            val = unpack('I', buf)[0]
        if bytes == 8:
            buf = self.read(8)
            val = unpack('Q', buf)[0]
        return val
    
    def read_int(self, bytes):
        buf = None
        val = None
        if bytes == 1:
            buf = self.read(1)
            val = unpack('b', buf)[0]
        if bytes == 2:
            buf = self.read(2)
            val = unpack('h', buf)[0]
        if bytes == 4:
            buf = self.read(4)
            val = unpack('i', buf)[0]
        if bytes == 8:
            buf = self.read(8)
            val = unpack('q', buf)[0]
        return val
    
    def read(self, bytes):
        with gevent.timeout.Timeout(10):
            return self.socket.recv(bytes)
    
    def send(self, message):
        with gevent.timeout.Timeout(10):
            bytes_sent = 0 
            while bytes_sent < len(message):
                bytes_sent += self.socket.send(message[bytes_sent:])
        return bytes_sent


    def parse(self):
        request = self.read_uint(1)
        return request

    def send_acquire(self, namespace, expiration):
        message = pack('<BBH', MessageParser.ACQUIRE_MESSAGE, expiration, len(namespace))
        message += namespace
        return self.send(message)
    
    def read_acquire(self):
        expiration = self.read_uint(1)
        strlen = self.read_uint(2)
        namespace = self.read(strlen)

        return (namespace, expiration)

    def send_acquire_response(self, status, key):
        message = pack('<B', status)
        if status > 0:
            message += key
        return self.send(message)
    
    def read_acquire_response(self):
        status = self.read_uint(1)
        key = None
        if status > 0:
            key = self.read(16)
        return status, key

    def send_release(self, namespace, key):
        message = pack('<BH', MessageParser.RELEASE_MESSAGE, len(namespace))
        message += namespace
        message += key
        return self.send(message)

    def read_release(self):
        strlen = self.read_uint(2)
        namespace = self.read(strlen)
        key = self.read(16)
        return namespace, key

    def send_release_response(self, status):
        message = pack('<B', status)
        return self.send(message)

    def read_release_response(self):
        status = self.read_uint(1)
        return status

    def send_nop(self):
        message = pack('<B', MessageParser.NOP_MESSAGE)
        return self.send(message)

    def read_nop_response(self):
        status = self.read_uint(1)
        return status

class UsherTCPServer(StreamServer):

    def __init__(self, *args, **kwargs):

        self.server = UsherServer()
        StreamServer.__init__(self, *args, **kwargs)

    def handle(self, socket, addr):
        log.info('%s - Accepted', (addr,))
        mp = MessageParser(socket)
        mtype = mp.parse()
        if mtype == MessageParser.NOP_MESSAGE:
            log.debug('%s - NOP', (addr,))
            mp.send_nop()
            return
        elif mtype == MessageParser.ACQUIRE_MESSAGE:
            log.debug('%s - Acquire', (addr,))
            namespace, expiration = mp.read_acquire()
            log.debug('%s - (%s/%s) Requested', addr, namespace, expiration)
            status, key = self.server.acquire_lease(namespace, expiration)
            if log.isEnabledFor(DEBUG):
                if key:
                    h = ''.join([hex(ord(i)).replace('0x','') for i in key])
                else:
                    h = 'None'
                log.debug('%s - status: %s key %s', addr, status, h)
            mp.send_acquire_response(status, key)
            return
        elif mtype == MessageParser.RELEASE_MESSAGE:
            log.debug('%s - Release', (addr,))
            namespace, key = mp.read_release()
            log.debug('%s - (%s) Release', (addr,), namespace)
            status = self.server.free_lease(namespace, key)
            log.debug('%s - status: %s', (addr,), status)
            mp.send_release_response(status)
            return


if __name__ == '__main__':
    print 'Listening on 9090'
    UsherTCPServer(('0.0.0.0', 9090)).serve_forever()

