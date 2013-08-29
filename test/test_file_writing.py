from test.testcase import attr
from usher.tcp_client import UsherTCPClient, UsherLock
from test.test_tcp_server import ServerTestCase

import multiprocessing as mp
import sys
import tempfile
import os


@attr('unit')
class TestFileWriting(ServerTestCase):

    @staticmethod
    def increment_file(path):
        with open(path, 'r+') as f:
            buf = f.readline()
            f.seek(0)
            if not buf:
                f.write('1\n')
                return 1
            else:
                buf = buf.strip('\n')
                v = int(buf)
                if v > 9:
                    return v
                f.write('%s\n' % (v+1))
        return v+1

    @staticmethod
    def mp_file_write(path, host, port):
        usher = UsherTCPClient(host, port)
        lock = UsherLock(usher, '/flock')
        done = False
        while not done:
            with lock:
                v = TestFileWriting.increment_file(path)
                if v > 9:
                    done = True
        sys.exit(0)

    def test_increment(self):
        fd, temp_path = tempfile.mkstemp()
        self.addCleanup(os.remove, temp_path)
        os.close(fd)
        for i in xrange(10):
            TestFileWriting.increment_file(temp_path)
        with open(temp_path, 'r') as f:
            buf = f.read()
        self.assertEquals(buf, '10\n')


    def test_concurrent_write(self):
        fd, temp_path = tempfile.mkstemp()
        self.addCleanup(os.remove, temp_path)
        os.close(fd)

        pool = [mp.Process(target=TestFileWriting.mp_file_write,
            args=(temp_path, self.host, self.port)) for i in xrange(5)]

        map(lambda x : x.start(), pool)
        map(lambda x : x.join(), pool)

        with open(temp_path, 'r') as f:
            buf = f.read()
        self.assertEquals(buf, '10\n')


