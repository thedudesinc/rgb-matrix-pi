#!/usr/bin/env python3
"""
Simple test for stdin_listener to diagnose input issues
"""

import sys
import time
import logging
from stdin_listener import StdinListener

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(name)s %(levelname)s: %(message)s')
log = logging.getLogger('test')

def main():
    log.info('Testing stdin listener...')
    log.info('stdin.isatty(): %s', sys.stdin.isatty())
    log.info('stdin fileno: %s', sys.stdin.fileno())
    
    listener = StdinListener()
    listener.start()
    
    log.info('Listener started. Press arrow keys (Ctrl+C to exit)')
    log.info('Waiting for events...')
    
    try:
        count = 0
        while True:
            evt = listener.get_event(timeout=0.5)
            if evt:
                key, is_down, ts = evt
                count += 1
                log.info('==> EVENT #%d: key=%s is_down=%s ts=%.3f', count, key, is_down, ts)
            else:
                log.debug('No event (timeout)')
    except KeyboardInterrupt:
        log.info('\nCtrl+C received, exiting')
    finally:
        listener.stop()
        log.info('Test complete. Total events: %d', count)

if __name__ == '__main__':
    main()
