from test.testcase import UsherTestCase, attr
from usher.tcp_server import UsherTCPServer
from usher.tcp_client import UsherTCPClient
from usher.log import ERROR, enable_console_logging, log

import gevent

import gevent.queue
import gevent.pool
import multiprocessing as mp
import sys

q = mp.Queue()
def mp_get_lock(host, port):
    cli = UsherTCPClient(host, port)
    retval, key = cli.acquire_lease('/mp', 5)
    q.put(retval)
    sys.exit(0)


def mp_server(host, port):
    enable_console_logging(ERROR)
    server = UsherTCPServer((host, port))
    server.server.LEASE_EXT = 0
    log.info('Serving on %s:%s', host, port)
    server.serve_forever()


class ServerTestCase(UsherTestCase):
    def setUp(self):
        self.host = '127.0.0.1'
        self.port = 30128

        self.server = mp.Process(target=mp_server, args=(self.host, self.port))
        self.server.start()
        gevent.sleep(0.5)
    
    def tearDown(self):
        self.server.terminate()


@attr('unit')
class TestTCPServer(ServerTestCase):
    def test_basic_client(self):
        cli = UsherTCPClient(self.host, self.port)
        lease, key = cli.acquire_lease('/ex1', 30)
        self.assertEquals(lease, 30)
        error, key = cli.acquire_lease('/ex1', 90)
        self.assertEquals(error, 0)
        self.assertIsNone(key)
        lease, key = cli.acquire_lease('/ex2', 2)
        self.assertEquals(lease, 2)
        error, key = cli.acquire_lease('/ex2', 1)
        self.assertEquals(error, 0)
        gevent.sleep(2)
        lease, key = cli.acquire_lease('/ex2', 30)
        self.assertEquals(lease, 30)

    def test_concurrent_access(self):
        answer_bin = gevent.queue.Queue()
        def get_lock():
            cli = UsherTCPClient(self.host, self.port)
            retval, key = cli.acquire_lease('/concurrent', 5)
            answer_bin.put(retval)

        gpool = gevent.pool.Group()
        for i in xrange(10):
            gpool.spawn(get_lock)

        gpool.join(timeout=10)
        total = sum([answer_bin.get() for i in xrange(10)])
        self.assertEquals(total, 5)

    def test_multiprocess_access(self):
        global q
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

