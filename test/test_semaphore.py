#!/usr/bin/env python

from test.testcase import UsherTestCase, attr
from usher.server import NamespaceSemaphore
import gevent

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

        

