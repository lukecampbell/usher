#!/usr/bin/env python

import sys
import dis
from copy import deepcopy

def get_safe(dict_instance, keypath, default=None):
    try:
        obj = dict_instance
        keylist = keypath if type(keypath) is list else keypath.split('.')
        for key in keylist:
            obj = obj[key]
        return obj
    except Exception:
        return default

class DotDict(dict):

    def __dir__(self):
        return self.__dict__.keys() + self.keys()

    def __getattr__(self, key):
        """ Make attempts to lookup by nonexistent attributes also attempt key lookups. """
        if self.has_key(key):
            if isinstance(self[key], dict):
                return DotDict(self[key])
            return self[key]
        frame = sys._getframe(1)
        if '\x00%c' % dis.opmap['STORE_ATTR'] in frame.f_code.co_code:
            self[key] = DotDict()
            return self[key]

        raise AttributeError(key)

    def __setattr__(self,key,value):
        if key in dir(dict):
            raise AttributeError('%s conflicts with builtin.' % key)
        if isinstance(value, dict):
            self[key] = DotDict(value)
        else:
            self[key] = value

    def copy(self):
        return deepcopy(self)

    def get_safe(self, qual_key, default=None):
        value = get_safe(self, qual_key)
        if value is None:
            value = default
        return value

    @classmethod
    def fromkeys(cls, seq, value=None):
        return DotDict(dict.fromkeys(seq, value))

