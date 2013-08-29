from test.testcase import UsherTestCase, attr
from usher.tcp_server import UsherTCPServer
from usher.tcp_client import UsherTCPClient
from usher.log import INFO, enable_console_logging
from subprocess import Popen

import gevent

import gevent.queue
import gevent.pool
import multiprocessing as mp
import sys

q = mp.Queue()
def mp_get_lock(host, port):
    cli = UsherTCPClient(host, port)
    retval = cli.acquire_lease('/mp', 5)
    q.put(retval)
    sys.exit(0)


def mp_server(host, port):
    server = UsherTCPServer((host, port))
    server.serve_forever()


@attr('unit')
class TestTCPServer(UsherTestCase):
    def setUp(self):
        enable_console_logging(INFO)
        

        self.host = '127.0.0.1'
        self.port = 30128

        self.server = UsherTCPServer((self.host,self.port))
        self.server.server.LEASE_EXT = 0
        self.server.start()
    
    def tearDown(self):
        self.server.stop()

    def test_basic_client(self):
        cli = UsherTCPClient(self.host, self.port)
        lease = cli.acquire_lease('/ex1', 30)
        self.assertEquals(lease, 30)
        error = cli.acquire_lease('/ex1', 90)
        self.assertEquals(error, 0)
        lease = cli.acquire_lease('/ex2', 2)
        self.assertEquals(lease, 2)
        error = cli.acquire_lease('/ex2', 1)
        self.assertEquals(error, 0)
        gevent.sleep(2)
        lease = cli.acquire_lease('/ex2', 30)
        self.assertEquals(lease, 30)

    def test_concurrent_access(self):
        answer_bin = gevent.queue.Queue()
        def get_lock():
            cli = UsherTCPClient(self.host, self.port)
            retval = cli.acquire_lease('/concurrent', 5)
            answer_bin.put(retval)

        gpool = gevent.pool.Group()
        for i in xrange(10):
            gpool.spawn(get_lock)

        gpool.join(timeout=10)
        total = sum([answer_bin.get() for i in xrange(10)])
        self.assertEquals(total, 5)

    def test_multiprocess_access(self):
        global q
        self.server.stop()
        self.port += 1 # Deal with the TCP_WAIT thing
        server = mp.Process(target=mp_server, args=(self.host, self.port))
        server.start()
        pool = [mp.Process(target=mp_get_lock, args=(self.host, self.port)) for i in xrange(5)]
        for p in pool:
            p.start()

        for p in pool:
            p.join()

        total=0
        for i in xrange(5):
            r = q.get()
            total += r
        self.assertEquals(total, 5)

        gevent.sleep(5)
        pool = [mp.Process(target=mp_get_lock, args=(self.host, self.port)) for i in xrange(5)]
        for p in pool:
            p.start()

        for p in pool:
            p.join()

        total=0
        for i in xrange(5):
            r = q.get()
            total += r

        server.terminate()


