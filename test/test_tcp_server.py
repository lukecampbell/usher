from test.testcase import UsherTestCase, attr
from usher.tcp_server import UsherTCPServer
from usher.tcp_client import UsherTCPClient
import gevent

@attr('unit')
class TestTCPServer(UsherTestCase):
    def setUp(self):
        self.server = UsherTCPServer(('127.0.0.1', 30128))
        self.server.server.LEASE_EXT = 0
        self.server.start()

    def tearDown(self):
        self.server.stop()

    def test_basic_client(self):
        cli = UsherTCPClient('localhost', 30128)
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





