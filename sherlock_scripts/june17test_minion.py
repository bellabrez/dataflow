import time
import sys
import os
import fcntl

class Printlog():
    def __init__(self, logfile):
        self.logfile = logfile
    def print_to_log(self, message):
        with open(self.logfile, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(message)
            fcntl.flock(f, fcntl.LOCK_UN)

def main(args):
    printlog_object = Printlog(logfile='tada.txt')
    printlog = getattr(printlog_object, 'print_to_log')

    for i in range(10):
        printlog('minion says {} {}\n'.format(args[0], i))
        time.sleep(1)

if __name__ == '__main__':
    main(sys.argv[1:])
