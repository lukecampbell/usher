#!/usr/bin/env python

from test.testcase import UsherTestCase, attr
from usher.server import UsherServer
import gevent

@attr('unit')
class TestServer(UsherTestCase):
    def setUp(self):
        self.server = UsherServer()


    def test_basic_leasing(self):
        lease = self.server.acquire_lease('/ex1', 5)
        self.assertEquals(lease, 5)

        lease = self.server.acquire_lease('/ex1', 5)
        self.assertEquals(lease, -1)

        self.assertTrue(self.server.is_leased('/ex1'))
        self.assertFalse(self.server.is_leased('/ex2'))

        self.server.free_lease('/ex1')
        self.assertEquals(self.server.acquire_lease('/ex1', 5), 5)

    def test_expiration(self):
        self.server.LEASE_EXT = 0 # Exact expiration

        lease = self.server.acquire_lease('/ex1', 1)
        self.assertEquals(lease, 1)
        self.assertEquals(self.server.acquire_lease('/ex1', 10), -1)
        gevent.sleep(1)

        lease = self.server.acquire_lease('/ex1', 1)
        self.assertEquals(lease, 1)

        



