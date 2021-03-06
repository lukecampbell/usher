from unittest import TestCase
from nose.plugins.attrib import attr

class UsherTestCase(TestCase):
    def __repr__(self):
        name = self.id()
        name = name.split('.')
        for i,n in enumerate(name):
            if n == self.__class__.__name__:
                break
        mod = '.'.join(name[:i])
        cls = '.'.join(name[i:])
        method = name[-1]
        name = ':'.join([mod,cls])
        return '%s (%s)' %(method,name)
    __str__ = __repr__

    def shortDescription(self):
        return None


