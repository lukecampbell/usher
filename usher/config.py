#!/usr/bin/env python

from itertools import chain
import yaml

class ConfigLoader:

    @classmethod
    def load(cls, path, template={}):

        with open(path, mode='r') as f:
            decoded_dict = yaml.load(f)
            
        retval = dict(chain(template.iteritems(), decoded_dict.iteritems()))
        return retval
        


