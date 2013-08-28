#!/usr/bin/env python

import gevent
import gevent.coros
import time

class UsherServer:
    LEASE_EXT = 60 # A constant buffer size in seconds

    def __init__(self):
        self.table = {}
        self.gevent_lock = gevent.coros.RLock()
    
    def acquire_lease(self, namespace, expiration=60):
        '''
        Acquires a lease on a namespace
        '''
        with self.gevent_lock: # Assuming it acquires, need to check
            if namespace in self.table and not self.is_expired(namespace):
                return 0
            else:
                self.lease(namespace, expiration)
                return expiration
    
    def is_expired(self, namespace):
        '''
        Compares the timestamp in the lease table with the current system time
        If the current system time is greater than the lease expiration then the 
        function returns true
        '''
        lease_value = self.table[namespace]
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
        expiration = current_time + expiration

        self.table[namespace] = expiration + extension
        return expiration # Clients shouldn't be aware of the extension

    def free_lease(self, namespace):
        '''
        Removes a lease from the lease table
        '''
        with self.gevent_lock:
            if namespace in self.table:
                self.table[namespace] = None
                del self.table[namespace]
                return 1
            else:
                return 2
        return 0
            
    def is_leased(self, namespace):
        '''
        Determines if a namespace is leased
        '''
        with self.gevent_lock:
            if namespace in self.table and not self.is_expired(namespace):
                return True
            return False









        



