#!/usr/bin/env python

from usher.dotdict import DotDict

import gevent
import gevent.coros
import time
import uuid


class NamespaceSemaphore:
    '''
    A utility to manage timed semaphores with namespaces
    '''
    def __init__(self):
        self.table = {}
        self.lock = gevent.coros.RLock()


    def acquire(self, namespace, expiration, timeout):
        '''
        Attempts to acquire a lock/semaphore with the given namespace
        the attempt will wait <timeout> seconds.
        namespace  - The namespace of the semaphore
        expiration - how long before the semaphore should automatically be 
                     released
        timeout    - How many seconds the acquisition should block for attempting
        returns uuid key of acquisition OR None if acquisition failed
        '''


        with self.lock:
            if namespace in self.table:
                semaphore = self.table[namespace]
            else:
                semaphore = self.table[namespace] = gevent.coros.Semaphore()
                semaphore.acquire()
                semaphore.name = namespace
                semaphore.key = uuid.uuid4().bytes
                semaphore.rawlink(self.free)
                gevent.spawn(self.timed_release, namespace, expiration)
                return semaphore.key
        if semaphore.acquire(timeout=timeout):
            gevent.spawn(self.timed_release, namespace, expiration)
            return semaphore.key
        return None

    def is_acquired(self, namespace):
        '''
        Determines if a semaphore exists and is acquired
        '''
        with self.lock:
            if namespace in self.table:
                return True
        return False
            

    def timed_release(self, namespace, expiration):
        '''
        The greenlet execution that waits <expiration> seconds before releasing
        the semaphore.  
        '''

        gevent.sleep(expiration)
        self.release(namespace)

    def free(self, semaphore):
        '''
        Frees the table entry
        '''

        namespace = semaphore.name
        with self.lock:
            if namespace in self.table:
                del self.table[namespace]

    def release(self, namespace, key=None):
        '''
        Releases the semaphore
        Returns False only if a provided key doesn't match
        '''
        with self.lock:
            if namespace in self.table:
                semaphore = self.table[namespace]
                if key is not None:
                    if key == semaphore.key:
                        semaphore.release()
                        return True
                    else:
                        return False
                semaphore.release()
                return True
        return True 


class UsherServer:
    LEASE_EXT = 60 # A constant buffer size in seconds

    def __init__(self, config=None):
        if config is None:
            self.config = DotDict()
        else:
            self.config = DotDict(config)
        self.ns = NamespaceSemaphore()
    
    def acquire_lease(self, namespace, expiration=60, timeout=0):
        '''
        Acquires a lease on a namespace
        returns the allowed expiration and a unique key to use when releasing the lock
        '''
        expiration = min(expiration, 60)
        timeout = min(timeout, 120) # At most tie up for 120 seconds
        key = self.ns.acquire(namespace, expiration + self.LEASE_EXT, timeout)
        if key is None:
            print 'empty'
            return 0, None
        else:
            return expiration, key
    
    def is_leased(self, namespace):
        '''
        Compares the timestamp in the lease table with the current system time
        If the current system time is greater than the lease expiration then the 
        function returns true
        '''
        return self.ns.is_acquired(namespace)


    def free_lease(self, namespace, key):
        '''
        Removes a lease from the lease table
        '''
        return self.ns.release(namespace, key)
            









        



