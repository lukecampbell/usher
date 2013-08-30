import logging
log = logging.getLogger('usher')

from logging import DEBUG,INFO,WARNING,ERROR,CRITICAL,NOTSET
def clear_console_logging():
    log.handlers = filter(lambda x : not isinstance(x, logging.StreamHandler), log.handlers)

def enable_console_logging(level):
    clear_console_logging()
    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.setLevel(level)


