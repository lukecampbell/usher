#!/usr/bin/env python
from usher.tcp_server import MessageParser

from struct import pack, unpack
import socket

class UsherSocket(socket.socket):
    def __init__(self, host, port):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host,port))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class UsherTCPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def acquire_lease(self, namespace, expiration=60):
        message = pack('<BBH', MessageParser.ACQUIRE_MESSAGE, expiration, len(namespace))
        message += namespace
        with UsherSocket(self.host, self.port) as s:
            s.send(message)
            retval = s.recv(1)
            retval = unpack('<B', retval)[0]
        return retval

    def release_lease(self, namespace):
        message = pack('<BH', MessageParser.RELEASE_MESSAGE, len(namespace))
        message += namespace
        with UsherSocket(self.host, self.port) as s:
            s.send(message)
            retval = s.recv(1)
            retval = unpack('<B', retval)[0]
        return retval





       

