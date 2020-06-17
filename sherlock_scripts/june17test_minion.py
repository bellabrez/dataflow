import time
import sys

def main(args):

    sys.stdout = open('hellotoyou.txt', 'a+')

    for i in range(10):
        print('minion says {} {}'.format(args[0], i))
        sys.stdout.flush()
        time.sleep(1)

if __name__ == '__main__':
    main(sys.argv[1:])
