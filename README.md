# Usher

A simple TCP-based distributed locking solution

Author: Luke Campbell &lt; lcampbell at-thingy asascience dot-ish commercial domain &gt;

## Installation

1. Get `libevent`
   
   On Mac: `brew install libevent` 

   On Ubuntu: `sudo apt-get install libevent-dev`

2. Install

   ```
   python setup.py install
   ```

## Running the server

Run the server with the `usher-server` command. 
```
usher-server -l DEBUG -p 9090
```

```
usage: usher-server [-h] [-l LOG_LEVEL] [-i INTERFACE] [-p PORT]

optional arguments:
  -h, --help            show this help message and exit
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        set the log level
  -i INTERFACE, --interface INTERFACE
                        the ip-address or host of the interface to listen on
  -p PORT, --port PORT  port to listen on
```

## Using the locks!

Install usher on any python environment where you wish to use the locks. 

In a python application:
```python
from usher.tcp_client import UsherTCPClient, UsherLock
host = 'localhost'
port = 9090

client = UsherTCPClient(host, port)
lock = UsherLock(client, '/lock-example', timeout=10)

with lock:
    # Do whatever you need to, safely
    do_something()

# The lock is automatically freed at the end
```
