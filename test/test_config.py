from test.testcase import UsherTestCase, attr
from tempfile import TemporaryFile, mkstemp
from usher.config import ConfigLoader
from usher.dotdict import DotDict

import os

@attr('unit')
class TestConfig(UsherTestCase):
    def test_basic_config(self):
        sample_file='''cluster:
  name: example
  port: 8080
  hosts:
    - localhost
    - google.com
    - blah.whatever

  key: abc123'''
        fd, path = mkstemp()
        os.close(fd)
        self.addCleanup(os.remove, path)
        with open(path, 'w+') as f:
            f.write(sample_file)
        config = ConfigLoader.load(path)

        config = DotDict(config)
        self.assertEquals(config.cluster.name, 'example')
        self.assertEquals(config.cluster.port, 8080)
        self.assertEquals(config.cluster.key, 'abc123')



