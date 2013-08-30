#!/usr/bin/env python

from test.testcase import UsherTestCase, attr
from usher.server import UsherServer
import gevent

@attr('unit')
class TestServer(UsherTestCase):
    def setUp(self):
        self.server = UsherServer()


    def test_basic_leasing(self):
        lease, key = self.server.acquire_lease('/ex1', 5)
        self.assertEquals(lease, 5)
        self.assertIsNotNone(key)

        lease, key_err = self.server.acquire_lease('/ex1', 5)
        self.assertEquals(lease, 0)
        self.assertIsNone(key_err)

        self.assertTrue(self.server.is_leased('/ex1'))
        self.assertFalse(self.server.is_leased('/ex2'))

        self.server.free_lease('/ex1', key)
        lease, key = self.server.acquire_lease('/ex1', 5)
        self.assertEquals(lease, 5)

    def test_expiration(self):
        self.server.LEASE_EXT = 0 # Exact expiration

        lease, key = self.server.acquire_lease('/ex1', 1)
        self.assertEquals(lease, 1)
        lease, key = self.server.acquire_lease('/ex1', 10)
        self.assertEquals(lease, 0)
        self.assertIsNone(key)
        gevent.sleep(1)

        lease, key = self.server.acquire_lease('/ex1', 1)
        self.assertEquals(lease, 1)

        



