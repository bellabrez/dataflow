import time
import sys
import os
import dataflow as flow

def main(args):
    printlog = getattr(flow.Printlog(logfile='tada.txt'), 'print_to_log')

    for i in range(10):
        printlog('minion says {} {}'.format(args[0], i))
        time.sleep(1)
        dfgkjh

if __name__ == '__main__':
    main(sys.argv[1:])
