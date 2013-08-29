#!/usr/bin/env python

import gevent.monkey
gevent.monkey.patch_all()

from gevent.server import StreamServer
from usher.server import UsherServer

from struct import pack, unpack


'''
Message Structure

Type : 1 Byte

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
            buf = self.socket.recv(1)
            val = unpack('B', buf)[0]
        if bytes == 2:
            buf = self.socket.recv(2)
            val = unpack('H', buf)[0]
        if bytes == 4:
            buf = self.socket.recv(4)
            val = unpack('I', buf)[0]
        if bytes == 8:
            buf = self.socket.recv(8)
            val = unpack('Q', buf)[0]
        return val
    
    def read_int(self, bytes):
        buf = None
        val = None
        if bytes == 1:
            buf = self.socket.recv(1)
            val = unpack('b', buf)[0]
        if bytes == 2:
            buf = self.socket.recv(2)
            val = unpack('h', buf)[0]
        if bytes == 4:
            buf = self.socket.recv(4)
            val = unpack('i', buf)[0]
        if bytes == 8:
            buf = self.socket.recv(8)
            val = unpack('q', buf)[0]
        return val
    
    def read(self, bytes):
        return self.socket.recv(bytes)

    def parse(self):
        request = self.read_uint(1)
        return request

    def parse_acquire(self):
        expiration = self.read_uint(1)
        strlen = self.read_uint(2)
        namespace = self.read(strlen)

        return (namespace, expiration)

    def parse_release(self):
        strlen = self.read_uint(2)
        namespace = self.read(strlen)

        return namespace



class UsherTCPServer(StreamServer):

    def __init__(self, *args, **kwargs):

        self.server = UsherServer()
        StreamServer.__init__(self, *args, **kwargs)

    def handle(self, socket, addr):
        parser = MessageParser(socket)
        mtype = parser.parse()
        if mtype == MessageParser.NOP_MESSAGE:
            return
        elif mtype == MessageParser.ACQUIRE_MESSAGE:
            namespace, expiration = parser.parse_acquire()
            status = self.server.acquire_lease(namespace, expiration)
            outgoing = pack('<h', status)
            socket.send(outgoing)
            return
        elif mtype == MessageParser.RELEASE_MESSAGE:
            namespace = parser.parse_release()
            status = self.server.free_lease(namespace)
            outgoing = pack('<h', status)
            socket.send(outgoing)
            return


if __name__ == '__main__':
    print 'Listening on 9090'
    UsherTCPServer(('0.0.0.0', 9090)).serve_forever()

