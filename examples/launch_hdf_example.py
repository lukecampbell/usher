'''
This launches a server and 10 workers
'''
from subprocess import Popen

def main(host, port, path):

    procs = [Popen(['python', 'examples/hdf_writer.py', host, '%s' % port, path]) for i in xrange(10)]

    for p in procs:
        p.wait()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='server ip-address')
    parser.add_argument('port', type=int, help='server port')
    parser.add_argument('path', help='path to h5 file')
    args = parser.parse_args()

    main(args.host, args.port, args.path)


