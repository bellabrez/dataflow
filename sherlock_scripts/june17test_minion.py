import time
import sys

sys.stdout = open('hellotoyou.txt', 'w')

for i in range(10):
    print('minion says {}'.format(i))
    sys.stdout.flush()
    time.sleep(1)
