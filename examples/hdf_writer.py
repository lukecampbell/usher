'''
This simple example will act as a worker and increment an attribute in an HDF5 file
'''
from usher.tcp_client import UsherTCPClient, UsherLock
import sys
import h5py
import os


pid = os.getpid()

def increment_file(path):
    with h5py.File(path, 'a') as f:
        try:
            v = f.attrs['attribute']
        except KeyError:
            f.attrs['attribute'] = '1'
            return 1
        v = int(v)
        if v < 4095:
            f.attrs['attribute'] = '%s' % (v+1) # Increment it
            f.attrs['%s' % pid] = 1 # Just to show that all the processes get a turn

        return v+1

def main(host, port, path):
    cli = UsherTCPClient(host, port)
    lock = UsherLock(cli, '/hdf-example', acquisition_timeout=60)

    while True:
        with lock:
            v = increment_file(path)
            if v > 4095:
                sys.exit(0)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='server ip-address')
    parser.add_argument('port', type=int, help='server port')
    parser.add_argument('path', help='path to h5 file')
    args = parser.parse_args()

    main(args.host, args.port, args.path)

