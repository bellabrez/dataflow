import time
import sys

for i in range(10):
    print('minion says {}'.format(i))
    sys.stdout.flush()
    time.sleep(1)
