import time
import sys
import os

def main(args):

    #sys.stdout = open('hellotoyou.txt', 'a+', os.O_NONBLOCK)
    f = open('hellotoyou.txt', 'a+', os.O_NONBLOCK)

    for i in range(10):
        f.write('minion says {} {}'.format(args[0], i))
        f.flush()
        #print('minion says {} {}'.format(args[0], i))
        #sys.stdout.flush()
        time.sleep(1)

if __name__ == '__main__':
    main(sys.argv[1:])
