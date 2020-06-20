import time
import sys
import os
import dataflow as flow

def main(args):
    #logfile = args[0]
    printlog = args[0]
    #printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    for i in range(10):
        printlog('minion says {} {}'.format(args[1], i))
        time.sleep(1)

if __name__ == '__main__':
    main(sys.argv[1:])
