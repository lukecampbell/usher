#!/usr/bin/env python

from test.testcase import UsherTestCase, attr
from usher.server import NamespaceSemaphore
import gevent
import gevent.queue
import gevent.pool

@attr('unit')
class TestSemaphore(UsherTestCase):
    def test_serial_semaphore(self):
        ns = NamespaceSemaphore()

        key = ns.acquire('/ex1', 2, 0)
        self.assertIsNotNone(key)
        self.assertIsNone(ns.acquire('/ex1', 1, 0))
        key = ns.acquire('/ex1', 2, 3)
        self.assertIsNotNone(key)
        gevent.sleep(2.2)

        self.assertTrue( '/ex1' not in ns.table )

    def test_releasing(self):
        ns = NamespaceSemaphore()
        key = ns.acquire('/ex1', 2, 0)
        self.assertIsNotNone(key)

        self.assertFalse(ns.release('/ex1', 'not a key'))
        self.assertIsNone(ns.acquire('/ex1', 1, 0))
        
        key2 = ns.acquire('/ex1', 2, 3)
        self.assertEquals(key, key2)
        ns.release('/ex1', key2)

        key = ns.acquire('/ex1', 2, 0)
        self.assertIsNotNone(key)
        self.assertIsNone(ns.acquire('/ex1', 1, 0))
        gevent.sleep(2.2)
        self.assertIsNotNone(ns.acquire('/ex1', 1, 0))

    def acquire(self, ns):
        key = ns.acquire('/ex', 5, 5)
        if key is not None:
            self.q.put(True)

    def test_contest(self):
        ns = NamespaceSemaphore()
        ns.acquire('/ex', 3, 0)
        self.q = gevent.queue.Queue()
        pool = gevent.pool.Pool(size=5)
        for i in xrange(5):
            pool.spawn(self.acquire, ns)

        pool.join()
        self.assertEquals(self.q.qsize(), 1)
        self.q.get()
        for i in xrange(5):
            pool.spawn(self.acquire, ns)
        pool.join()
        self.assertEquals(self.q.qsize(), 1)



