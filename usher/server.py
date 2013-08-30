#!/usr/bin/env python

from usher.dotdict import DotDict

import gevent
import gevent.coros
import time
import uuid


class UsherServer:
    LEASE_EXT = 60 # A constant buffer size in seconds

    def __init__(self, config=None):
        if config is None:
            self.config = DotDict()
        else:
            self.config = DotDict(config)
        self.table = {}
        self.gevent_lock = gevent.coros.RLock()
    
    def acquire_lease(self, namespace, expiration=60):
        '''
        Acquires a lease on a namespace
        returns the allowed expiration and a unique key to use when releasing the lock
        '''
        with self.gevent_lock: # Assuming it acquires, need to check
            if namespace in self.table and not self.is_expired(namespace):
                return 0, None
            else:
                expiration, key = self.lease(namespace, expiration)
                return expiration, key
    
    def is_expired(self, namespace):
        '''
        Compares the timestamp in the lease table with the current system time
        If the current system time is greater than the lease expiration then the 
        function returns true
        '''
        key, lease_value = self.table[namespace]
        current_time = time.time()
        if current_time > lease_value:
            return True
        return False

    def lease(self, namespace, expiration, extension=None):
        '''
        Assigns an expiration timestamp to a namespace in the lease table
        Automatically applies the lease extension
        '''
        if extension is None:
            extension = self.LEASE_EXT

        current_time = time.time()
        t_expiration = current_time + expiration
        key = uuid.uuid4().get_bytes()

        self.table[namespace] = (key, t_expiration + extension)
        return expiration, key # Clients shouldn't be aware of the extension

    def free_lease(self, namespace, key):
        '''
        Removes a lease from the lease table
        returns 0 on failure
        returns 1 on success
        returns 2 if the lock doesn't exist (or expired)
        returns 3 on key-mismatch (permission denied)

        '''
        with self.gevent_lock:
            if namespace in self.table:
                table_key, expiration = self.table[namespace]
                if key == table_key: # If the key matches then we're good
                    self.table[namespace] = None
                    del self.table[namespace]
                    return 1 # Lock released
                else:
                    return 3 # Wrong credentials
            else:
                return 2 # No key
        return 0 # something really bad happened
            
    def is_leased(self, namespace):
        '''
        Determines if a namespace is leased
        '''
        with self.gevent_lock:
            if namespace in self.table and not self.is_expired(namespace):
                return True
            return False









        



