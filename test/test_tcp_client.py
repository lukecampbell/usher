from test.test_tcp_server import ServerTestCase, attr
from usher.tcp_client import UsherTCPClient, UsherLock
import gevent
import time

@attr('unit')
class TestTCPClient(ServerTestCase):

    def test_simple_locking(self):
        cli = UsherTCPClient(self.host, self.port)
        lock = UsherLock(cli,'/ex1', timeout=2)
        with lock:
            lease, key = cli.acquire_lease('/ex1', 40)
            self.assertEquals(lease, 0)
            self.assertIsNone(key)

    def test_lock_timeout(self):
        cli = UsherTCPClient(self.host, self.port)
        lock = UsherLock(cli,'/ex1', timeout=2)
        with self.assertRaises(gevent.timeout.Timeout):
            with lock:
                gevent.sleep(3)

    def test_lock_blocking(self):
        cli = UsherTCPClient(self.host, self.port)
        lock = UsherLock(cli,'/ex1', timeout=10)
        lock.acquire()

        lock2 = UsherLock(cli, '/ex1', acquisition_timeout=1)
        with self.assertRaises(gevent.timeout.Timeout):
            lock2.acquire()

        lock.release()

    def test_lock_expiration(self):
        cli = UsherTCPClient(self.host, self.port)
        lock = UsherLock(cli,'/ex1', timeout=2)
        lock.acquire()
        then = time.time()

        lock2 = UsherLock(cli, '/ex1')
        success = False
        with lock2:
            success=True
        self.assertTrue(success)
        self.assertTrue(time.time() > (then+2)) # Make sure it properly expired

    def test_no_lock(self):
        cli = UsherTCPClient(self.host, self.port)
        lock = UsherLock(cli,'/ex1', timeout=2)
        lock.acquire()

        lock2 = UsherLock(cli, '/ex1', blocking=False)

        with self.assertRaises(RuntimeError):
            with lock2:
                self.assertTrue(False)
        lock2 = UsherLock(cli, '/ex1', acquisition_timeout=1)
        with self.assertRaises(gevent.timeout.Timeout):
            with lock2:
                self.assertTrue(False)










